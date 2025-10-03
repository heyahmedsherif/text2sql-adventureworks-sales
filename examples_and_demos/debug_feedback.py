#!/usr/bin/env python
"""
Debug script to test feedback functionality step by step
"""
import streamlit as st
import sys
from pathlib import Path

# Add paths for the text2sql modules
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
autogen_path = Path(__file__).parent / "text_2_sql" / "autogen" / "src"
sys.path.insert(0, str(text_2_sql_path))
sys.path.insert(0, str(autogen_path))

st.title("🔍 Debug Feedback Issue")

# Test 1: Import check
st.subheader("1. Testing Imports")
try:
    from mlflow_tracking import get_tracker, render_feedback_ui, render_mlflow_stats
    st.success("✅ MLflow tracking imports successful")
except Exception as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

# Test 2: Tracker initialization
st.subheader("2. Testing Tracker Initialization")
try:
    tracker = get_tracker()
    st.success("✅ MLflow tracker initialized")
    st.write(f"Tracker type: {type(tracker)}")
except Exception as e:
    st.error(f"❌ Tracker initialization error: {e}")
    st.stop()

# Test 3: Create a test run
st.subheader("3. Testing MLflow Logging")
if st.button("Create Test Run"):
    try:
        test_result = {
            'success': True,
            'method': 'Debug Test',
            'sql_query': 'SELECT 1',
            'results': [{'result': 1}],
            'question': 'Debug test question'
        }
        
        run_id = tracker.log_query_experiment(
            question="Debug test question",
            approach="Debug Test",
            result=test_result,
            execution_time=0.1,
            session_id="debug_session"
        )
        
        if run_id:
            st.success(f"✅ Created run with ID: {run_id}")
            st.session_state.test_run_id = run_id
        else:
            st.error("❌ No run_id returned from log_query_experiment")
    except Exception as e:
        st.error(f"❌ Error creating test run: {e}")
        st.write(f"Error details: {type(e).__name__}: {str(e)}")

# Test 4: Render feedback UI
st.subheader("4. Testing Feedback UI Rendering")
if hasattr(st.session_state, 'test_run_id') and st.session_state.test_run_id:
    try:
        st.write(f"Using run_id: {st.session_state.test_run_id}")
        st.write("About to call render_feedback_ui...")
        
        # This should show the feedback UI
        render_feedback_ui(st.session_state.test_run_id, tracker)
        
        st.write("✅ render_feedback_ui call completed")
    except Exception as e:
        st.error(f"❌ Error rendering feedback UI: {e}")
        st.write(f"Error details: {type(e).__name__}: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
else:
    st.info("👆 Click 'Create Test Run' above first")

# Test 5: Manual feedback form (as backup)
st.subheader("5. Manual Feedback Form Test")
st.write("This is what the feedback UI should look like:")

with st.form("manual_feedback_test"):
    st.markdown("---")
    st.subheader("📝 Feedback")
    st.markdown("Help us improve by rating this response:")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        feedback_type = st.radio(
            "Was this response helpful?",
            ["👍 Yes", "👎 No"],
            key="manual_feedback"
        )
    
    with col2:
        user_comment = st.text_area(
            "Comments (optional):",
            placeholder="What was good or what could be improved?",
            key="manual_comment",
            height=100
        )
    
    submitted = st.form_submit_button("Submit Manual Test Feedback")
    
    if submitted:
        user_rating = 1 if feedback_type == "👍 Yes" else 0
        st.success(f"✅ Manual test feedback: Rating={user_rating}, Comment='{user_comment}'")
        
        # Try to log this feedback if we have a run_id
        if hasattr(st.session_state, 'test_run_id') and st.session_state.test_run_id:
            try:
                tracker.log_user_feedback(
                    run_id=st.session_state.test_run_id,
                    user_rating=user_rating,
                    user_comment=user_comment,
                    user_id="debug_user"
                )
                st.success("✅ Feedback logged to MLflow!")
            except Exception as e:
                st.error(f"❌ Error logging feedback: {e}")

st.markdown("---")
st.markdown("**Troubleshooting Steps:**")
st.markdown("1. All tests above should pass with ✅")
st.markdown("2. You should see the feedback form in section 4 after creating a test run")
st.markdown("3. The manual form in section 5 shows what it should look like")
st.markdown("4. Check MLflow UI at http://localhost:5001 to verify data is being logged")