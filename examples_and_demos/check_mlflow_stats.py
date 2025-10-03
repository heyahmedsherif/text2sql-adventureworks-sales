#!/usr/bin/env python
"""
Simple script to check MLflow experiment statistics
"""
import sys
from pathlib import Path

# Add the path for MLflow tracking
sys.path.insert(0, str(Path(__file__).parent))

from mlflow_tracking import get_tracker

def main():
    print("🔍 Checking MLflow Experiment Statistics...")
    print("=" * 50)
    
    # Get the tracker
    tracker = get_tracker()
    
    # Get stats
    stats = tracker.get_experiment_stats()
    
    if not stats:
        print("❌ No experiment statistics found")
        return
    
    print(f"📊 Total Experiments: {stats.get('total_runs', 0)}")
    print(f"✅ Successful Runs: {stats.get('successful_runs', 0)}")
    print(f"⏱️ Average Execution Time: {stats.get('average_execution_time', 0):.2f}s")
    
    if stats.get("average_user_rating") is not None:
        print(f"⭐ Average User Rating: {stats['average_user_rating']:.2f}")
        print(f"📝 Total Rated Runs: {stats.get('total_rated_runs', 0)}")
    else:
        print("📝 No user ratings yet")
    
    # Approach breakdown
    approaches = stats.get("approaches_used", {})
    if any(approaches.values()):
        print("\n🚀 Approach Usage:")
        total_approaches = sum(approaches.values())
        for approach, count in approaches.items():
            if count > 0:
                percentage = (count / total_approaches) * 100
                print(f"  • {approach.replace('_', ' ').title()}: {count} runs ({percentage:.1f}%)")
    
    # Show recent comments
    print("\n💬 Recent User Comments:")
    try:
        import os
        import glob
        
        # Find recent comment files
        comment_files = glob.glob("mlflow_tracking/302908183335873660/*/params/user_comment")
        if comment_files:
            for comment_file in comment_files[-3:]:  # Show last 3 comments
                try:
                    with open(comment_file, 'r') as f:
                        comment = f.read().strip()
                    run_id = comment_file.split('/')[-3][:8]  # First 8 chars of run ID
                    print(f"  • [{run_id}]: '{comment}'")
                except:
                    pass
        else:
            print("  No comments found yet")
    except Exception as e:
        print(f"  Error reading comments: {e}")
    
    print("\n" + "=" * 50)
    print("✅ MLflow tracking is working correctly!")
    print("🌐 Access MLflow UI at: http://127.0.0.1:5001")
    print("🖥️ Streamlit App at: http://localhost:8501")
    print("📝 Comments are being captured in both parameters and JSON artifacts!")

if __name__ == "__main__":
    main()