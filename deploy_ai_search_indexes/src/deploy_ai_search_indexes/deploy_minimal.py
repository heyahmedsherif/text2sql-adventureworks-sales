#!/usr/bin/env python
"""
Minimal deploy script that works around the mysterious URL bug
"""
import sys
import os

# Add the current directory to the path to ensure proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Clear any potentially problematic environment variables
for key in list(os.environ.keys()):
    if key.startswith('AIService__') and 'your-ai-search-endpoint' in os.environ.get(key, ''):
        print(f"Removing problematic env var: {key}")
        del os.environ[key]

# Force reload of dotenv
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(), override=True)

# Import after environment is clean
from text_2_sql_schema_store import Text2SqlSchemaStoreAISearch
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("=== MINIMAL DEPLOY SCRIPT ===")
    
    # Create fresh instance
    schema_store = Text2SqlSchemaStoreAISearch(
        suffix=None,
        rebuild=True,
        single_data_dictionary_file=False,
    )
    
    # Debug the client before using it
    print(f"Client endpoint: {schema_store._search_indexer_client._endpoint}")
    print(f"Environment endpoint: {schema_store.environment.ai_search_endpoint}")
    
    if '<' in str(schema_store._search_indexer_client._endpoint):
        print("ERROR: Client has placeholder endpoint!")
        return
    
    # Deploy step by step with error handling
    steps = [
        ("Storage container", lambda: schema_store._ensure_storage_container_exists()),
        ("Data source", lambda: schema_store.deploy_data_source()),
        ("Synonym map", lambda: schema_store.deploy_synonym_map()),
        ("Index", lambda: schema_store.deploy_index()),
        ("Skillset", lambda: schema_store.deploy_skillset()),
        ("Indexer", lambda: schema_store.deploy_indexer()),
    ]
    
    for step_name, step_func in steps:
        try:
            print(f"Executing: {step_name}")
            step_func()
            print(f"✓ {step_name} completed")
        except Exception as e:
            print(f"✗ {step_name} failed: {e}")
            break
    
    print("=== DEPLOY COMPLETED ===")

if __name__ == "__main__":
    main()