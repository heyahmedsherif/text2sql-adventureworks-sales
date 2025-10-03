#!/usr/bin/env python
"""
Test script to verify MLflow feedback logging is working correctly
"""
import sys
from pathlib import Path

# Add the path for MLflow tracking
sys.path.insert(0, str(Path(__file__).parent))

from mlflow_tracking import get_tracker

def test_feedback_logging():
    print("🧪 Testing MLflow Feedback Logging...")
    print("=" * 50)
    
    # Get the tracker
    tracker = get_tracker()
    
    # Create a test experiment
    test_question = "Test question for feedback verification"
    test_result = {
        'success': True,
        'method': 'Test',
        'sql_query': 'SELECT 1 as test',
        'results': [{'test': 1}]
    }
    
    # Log a test experiment
    print("📝 Logging test experiment...")
    run_id = tracker.log_query_experiment(
        question=test_question,
        approach="Test",
        result=test_result,
        execution_time=0.1,
        session_id="test_session"
    )
    
    if run_id:
        print(f"✅ Test experiment logged with run_id: {run_id}")
        
        # Test feedback logging
        print("📝 Logging test feedback with comment...")
        tracker.log_user_feedback(
            run_id=run_id,
            user_rating=1,
            user_comment="This is a test comment to verify feedback logging works correctly!",
            user_id="test_user"
        )
        
        print("✅ Test feedback logged successfully!")
        
        # Verify the feedback was logged by checking the file system
        import os
        feedback_file = f"mlflow_tracking/302908183335873660/{run_id}/params/user_comment"
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                comment = f.read().strip()
            print(f"🔍 Verified comment in MLflow: '{comment}'")
        else:
            print("❌ Comment file not found")
            
        # Check artifact
        artifact_file = f"mlflow_tracking/302908183335873660/{run_id}/artifacts/feedback_{run_id}.json"
        if os.path.exists(artifact_file):
            print("✅ Feedback artifact JSON file exists")
        else:
            print("❌ Feedback artifact file not found")
            
    else:
        print("❌ Failed to log test experiment")
    
    print("\n" + "=" * 50)
    print("🎯 Feedback logging test completed!")

if __name__ == "__main__":
    test_feedback_logging()