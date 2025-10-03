#!/usr/bin/env python
"""
Test OpenAI connection for Text2SQL
"""
import sys
import os
import asyncio
from pathlib import Path

# Add text_2_sql_core to path
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

async def test_openai():
    """Test OpenAI connection"""
    print("=== TESTING OPENAI CONNECTION ===")
    
    try:
        from text_2_sql_core.connectors.open_ai import OpenAIConnector
        
        connector = OpenAIConnector()
        
        messages = [
            {"role": "user", "content": "What is 2+2? Give a short answer."}
        ]
        
        result = await connector.run_completion_request(messages)
        
        print("✅ OpenAI connection successful!")
        print(f"Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def test_env_vars():
    """Test environment variables"""
    print("=== TESTING ENVIRONMENT VARIABLES ===")
    
    required_vars = [
        'OpenAI__Endpoint',
        'OpenAI__ApiKey', 
        'OpenAI__CompletionDeployment',
        'OpenAI__ApiVersion'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: configured")
        else:
            print(f"❌ {var}: missing")
            all_good = False
            
    return all_good

async def main():
    """Run all tests"""
    print("Testing Text2SQL OpenAI setup...\n")
    
    env_ok = test_env_vars()
    
    if env_ok:
        openai_ok = await test_openai()
    else:
        openai_ok = False
    
    print(f"\n=== SUMMARY ===")
    if env_ok and openai_ok:
        print("✅ OpenAI setup is working! Text2SQL should be able to generate SQL queries.")
    else:
        print("❌ Some issues found. Check configuration.")

if __name__ == "__main__":
    asyncio.run(main())