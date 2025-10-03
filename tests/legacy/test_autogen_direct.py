#!/usr/bin/env python
"""
Direct test of AutoGen system to diagnose why it's not returning data
"""
import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add paths
text_2_sql_path = Path("text_2_sql/text_2_sql_core/src")
autogen_path = Path("text_2_sql/autogen/src")
sys.path.insert(0, str(text_2_sql_path))
sys.path.insert(0, str(autogen_path))

# Load environment
load_dotenv('text_2_sql/.env')

async def test_autogen_directly():
    """Test AutoGen system directly to see where it's failing"""
    
    print("🔍 Testing AutoGen Database Access...")
    print("=" * 60)
    
    # Check environment variables
    print("1. ENVIRONMENT VARIABLES:")
    env_vars = [
        'SPIDER_DATA_DIR',
        'Text2Sql__DatabaseEngine', 
        'Text2Sql__Sqlite__Database',
        'OpenAI__Endpoint',
        'OpenAI__ApiKey'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if var == 'OpenAI__ApiKey':
            value = value[:10] + "..." if value else None
        print(f"   {var}: {value}")
    
    # Check if database file exists
    db_path = os.getenv('Text2Sql__Sqlite__Database')
    print(f"\n2. DATABASE FILE CHECK:")
    print(f"   Path: {db_path}")
    print(f"   Exists: {os.path.exists(db_path) if db_path else False}")
    
    # Check schema file
    schema_dir = os.getenv('SPIDER_DATA_DIR')
    schema_file = os.path.join(schema_dir, 'tables.json') if schema_dir else None
    print(f"\n3. SCHEMA FILE CHECK:")
    print(f"   Schema Dir: {schema_dir}")
    print(f"   Schema File: {schema_file}")
    print(f"   Exists: {os.path.exists(schema_file) if schema_file else False}")
    
    # Test database connection directly
    if db_path and os.path.exists(db_path):
        print(f"\n4. DIRECT DATABASE TEST:")
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM CUSTOMER_DIMENSION")
            customer_count = cursor.fetchone()[0]
            print(f"   Customer count: {customer_count}")
            
            # Test risk rating query
            cursor.execute("SELECT COUNT(*) FROM CUSTOMER_DIMENSION WHERE OFFICER_RISK_RATING_DESC IS NOT NULL")
            rated_customers = cursor.fetchone()[0]
            print(f"   Customers with risk ratings: {rated_customers}")
            
            conn.close()
            print("   ✅ Database connection successful")
            
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
    
    # Test AutoGen system
    print(f"\n5. AUTOGEN SYSTEM TEST:")
    try:
        from autogen_text_2_sql.autogen_text_2_sql import AutoGenText2Sql
        from autogen_text_2_sql.state_store import InMemoryStateStore
        from text_2_sql_core.payloads.interaction_payloads import UserMessagePayload
        
        # Create AutoGen system
        state_store = InMemoryStateStore()
        autogen_system = AutoGenText2Sql(
            state_store=state_store,
            thread_id="test_thread",
            use_case="Banking and financial data analysis",
            enable_cache=True,
            enable_column_value_store=True
        )
        print("   ✅ AutoGen system created successfully")
        
        # Test simple question
        test_question = "How many customers do we have?"
        payload = UserMessagePayload(user_message=test_question, injected_parameters={})
        
        print(f"   Testing question: '{test_question}'")
        
        response_data = None
        async for response_payload in autogen_system.process_user_message("test_thread", payload):
            if hasattr(response_payload, 'payload_type') and response_payload.payload_type.value != 'processing_update':
                response_data = response_payload
                break
        
        if response_data:
            print(f"   ✅ Got response: {type(response_data)}")
            if hasattr(response_data, 'body') and hasattr(response_data.body, 'sources'):
                sources = response_data.body.sources
                print(f"   Sources count: {len(sources) if sources else 0}")
                if sources:
                    for i, source in enumerate(sources[:2]):
                        if hasattr(source, 'sql_query'):
                            print(f"   SQL {i+1}: {source.sql_query[:100]}...")
                else:
                    print("   ❌ No sources returned - this is the problem!")
            
            if hasattr(response_data, 'body') and hasattr(response_data.body, 'answer'):
                answer = response_data.body.answer
                print(f"   Answer: {answer[:200]}...")
        else:
            print("   ❌ No response received")
            
    except Exception as e:
        print(f"   ❌ AutoGen system failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_autogen_directly())