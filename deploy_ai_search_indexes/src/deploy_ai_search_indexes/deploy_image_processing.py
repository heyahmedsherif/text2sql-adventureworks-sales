#!/usr/bin/env python
"""
Deploy Image Processing component
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
from image_processing import ImageProcessingAISearch
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("=== DEPLOYING IMAGE PROCESSING ===")
    
    # Create fresh instance
    image_proc = ImageProcessingAISearch(
        suffix=None,
        rebuild=True,
        enable_page_by_chunking=False,  # Start with basic chunking
    )
    
    # Deploy step by step with error handling
    steps = [
        ("Storage container", lambda: image_proc._ensure_storage_container_exists()),
        ("Data source", lambda: image_proc.deploy_data_source()),
        ("Synonym map", lambda: image_proc.deploy_synonym_map()),
        ("Index", lambda: image_proc.deploy_index()),
        ("Skillset", lambda: image_proc.deploy_skillset()),
        ("Indexer", lambda: image_proc.deploy_indexer()),
    ]
    
    for step_name, step_func in steps:
        try:
            print(f"Executing: {step_name}")
            step_func()
            print(f"✓ {step_name} completed")
        except Exception as e:
            print(f"✗ {step_name} failed: {e}")
            break
    
    print("=== IMAGE PROCESSING DEPLOY COMPLETED ===")

if __name__ == "__main__":
    main()