#!/usr/bin/env python
"""
Test multiple demo questions to find reliable ones for stakeholder presentation
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

def test_demo_question(question, timeout=60):
    """Test a single demo question with timeout"""
    print(f"\n{'='*80}")
    print(f"Testing: {question}")
    print('='*80)
    
    try:
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Question timed out")
        
        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        result = process_autogen_sync(question)
        
        # Cancel timeout
        signal.alarm(0)
        
        print(f"✅ SUCCESS")
        print(f"Method: {result.get('method')}")
        print(f"Response Type: {result.get('response_type', 'answer')}")
        print(f"Success: {result.get('success')}")
        
        if result.get('answer'):
            answer_preview = result['answer'][:200] + "..." if len(result['answer']) > 200 else result['answer']
            print(f"Answer Preview: {answer_preview}")
        
        if result.get('sql_query'):
            print(f"SQL Generated: ✅")
        
        if result.get('results'):
            print(f"Results: {len(result['results'])} rows")
        
        return True, result
        
    except TimeoutError:
        print(f"❌ TIMEOUT after {timeout} seconds")
        return False, "timeout"
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        print(f"❌ ERROR: {e}")
        return False, str(e)

def main():
    """Test multiple demo questions to find reliable ones"""
    
    print("🎯 Testing Demo Questions for Stakeholder Presentation")
    print("=" * 80)
    
    # List of potential demo questions - from simple to complex
    demo_questions = [
        # Simple, straightforward questions
        "What is our total loan portfolio value?",
        "How many customers do we have with high risk ratings?",
        "Show me the top 5 customers by loan balance",
        
        # Medium complexity
        "What percentage of our customers have risk ratings of SUBSTANDARD or worse?",
        "Which customers have the highest loan balances and what are their risk ratings?",
        "How many customers have past due amounts greater than $10,000?",
        
        # Banking-specific analysis
        "Analyze the distribution of risk ratings across our customer base",
        "What is the total exposure to customers with SUBSTANDARD risk ratings?",
        "Show me customers with high loan balances but concerning risk ratings",
        
        # Multi-table analysis
        "Compare loan balances to risk ratings to identify potential problem accounts",
        "Analyze the relationship between customer risk ratings and loan performance",
        "Identify customers with multiple risk factors indicating potential default"
    ]
    
    successful_questions = []
    failed_questions = []
    
    for question in demo_questions:
        success, result = test_demo_question(question, timeout=45)
        
        if success:
            successful_questions.append((question, result))
        else:
            failed_questions.append((question, result))
    
    print(f"\n\n🎯 DEMO QUESTION RECOMMENDATIONS")
    print("=" * 80)
    
    if successful_questions:
        print(f"✅ SUCCESSFUL QUESTIONS ({len(successful_questions)}):")
        print("These questions work reliably for your demo:\n")
        
        for i, (question, result) in enumerate(successful_questions, 1):
            print(f"{i}. \"{question}\"")
            if result.get('results'):
                print(f"   → Returns {len(result['results'])} results")
            if result.get('answer'):
                print(f"   → Provides detailed analysis")
            print()
    
    if failed_questions:
        print(f"\n❌ AVOID THESE QUESTIONS ({len(failed_questions)}):")
        for question, error in failed_questions:
            print(f"• \"{question}\" - {error}")
    
    # Recommend top 3 for demo
    if successful_questions:
        print(f"\n🏆 TOP 3 RECOMMENDED FOR DEMO:")
        for i, (question, result) in enumerate(successful_questions[:3], 1):
            print(f"{i}. \"{question}\"")
            if result.get('answer'):
                answer_preview = result['answer'][:150] + "..." if len(result['answer']) > 150 else result['answer']
                print(f"   Preview: {answer_preview}")
        
        print(f"\n💡 For your stakeholder demo tomorrow, use questions 1-3 above.")
        print(f"   They provide good analysis and complete quickly.")

if __name__ == "__main__":
    main()