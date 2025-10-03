# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License
import os
import logging
import base64
from datetime import datetime, timezone
from typing import Annotated
import chromadb
from chromadb.config import Settings
from text_2_sql_core.connectors.open_ai import OpenAIConnector
from text_2_sql_core.utils.database import DatabaseEngineSpecificFields


class ChromaSearchConnector:
    """ChromaDB-based vector search connector to replace Azure AI Search"""

    def __init__(self):
        self.open_ai_connector = OpenAIConnector()
        # Initialize ChromaDB client
        chroma_path = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
        self.client = chromadb.PersistentClient(path=chroma_path)

    def _get_or_create_collection(self, collection_name: str):
        """Get or create a ChromaDB collection"""
        try:
            collection = self.client.get_collection(name=collection_name)
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return collection

    async def run_ai_search_query(
        self,
        query,
        vector_fields: list[str],
        retrieval_fields: list[str],
        index_name: str,
        semantic_config: str = None,
        top=5,
        include_scores=False,
        minimum_score: float = None,
    ):
        """Run the AI search query using ChromaDB."""

        collection = self._get_or_create_collection(index_name)

        # Generate query embedding if vector fields are specified
        if len(vector_fields) > 0:
            embeddings = await self.open_ai_connector.run_embedding_request([query])
            query_embedding = embeddings.data[0].embedding

            # Query with embeddings
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top,
                include=['documents', 'metadatas', 'distances']
            )
        else:
            # Full-text search using query
            results = collection.query(
                query_texts=[query],
                n_results=top,
                include=['documents', 'metadatas', 'distances']
            )

        combined_results = []

        # Process results
        if results['metadatas'] and len(results['metadatas'][0]) > 0:
            for i, metadata in enumerate(results['metadatas'][0]):
                # Convert distance to similarity score (1 - distance for cosine)
                score = 1 - results['distances'][0][i] if results['distances'] else 1.0

                # Filter by minimum score if specified
                if minimum_score is not None and score < (minimum_score / 4.0):  # Adjust threshold
                    continue

                result_item = metadata.copy()

                if include_scores:
                    result_item["@search.score"] = score

                combined_results.append(result_item)

        logging.info("Results: %s", combined_results)
        return combined_results

    async def get_column_values(
        self,
        text: Annotated[
            str,
            "The text to run a semantic search against. Relevant entities will be returned.",
        ],
    ):
        """Gets the values of a column in the SQL Database by selecting the most relevant entity based on the search term."""

        index_name = os.environ.get(
            "CHROMA_TEXT2SQL_COLUMN_VALUE_STORE",
            "text2sql-column-value-store"
        )

        values = await self.run_ai_search_query(
            text,
            vector_fields=[],
            retrieval_fields=["FQN", "Column", "Value"],
            index_name=index_name,
            semantic_config=None,
            top=50,
            include_scores=False,
            minimum_score=5,
        )

        return values

    async def get_entity_schemas(
        self,
        text: Annotated[
            str,
            "The text to run a semantic search against. Relevant entities will be returned.",
        ],
        excluded_entities: Annotated[
            list[str],
            "The entities to exclude from the search results.",
        ] = [],
        engine_specific_fields: Annotated[
            list[DatabaseEngineSpecificFields],
            "The fields specific to the engine to be included in the search results.",
        ] = [],
    ) -> str:
        """Gets the schema of a view or table in the SQL Database."""

        logging.info("Search Text: %s", text)

        stringified_engine_specific_fields = list(map(str, engine_specific_fields))

        retrieval_fields = [
            "FQN",
            "Entity",
            "EntityName",
            "Schema",
            "Definition",
            "Columns",
            "EntityRelationships",
            "CompleteEntityRelationshipsGraph",
        ] + stringified_engine_specific_fields

        index_name = os.environ.get(
            "CHROMA_TEXT2SQL_SCHEMA_STORE",
            "text2sql-schema-store"
        )

        schemas = await self.run_ai_search_query(
            text,
            ["DefinitionEmbedding"],
            retrieval_fields,
            index_name,
            None,
            top=3,
            minimum_score=1.5,
        )

        fqn_to_trim = ".".join(stringified_engine_specific_fields)

        if len(excluded_entities) == 0:
            return schemas

        filtered_schemas = []
        for schema in schemas:
            if "FQN" in schema:
                del schema["FQN"]

            if (
                schema.get("CompleteEntityRelationshipsGraph") is not None
                and len(schema["CompleteEntityRelationshipsGraph"]) == 0
            ):
                del schema["CompleteEntityRelationshipsGraph"]
            else:
                if schema.get("CompleteEntityRelationshipsGraph"):
                    schema["CompleteEntityRelationshipsGraph"] = list(
                        map(
                            lambda x: x.replace(fqn_to_trim, ""),
                            schema["CompleteEntityRelationshipsGraph"],
                        )
                    )

            if schema.get("SampleValues") is not None and len(schema.get("SampleValues", [])) == 0:
                del schema["SampleValues"]

            if (
                schema.get("EntityRelationships") is not None
                and len(schema.get("EntityRelationships", [])) == 0
            ):
                del schema["EntityRelationships"]

            if schema.get("Entity", "").lower() not in excluded_entities:
                filtered_schemas.append(schema)
            else:
                logging.info("Excluded entity: %s", schema.get("Entity"))

        logging.info("Filtered Schemas: %s", filtered_schemas)
        return filtered_schemas

    async def add_entry_to_index(
        self, document: dict, vector_fields: dict, index_name: str
    ):
        """Add an entry to the ChromaDB collection."""

        logging.info("Document: %s", document)
        logging.info("Vector Fields: %s", vector_fields)

        for field in vector_fields.keys():
            if field not in document.keys():
                logging.error(f"Field {field} is not in the document.")
                return

        collection = self._get_or_create_collection(index_name)

        fields_to_embed = {field: document[field] for field in vector_fields}
        document["DateLastModified"] = datetime.now(timezone.utc).isoformat()

        try:
            embeddings = await self.open_ai_connector.run_embedding_request(
                list(fields_to_embed.values())
            )

            # Generate document ID
            doc_id = base64.urlsafe_b64encode(
                document["Question"].encode()
            ).decode("utf-8")

            # Prepare metadata (all non-embedding fields)
            metadata = {k: v for k, v in document.items() if k not in vector_fields.values()}

            # Use the first embedding for the document
            embedding = embeddings.data[0].embedding

            # Add to ChromaDB
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[document.get("Question", "")]
            )

            logging.info(f"Successfully added document to {index_name}")

        except Exception as e:
            logging.error("Failed to add item to index.")
            logging.error("Error: %s", e)
