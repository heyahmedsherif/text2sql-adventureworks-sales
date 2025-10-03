#!/usr/bin/env python
"""
MLflow Configuration for FIS Banking Text2SQL
Setup and configuration utilities for MLflow tracking
"""

import os
import mlflow
from mlflow_tracking import Text2SQLMLflowTracker

def setup_mlflow_environment():
    """Setup MLflow environment with proper configuration"""
    
    # Set MLflow tracking URI - can be local or remote
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlflow_tracking")
    mlflow.set_tracking_uri(tracking_uri)
    
    print(f"MLflow tracking URI: {tracking_uri}")
    
    # Create experiment if it doesn't exist
    experiment_name = "FIS_Text2SQL_Banking"
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Created new experiment: {experiment_name} with ID: {experiment_id}")
        else:
            print(f"Using existing experiment: {experiment_name}")
    except Exception as e:
        print(f"Error setting up experiment: {e}")

def view_mlflow_ui():
    """Launch MLflow UI to view experiments and feedback"""
    import subprocess
    import sys
    
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlflow_tracking")
    
    print("Starting MLflow UI...")
    print(f"Tracking URI: {tracking_uri}")
    print("MLflow UI will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the UI")
    
    try:
        subprocess.run([sys.executable, "-m", "mlflow", "ui", "--backend-store-uri", tracking_uri])
    except KeyboardInterrupt:
        print("\nMLflow UI stopped.")

def export_experiment_data(experiment_name="FIS_Text2SQL_Banking", output_file="experiment_data.csv"):
    """Export experiment data to CSV for analysis"""
    import pandas as pd
    
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if not experiment:
            print(f"Experiment '{experiment_name}' not found.")
            return
        
        # Get all runs for this experiment
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        if runs.empty:
            print("No runs found in the experiment.")
            return
        
        # Export to CSV
        runs.to_csv(output_file, index=False)
        print(f"Experiment data exported to: {output_file}")
        print(f"Total runs: {len(runs)}")
        
        # Print summary statistics
        if not runs.empty:
            print("\n--- Experiment Summary ---")
            print(f"Total queries: {len(runs)}")
            print(f"Successful queries: {len(runs[runs['metrics.success'] == 1.0])}")
            print(f"Average execution time: {runs['metrics.execution_time_seconds'].mean():.2f}s")
            
            # Approach breakdown
            approach_counts = {}
            if 'metrics.pattern_match_used' in runs.columns:
                approach_counts['Pattern Match'] = len(runs[runs['metrics.pattern_match_used'] == 1.0])
            if 'metrics.ai_powered_used' in runs.columns:
                approach_counts['AI-Powered'] = len(runs[runs['metrics.ai_powered_used'] == 1.0])
            if 'metrics.autogen_used' in runs.columns:
                approach_counts['AutoGen'] = len(runs[runs['metrics.autogen_used'] == 1.0])
            
            print("Approach usage:")
            for approach, count in approach_counts.items():
                print(f"  {approach}: {count}")
            
            # User feedback summary
            rated_runs = runs[runs['metrics.user_rating'].notna()]
            if not rated_runs.empty:
                avg_rating = rated_runs['metrics.user_rating'].mean()
                print(f"Average user rating: {avg_rating:.2f} ({len(rated_runs)} rated)")
        
    except Exception as e:
        print(f"Error exporting experiment data: {e}")

def cleanup_old_experiments(days_old=30):
    """Cleanup old experiment runs (optional utility)"""
    import time
    from datetime import datetime, timedelta
    
    cutoff_time = datetime.now() - timedelta(days=days_old)
    cutoff_timestamp = int(cutoff_time.timestamp() * 1000)  # MLflow uses milliseconds
    
    try:
        experiment = mlflow.get_experiment_by_name("FIS_Text2SQL_Banking")
        if not experiment:
            print("No experiment found to cleanup.")
            return
        
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        old_runs = runs[runs['start_time'] < cutoff_timestamp]
        
        print(f"Found {len(old_runs)} runs older than {days_old} days")
        
        if len(old_runs) > 0:
            response = input("Do you want to delete these old runs? (y/N): ")
            if response.lower() == 'y':
                for run_id in old_runs['run_id']:
                    mlflow.delete_run(run_id)
                print(f"Deleted {len(old_runs)} old runs")
            else:
                print("Cleanup cancelled")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mlflow_config.py <command>")
        print("Commands:")
        print("  setup    - Setup MLflow environment")
        print("  ui       - Launch MLflow UI")
        print("  export   - Export experiment data to CSV")
        print("  cleanup  - Cleanup old experiments")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        setup_mlflow_environment()
    elif command == "ui":
        view_mlflow_ui()
    elif command == "export":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "experiment_data.csv"
        export_experiment_data(output_file=output_file)
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cleanup_old_experiments(days_old=days)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)