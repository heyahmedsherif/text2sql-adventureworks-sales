#!/usr/bin/env python
"""
Test the updated AutoGen disambiguation functionality in unified_text2sql_streamlit.py
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

# Import the process_autogen_sync function from the Streamlit app
from unified_text2sql_streamlit import process_autogen_sync

def test_disambiguation_in_streamlit():
    """Test the AutoGen disambiguation functionality as used in Streamlit"""
    
    print("🔍 Testing AutoGen Disambiguation in Streamlit Context...")
    print("=" * 70)
    
    # Test the same question that triggers disambiguation
    test_question = "Identify trends in customer risk assessment showing concerning patterns across different rating sources"
    
    print(f"Testing question: '{test_question}'")
    print("\nProcessing with AutoGen...")
    
    try:
        # Use the same function that Streamlit uses
        result = process_autogen_sync(test_question)
        
        print(f"\n✅ Result received!")
        print(f"Method: {result.get('method')}")
        print(f"Success: {result.get('success')}")
        print(f"Response type: {result.get('response_type')}")
        
        if result.get('response_type') == 'disambiguation':
            print(f"\n🎯 Disambiguation detected!")
            
            clarification_questions = result.get('clarification_questions', [])
            user_choices = result.get('user_choices', [])
            
            print(f"Clarification questions ({len(clarification_questions)}):")
            for i, question in enumerate(clarification_questions, 1):
                print(f"  {i}. {question}")
            
            print(f"\nUser choices ({len(user_choices)}):")
            for i, choice in enumerate(user_choices, 1):
                print(f"  {i}. {choice}")
            
            if user_choices:
                print(f"\n✅ SUCCESS: User choices found and should be displayed in Streamlit!")
            else:
                print(f"\n❌ ISSUE: No user choices found")
        else:
            print(f"\n❌ Not a disambiguation response: {result.get('response_type')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_disambiguation_in_streamlit()