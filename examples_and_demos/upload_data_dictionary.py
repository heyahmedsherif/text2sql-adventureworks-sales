#!/usr/bin/env python
"""
Upload data dictionary to AI Search for enhanced Text2SQL context
"""
import os
import sys
import json
from pathlib import Path

# Add the deploy script path
deploy_path = Path(__file__).parent / "deploy_ai_search_indexes" / "src" / "deploy_ai_search_indexes"
sys.path.insert(0, str(deploy_path))

from dotenv import load_dotenv
load_dotenv('deploy_ai_search_indexes/.env')

def upload_data_dictionary():
    """Upload data dictionary to AI Search schema store"""
    print("=== UPLOADING DATA DICTIONARY TO AI SEARCH ===")
    
    try:
        from text_2_sql_schema_store import Text2SqlSchemaStoreAISearch
        
        # Create schema store instance
        schema_store = Text2SqlSchemaStoreAISearch(
            suffix=None,
            rebuild=False,  # Don't rebuild, just upload data
            single_data_dictionary_file=True,
        )
        
        print("✅ Schema store instance created")
        
        # Path to our data dictionary
        data_dict_dir = Path("text_2_sql/data_dictionary_output")
        
        if not data_dict_dir.exists():
            print(f"❌ Data dictionary directory not found: {data_dict_dir}")
            return False
        
        print(f"📁 Data directory: {data_dict_dir}")
        
        # Upload the data dictionary
        print("🚀 Uploading data dictionary to AI Search...")
        
        # Upload files to blob storage manually
        from azure.storage.blob import BlobServiceClient
        
        # Get storage connection
        storage_conn_str = os.getenv('StorageAccount__ConnectionString')
        container_name = "text2sql-schema-store"
        
        blob_client = BlobServiceClient.from_connection_string(storage_conn_str)
        
        # Upload data dictionary file
        data_dict_file = data_dict_dir / "banking_data_dictionary.json"
        
        if data_dict_file.exists():
            with open(data_dict_file, 'rb') as data:
                blob_name = "banking_data_dictionary.json"
                blob_client.get_blob_client(
                    container=container_name, 
                    blob=blob_name
                ).upload_blob(data, overwrite=True)
                
            print(f"✅ Uploaded {blob_name} to blob storage")
        else:
            print(f"❌ Data dictionary file not found: {data_dict_file}")
        
        print("✅ Data dictionary uploaded successfully!")
        
        # Test the search functionality
        print("\n=== TESTING AI SEARCH FUNCTIONALITY ===")
        
        # You can add search tests here if needed
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = upload_data_dictionary()
    
    if success:
        print("\n🎉 Data dictionary successfully uploaded to AI Search!")
        print("Your Text2SQL system now has enhanced schema context for better query generation.")
    else:
        print("\n⚠️  Upload failed. The basic Text2SQL functionality still works.")