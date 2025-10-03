#!/usr/bin/env python
"""
Test Text2SQL application setup and configuration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add text_2_sql_core to path
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

# Load environment variables
load_dotenv('text_2_sql/.env')

def test_environment_setup():
    """Test if all required environment variables are configured"""
    print("=== TESTING TEXT2SQL ENVIRONMENT SETUP ===")
    
    required_vars = [
        'Text2Sql__DatabaseEngine',
        'OpenAI__CompletionDeployment',
        'OpenAI__Endpoint', 
        'OpenAI__ApiKey',
        'AIService__AzureSearchOptions__Endpoint',
        'AIService__AzureSearchOptions__Key',
        'Text2Sql__Tsql__ConnectionString',
        'Text2Sql__Tsql__Database'
    ]
    
    all_configured = True
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith('<'):
            print(f"✓ {var}: configured")
        else:
            print(f"✗ {var}: missing or not configured")
            all_configured = False
    
    return all_configured

def test_imports():
    """Test if all required modules can be imported"""
    print("\n=== TESTING MODULE IMPORTS ===")
    
    try:
        from text_2_sql_core.utils.environment import Environment
        print("✓ text_2_sql_core.utils.environment imported successfully")
        
        env = Environment()
        print(f"✓ Environment object created successfully")
        print(f"  - Database engine: {env.text_2_sql_database_engine}")
        print(f"  - OpenAI endpoint: {env.openai_endpoint}")
        print(f"  - AI Search endpoint: {env.ai_search_endpoint}")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_ai_services():
    """Test AI services connections"""
    print("\n=== TESTING AI SERVICES ===")
    
    try:
        # Test Azure OpenAI
        from text_2_sql_core.connectors.open_ai import OpenAIConnector
        
        openai_connector = OpenAIConnector()
        print("✓ OpenAI connector created successfully")
        
        # Test Azure AI Search
        from text_2_sql_core.connectors.ai_search import AISearchConnector
        
        search_connector = AISearchConnector()
        print("✓ AI Search connector created successfully")
        
        return True
    except Exception as e:
        print(f"✗ AI services test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Text2SQL setup...\n")
    
    env_ok = test_environment_setup()
    imports_ok = test_imports()
    services_ok = test_ai_services()
    
    print("\n=== SUMMARY ===")
    if env_ok and imports_ok and services_ok:
        print("✅ All tests passed! Text2SQL is ready to use.")
        print("\nNext steps:")
        print("1. Generate data dictionary: python -m text_2_sql_core.data_dictionary.cli TSQL -o data_dictionary_output -gen")
        print("2. Upload data dictionary files to your schema store")
        print("3. Test Text2SQL queries")
    else:
        print("❌ Some tests failed. Check the configuration.")
        
if __name__ == "__main__":
    main()