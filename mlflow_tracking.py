#!/usr/bin/env python
"""
MLflow tracking and feedback system for Banking Text2SQL
Captures query performance, results, and user feedback for MLOps
"""

import mlflow
import mlflow.sklearn
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st
import os

# Set up logging
logger = logging.getLogger(__name__)

class Text2SQLMLflowTracker:
    """MLflow tracking system for Text2SQL experiments and feedback"""
    
    def __init__(self, experiment_name: str = "Text2SQL_Banking"):
        """Initialize MLflow tracking
        
        Args:
            experiment_name: Name of the MLflow experiment
        """
        self.experiment_name = experiment_name
        self.setup_mlflow()
        
    def setup_mlflow(self):
        """Setup MLflow tracking configuration"""
        try:
            # Set tracking URI (can be local or remote)
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlflow_tracking")
            mlflow.set_tracking_uri(tracking_uri)
            
            # Set or create experiment
            try:
                experiment = mlflow.get_experiment_by_name(self.experiment_name)
                if experiment is None:
                    experiment_id = mlflow.create_experiment(self.experiment_name)
                    logger.info(f"Created new experiment: {self.experiment_name} with ID: {experiment_id}")
                else:
                    logger.info(f"Using existing experiment: {self.experiment_name}")
            except Exception as e:
                logger.warning(f"Error setting up experiment: {e}")
                
            mlflow.set_experiment(self.experiment_name)
            
        except Exception as e:
            logger.error(f"Failed to setup MLflow: {e}")
            
    def log_query_experiment(self, 
                           question: str, 
                           approach: str, 
                           result: Dict[str, Any],
                           execution_time: float,
                           session_id: str = None) -> str:
        """Log a Text2SQL query experiment to MLflow
        
        Args:
            question: User's natural language question
            approach: Processing approach used (Pattern Match, AI-Powered, AutoGen)
            result: Query result dictionary
            execution_time: Time taken to process query
            session_id: Optional session identifier
            
        Returns:
            run_id: MLflow run ID for this experiment
        """
        run_id = None
        
        try:
            with mlflow.start_run() as run:
                run_id = run.info.run_id
                
                # Log parameters
                mlflow.log_param("question", question)
                mlflow.log_param("approach", approach)
                mlflow.log_param("session_id", session_id or str(uuid.uuid4()))
                mlflow.log_param("timestamp", datetime.now().isoformat())
                
                # Log metrics
                mlflow.log_metric("execution_time_seconds", execution_time)
                mlflow.log_metric("success", 1 if result.get('success', False) else 0)
                
                # Log query details
                if result.get('sql_query'):
                    mlflow.log_param("sql_query", result['sql_query'])
                    
                if result.get('results'):
                    mlflow.log_metric("result_count", len(result['results']))
                else:
                    mlflow.log_metric("result_count", 0)
                    
                # Log approach-specific metrics
                if approach == "Pattern Match":
                    mlflow.log_metric("pattern_match_used", 1)
                elif approach == "AI-Powered":
                    mlflow.log_metric("ai_powered_used", 1)
                elif approach == "AutoGen Multi-Agent":
                    mlflow.log_metric("autogen_used", 1)
                    
                # Log error information if available
                if not result.get('success', False) and result.get('error'):
                    mlflow.log_param("error_message", str(result['error']))
                    
                # Log result as artifact
                result_data = {
                    "question": question,
                    "approach": approach,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                }
                
                # Save result as JSON artifact
                result_file = f"query_result_{run_id}.json"
                with open(result_file, 'w') as f:
                    json.dump(result_data, f, indent=2, default=str)
                mlflow.log_artifact(result_file)
                
                # Clean up temporary file
                if os.path.exists(result_file):
                    os.remove(result_file)
                    
                logger.info(f"Logged experiment with run_id: {run_id}")
                
        except Exception as e:
            logger.error(f"Failed to log experiment: {e}")
            
        return run_id
        
    def log_user_feedback(self, 
                         run_id: str, 
                         user_rating: int, 
                         user_comment: str = "",
                         user_id: str = None):
        """Log user feedback for a specific query result
        
        Args:
            run_id: MLflow run ID to associate feedback with
            user_rating: User rating (1-5 scale, or thumbs up/down as 1/0)
            user_comment: Optional user comment
            user_id: Optional user identifier
        """
        try:
            # Update the existing run with feedback
            with mlflow.start_run(run_id=run_id):
                mlflow.log_metric("user_rating", user_rating)
                mlflow.log_param("user_comment", user_comment)
                mlflow.log_param("user_id", user_id or "anonymous")
                mlflow.log_param("feedback_timestamp", datetime.now().isoformat())
                
                # Log feedback as artifact
                feedback_data = {
                    "run_id": run_id,
                    "user_rating": user_rating,
                    "user_comment": user_comment,
                    "user_id": user_id,
                    "feedback_timestamp": datetime.now().isoformat()
                }
                
                feedback_file = f"feedback_{run_id}.json"
                with open(feedback_file, 'w') as f:
                    json.dump(feedback_data, f, indent=2)
                mlflow.log_artifact(feedback_file)
                
                # Clean up temporary file
                if os.path.exists(feedback_file):
                    os.remove(feedback_file)
                    
                logger.info(f"Logged user feedback for run_id: {run_id}")
                
        except Exception as e:
            logger.error(f"Failed to log user feedback: {e}")
            
    def get_experiment_stats(self) -> Dict[str, Any]:
        """Get experiment statistics and metrics
        
        Returns:
            Dictionary containing experiment statistics
        """
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return {}
                
            # Get all runs for this experiment
            runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
            
            if runs.empty:
                return {"total_runs": 0}
                
            stats = {
                "total_runs": len(runs),
                "successful_runs": len(runs[runs['metrics.success'] == 1.0]),
                "average_execution_time": runs['metrics.execution_time_seconds'].mean(),
                "approaches_used": {
                    "pattern_match": len(runs[runs['metrics.pattern_match_used'] == 1.0]),
                    "ai_powered": len(runs[runs['metrics.ai_powered_used'] == 1.0]),
                    "autogen": len(runs[runs['metrics.autogen_used'] == 1.0])
                }
            }
            
            # Calculate average user rating if feedback exists
            rated_runs = runs[runs['metrics.user_rating'].notna()]
            if not rated_runs.empty:
                stats["average_user_rating"] = rated_runs['metrics.user_rating'].mean()
                stats["total_rated_runs"] = len(rated_runs)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get experiment stats: {e}")
            return {}

# Note: Feedback UI is now implemented directly in the main Streamlit app
# to avoid duplicate element key conflicts

def render_mlflow_stats(tracker: Text2SQLMLflowTracker):
    """Render MLflow experiment statistics in sidebar
    
    Args:
        tracker: MLflow tracker instance
    """
    stats = tracker.get_experiment_stats()
    
    if stats.get("total_runs", 0) > 0:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Usage Statistics")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.metric("Total Queries", stats.get("total_runs", 0))
            st.metric("Success Rate", f"{(stats.get('successful_runs', 0) / stats.get('total_runs', 1) * 100):.1f}%")
            
        with col2:
            st.metric("Avg Response Time", f"{stats.get('average_execution_time', 0):.2f}s")
            if stats.get("average_user_rating") is not None:
                rating_percent = stats["average_user_rating"] * 100
                st.metric("User Satisfaction", f"{rating_percent:.1f}%")
        
        # Approach usage breakdown
        approaches = stats.get("approaches_used", {})
        if any(approaches.values()):
            st.sidebar.markdown("**Approach Usage:**")
            total_approaches = sum(approaches.values())
            for approach, count in approaches.items():
                if count > 0:
                    percentage = (count / total_approaches) * 100
                    st.sidebar.write(f"• {approach.replace('_', ' ').title()}: {percentage:.1f}%")

# Initialize tracker as module-level variable
tracker = None

def get_tracker() -> Text2SQLMLflowTracker:
    """Get or create MLflow tracker instance"""
    global tracker
    if tracker is None:
        tracker = Text2SQLMLflowTracker()
    return tracker