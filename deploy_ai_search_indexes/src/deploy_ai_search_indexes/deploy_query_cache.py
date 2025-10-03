#!/usr/bin/env python
"""
Deploy Query Cache component
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
from text_2_sql_query_cache import Text2SqlQueryCacheAISearch
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("=== DEPLOYING QUERY CACHE ===")
    
    # Create fresh instance
    query_cache = Text2SqlQueryCacheAISearch(
        suffix=None,
        rebuild=True,
        single_query_cache_file=False,
        enable_query_cache_indexer=False,  # Start without indexer
    )
    
    # Deploy step by step with error handling
    steps = [
        ("Storage container", lambda: query_cache._ensure_storage_container_exists()),
        ("Data source", lambda: query_cache.deploy_data_source()),
        ("Synonym map", lambda: query_cache.deploy_synonym_map()),
        ("Index", lambda: query_cache.deploy_index()),
        ("Skillset", lambda: query_cache.deploy_skillset()),
        ("Indexer", lambda: query_cache.deploy_indexer()),
    ]
    
    for step_name, step_func in steps:
        try:
            print(f"Executing: {step_name}")
            step_func()
            print(f"✓ {step_name} completed")
        except Exception as e:
            print(f"✗ {step_name} failed: {e}")
            break
    
    print("=== QUERY CACHE DEPLOY COMPLETED ===")

if __name__ == "__main__":
    main()