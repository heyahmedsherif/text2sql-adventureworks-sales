#!/usr/bin/env python
"""
Test what fields are available in AutoGen response to capture follow-up suggestions
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

async def test_autogen_response_fields():
    """Test AutoGen response to see all available fields"""
    
    print("🔍 Testing AutoGen Response Fields...")
    print("=" * 60)
    
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
        
        # Test the question that should have follow-up suggestions
        test_question = "Identify trends in customer risk assessment showing concerning patterns across different rating sources"
        payload = UserMessagePayload(user_message=test_question, injected_parameters={})
        
        print(f"Testing question: '{test_question}'")
        
        response_data = None
        async for response_payload in autogen_system.process_user_message("test_thread", payload):
            if hasattr(response_payload, 'payload_type') and response_payload.payload_type.value != 'processing_update':
                response_data = response_payload
                break
        
        if response_data:
            print(f"\n✅ Got response: {type(response_data)}")
            print(f"Response payload type: {response_data.payload_type}")
            
            # Check all available attributes
            print(f"\nAll attributes: {dir(response_data)}")
            
            # Check body attributes if available
            if hasattr(response_data, 'body'):
                print(f"\nBody type: {type(response_data.body)}")
                print(f"Body attributes: {dir(response_data.body)}")
                
                # Check for follow_up_suggestions specifically
                if hasattr(response_data.body, 'follow_up_suggestions'):
                    suggestions = response_data.body.follow_up_suggestions
                    print(f"\n🎯 Found follow_up_suggestions: {suggestions}")
                else:
                    print(f"\n❌ No follow_up_suggestions in body")
                
                # Check for steps
                if hasattr(response_data.body, 'steps'):
                    steps = response_data.body.steps
                    print(f"\n📋 Found steps: {steps}")
                
                # Check sources
                if hasattr(response_data.body, 'sources'):
                    sources = response_data.body.sources
                    print(f"\n📊 Found sources count: {len(sources) if sources else 0}")
                
                # Check answer
                if hasattr(response_data.body, 'answer'):
                    answer = response_data.body.answer
                    print(f"\n💬 Answer preview: {answer[:200]}...")
            
            # Check if follow_up_suggestions is at the top level
            if hasattr(response_data, 'follow_up_suggestions'):
                suggestions = response_data.follow_up_suggestions
                print(f"\n🎯 Found follow_up_suggestions at top level: {suggestions}")
            
        else:
            print("❌ No response received")
            
    except Exception as e:
        print(f"❌ AutoGen test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_autogen_response_fields())