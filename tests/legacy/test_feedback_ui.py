#!/usr/bin/env python
"""
Test script to verify feedback UI is working
"""
import streamlit as st
import sys
from pathlib import Path

# Add paths for the text2sql modules
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
autogen_path = Path(__file__).parent / "text_2_sql" / "autogen" / "src"
sys.path.insert(0, str(text_2_sql_path))
sys.path.insert(0, str(autogen_path))

from mlflow_tracking import get_tracker, render_feedback_ui

st.title("🧪 Test Feedback UI")

# Initialize tracker
tracker = get_tracker()

# Create a test run
test_result = {
    'success': True,
    'method': 'Test Method',
    'sql_query': 'SELECT COUNT(*) FROM test_table',
    'results': [{'count': 100}]
}

if st.button("Create Test Run"):
    run_id = tracker.log_query_experiment(
        question="Test question for feedback",
        approach="Test Method",
        result=test_result,
        execution_time=0.1,
        session_id="test_session"
    )
    
    st.success(f"Created test run: {run_id}")
    
    # Show the feedback UI
    st.markdown("---")
    st.subheader("This is what the feedback UI should look like:")
    render_feedback_ui(run_id, tracker)

st.markdown("---")
st.markdown("**Instructions:**")
st.markdown("1. Click 'Create Test Run' above")
st.markdown("2. You should see the feedback form appear")
st.markdown("3. Select 👍 or 👎 and add a comment")
st.markdown("4. Click 'Submit Feedback'")
st.markdown("5. Check MLflow UI at http://localhost:5001 to see the feedback")