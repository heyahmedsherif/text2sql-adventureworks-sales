#!/usr/bin/env python
"""
Deploy Column Value Store component
"""
import sys
import os

# Add the current directory to the path to ensure proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Force reload of dotenv
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(), override=True)

# Import after environment is clean
from text_2_sql_column_value_store import Text2SqlColumnValueStoreAISearch
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("=== DEPLOYING COLUMN VALUE STORE ===")
    
    # Create fresh instance
    column_store = Text2SqlColumnValueStoreAISearch(
        suffix=None,
        rebuild=True,
    )
    
    # Deploy step by step with error handling
    steps = [
        ("Storage container", lambda: column_store._ensure_storage_container_exists()),
        ("Data source", lambda: column_store.deploy_data_source()),
        ("Synonym map", lambda: column_store.deploy_synonym_map()),
        ("Index", lambda: column_store.deploy_index()),
        ("Skillset", lambda: column_store.deploy_skillset()),
        ("Indexer", lambda: column_store.deploy_indexer()),
    ]
    
    for step_name, step_func in steps:
        try:
            print(f"Executing: {step_name}")
            step_func()
            print(f"✓ {step_name} completed")
        except Exception as e:
            print(f"✗ {step_name} failed: {e}")
            break
    
    print("=== COLUMN VALUE STORE DEPLOY COMPLETED ===")

if __name__ == "__main__":
    main()