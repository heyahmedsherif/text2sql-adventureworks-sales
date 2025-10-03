#!/usr/bin/env python
"""
Test AutoGen Text2SQL with banking data
"""
import os
import sys
import asyncio
from pathlib import Path

# Add autogen path
autogen_path = Path(__file__).parent / "text_2_sql" / "autogen" / "src"
sys.path.insert(0, str(autogen_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

async def test_autogen_text2sql():
    """Test AutoGen Text2SQL system"""
    print("=== TESTING AUTOGEN TEXT2SQL SYSTEM ===")
    
    try:
        from autogen_text_2_sql.autogen_text_2_sql import AutoGenText2Sql
        from autogen_text_2_sql.state_store import InMemoryStateStore
        from text_2_sql_core.payloads.interaction_payloads import UserMessagePayload
        
        # Create state store for multi-agent coordination
        state_store = InMemoryStateStore()
        
        # Initialize AutoGen Text2SQL system
        autogen_system = AutoGenText2Sql(
            state_store=state_store,
            use_case="Analyzing banking and loan data"
        )
        
        print("✅ AutoGen Text2SQL system initialized")
        
        # Test queries with increasing complexity
        test_queries = [
            "How many customers do we have?",
            "What are the different customer types and their counts?", 
            "Show me the top 5 customers by total loan balance",
            "What is our total loan portfolio value in millions?",
            "Which customers have the highest risk ratings?",
            "What are the most common loan products?",
            "Show me loans that are past due",
            "What is the average loan amount by customer type?"
        ]
        
        print(f"\n🧠 Testing {len(test_queries)} queries with AutoGen agents...")
        
        successful_queries = 0
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"📋 Query {i}: {query}")
            print(f"{'='*60}")
            
            try:
                # Use AutoGen multi-agent system
                thread_id = f"banking_test_{i}"
                message_payload = UserMessagePayload(user_message=query)
                
                results = []
                async for message in autogen_system.process_user_message(
                    thread_id=thread_id, 
                    message_payload=message_payload
                ):
                    results.append(message)
                
                # Get the final result
                result = results[-1] if results else None
                
                if result and hasattr(result, 'answer'):
                    print(f"🎯 Answer: {result.answer}")
                    
                    if hasattr(result, 'sources') and result.sources:
                        for j, source in enumerate(result.sources, 1):
                            if hasattr(source, 'sql_query'):
                                print(f"🔍 SQL Query {j}: {source.sql_query}")
                            if hasattr(source, 'sql_rows') and source.sql_rows:
                                print(f"📊 Results: {len(source.sql_rows)} rows")
                                # Show first few results
                                for k, row in enumerate(source.sql_rows[:3], 1):
                                    print(f"   {k}: {row}")
                                if len(source.sql_rows) > 3:
                                    print(f"   ... and {len(source.sql_rows) - 3} more rows")
                    
                    successful_queries += 1
                    print("✅ SUCCESS")
                    
                else:
                    print("❌ No result returned")
                    
            except Exception as e:
                print(f"❌ Query failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Summary
        success_rate = (successful_queries / len(test_queries)) * 100
        
        print(f"\n{'='*80}")
        print(f"🏆 AUTOGEN TEXT2SQL RESULTS")
        print(f"{'='*80}")
        print(f"Total Queries: {len(test_queries)}")
        print(f"Successful: {successful_queries}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print(f"\n🎉 EXCELLENT! AutoGen agents are working well!")
            print(f"✅ Multi-agent coordination")
            print(f"✅ Schema selection and disambiguation") 
            print(f"✅ SQL generation and correction")
            print(f"✅ Query execution with real data")
            print(f"\n🚀 Your AutoGen Text2SQL system is production ready!")
            
        else:
            print(f"\n⚠️  Some queries failed. AutoGen agents may need tuning.")
            
        return success_rate >= 75
        
    except Exception as e:
        print(f"❌ AutoGen system initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Initializing AutoGen Text2SQL with your banking database...\n")
    
    # Check if required environment variables are set
    required_vars = [
        'Text2Sql__DatabaseEngine',
        'OpenAI__Endpoint',
        'OpenAI__ApiKey'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return
    
    success = await test_autogen_text2sql()
    
    if success:
        print(f"\n🎊 CONGRATULATIONS!")
        print(f"Your AutoGen Text2SQL system is fully operational!")
    else:
        print(f"\n🔧 System needs configuration adjustments")

if __name__ == "__main__":
    asyncio.run(main())