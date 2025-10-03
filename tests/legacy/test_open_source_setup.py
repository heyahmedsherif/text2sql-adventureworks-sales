#!/usr/bin/env python
"""
Test script to verify open source Text2SQL setup
"""

import sys
import os
from pathlib import Path

# Add paths
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
    except ImportError as e:
        print(f"❌ ChromaDB import failed: {e}")
        return False

    try:
        from openai import AsyncOpenAI
        print("✅ OpenAI client imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

    try:
        from text_2_sql_core.connectors.open_ai import OpenAIConnector
        print("✅ OpenAI connector imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI connector import failed: {e}")
        return False

    try:
        from text_2_sql_core.connectors.chroma_search import ChromaSearchConnector
        print("✅ ChromaDB search connector imported successfully")
    except ImportError as e:
        print(f"❌ ChromaDB connector import failed: {e}")
        return False

    try:
        import mlflow
        print("✅ MLflow imported successfully")
    except ImportError as e:
        print(f"❌ MLflow import failed: {e}")
        return False

    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    return True

def test_env_config():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")

    from dotenv import load_dotenv
    load_dotenv("text_2_sql/.env")

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OpenAI__ApiKey")

    if api_key and api_key.startswith("sk-"):
        print("✅ OpenAI API key configured")
    elif api_key == "<your-openai-api-key>":
        print("⚠️  OpenAI API key not set (still has placeholder value)")
        print("   Please update text_2_sql/.env with your actual API key")
    else:
        print("❌ OpenAI API key not found or invalid")
        print("   Please set OPENAI_API_KEY in text_2_sql/.env")
        return False

    db_engine = os.getenv("Text2Sql__DatabaseEngine")
    if db_engine:
        print(f"✅ Database engine configured: {db_engine}")
    else:
        print("⚠️  Database engine not configured")

    return True

def test_chromadb():
    """Test ChromaDB functionality"""
    print("\n🔍 Testing ChromaDB...")

    try:
        import chromadb
        from chromadb.config import Settings

        # Create a test client
        test_path = "./test_chroma_db"
        client = chromadb.PersistentClient(path=test_path)

        # Create a test collection
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )

        # Add a test document
        collection.add(
            ids=["test1"],
            documents=["This is a test document"],
            metadatas=[{"source": "test"}]
        )

        # Query
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )

        if results and len(results['ids'][0]) > 0:
            print("✅ ChromaDB working correctly")

            # Cleanup
            import shutil
            if os.path.exists(test_path):
                shutil.rmtree(test_path)

            return True
        else:
            print("❌ ChromaDB query returned no results")
            return False

    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("  Open Source Text2SQL Setup Test")
    print("=" * 50)
    print()

    all_passed = True

    # Run tests
    if not test_imports():
        all_passed = False
        print("\n❌ Import tests failed")
        print("   Run: pip install -r requirements.txt")

    if not test_env_config():
        all_passed = False
        print("\n❌ Environment configuration incomplete")
        print("   Edit text_2_sql/.env and add your OpenAI API key")

    if not test_chromadb():
        all_passed = False
        print("\n❌ ChromaDB tests failed")

    print()
    print("=" * 50)

    if all_passed:
        print("✅ All tests passed!")
        print()
        print("You're ready to run the application:")
        print("  streamlit run unified_text2sql_streamlit.py --server.port 8501")
    else:
        print("❌ Some tests failed")
        print()
        print("Please fix the issues above and run this test again")

    print("=" * 50)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
