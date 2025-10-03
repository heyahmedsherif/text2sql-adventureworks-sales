#!/usr/bin/env python
"""
Test AutoGen disambiguation response to see what user choices are being offered
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

async def test_disambiguation_details():
    """Test AutoGen disambiguation response details"""
    
    print("🔍 Testing AutoGen Disambiguation Response...")
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
        
        # Test the question that should trigger disambiguation
        test_question = "Identify trends in customer risk assessment showing concerning patterns across different rating sources"
        payload = UserMessagePayload(user_message=test_question, injected_parameters={})
        
        print(f"Testing question: '{test_question}'")
        
        response_data = None
        async for response_payload in autogen_system.process_user_message("test_thread", payload):
            if hasattr(response_payload, 'payload_type') and response_payload.payload_type.value != 'processing_update':
                response_data = response_payload
                break
        
        if response_data and response_data.payload_type.value == 'disambiguation_requests':
            print(f"\n🎯 Got disambiguation response!")
            
            # Get disambiguation requests
            if hasattr(response_data.body, 'disambiguation_requests'):
                requests = response_data.body.disambiguation_requests
                print(f"\nDisambiguation requests count: {len(requests) if requests else 0}")
                
                for i, req in enumerate(requests):
                    print(f"\n--- Request {i+1} ---")
                    print(f"Type: {type(req)}")
                    print(f"Attributes: {dir(req)}")
                    
                    # Check common fields
                    if hasattr(req, 'question'):
                        print(f"Question: {req.question}")
                    if hasattr(req, 'options'):
                        print(f"Options: {req.options}")
                    if hasattr(req, 'clarification_request'):
                        print(f"Clarification: {req.clarification_request}")
                    if hasattr(req, 'suggested_entities'):
                        print(f"Suggested entities: {req.suggested_entities}")
                    
                    # Print all fields
                    try:
                        print(f"Full request: {req}")
                    except:
                        print("Could not print full request")
            
            # Check steps
            if hasattr(response_data.body, 'steps'):
                print(f"\nSteps: {response_data.body.steps}")
        
        else:
            print(f"❌ Unexpected response type: {response_data.payload_type.value if response_data else 'None'}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_disambiguation_details())