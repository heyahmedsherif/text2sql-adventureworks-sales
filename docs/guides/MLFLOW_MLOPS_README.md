# 🧠 MLflow MLOps Integration for FIS Banking Text2SQL

## 📋 Overview

The FIS Banking Text2SQL application now includes comprehensive MLOps capabilities using MLflow to track, monitor, and improve system performance through user feedback and experiment tracking.

## 🚀 New Features

### **1. Automatic Experiment Tracking**
- Every query is automatically logged as an MLflow experiment
- Tracks response times, success rates, and approach usage
- Captures SQL queries, results, and error information
- Associates queries with user sessions

### **2. User Feedback Collection**
- **Thumbs Up/Down Rating**: Simple feedback mechanism
- **Optional Comments**: Detailed user feedback
- **Real-time Collection**: Feedback captured immediately after results
- **MLflow Integration**: All feedback stored in MLflow for analysis

### **3. Performance Analytics**
- **Usage Statistics**: Query volume, success rates, response times
- **Approach Analysis**: Performance comparison across Pattern Match, AI-Powered, and AutoGen
- **User Satisfaction**: Rating trends and feedback analysis
- **Session Tracking**: User behavior and query patterns

### **4. MLOps Dashboard**
- **Real-time Metrics**: Live statistics in Streamlit sidebar
- **Historical Analysis**: MLflow UI for detailed experiment analysis
- **Data Export**: CSV export for external analysis
- **Automated Cleanup**: Configurable retention policies

---

## 🔧 Setup Instructions

### **1. Install Dependencies**
```bash
pip install mlflow>=3.0.0
pip install streamlit>=1.28.0
```

### **2. Initialize MLflow Environment**
```bash
python mlflow_config.py setup
```

### **3. Launch Application**
```bash
streamlit run unified_text2sql_streamlit.py
```

### **4. View MLflow UI (Optional)**
```bash
python mlflow_config.py ui
# Opens MLflow UI at http://localhost:5000
```

---

## 📊 Using the MLOps Features

### **In the Streamlit Application:**

#### **1. Query Processing**
- Ask any question using Pattern Match, AI-Powered, or AutoGen Multi-Agent
- System automatically logs:
  - Question text
  - Processing approach used
  - Execution time
  - SQL query generated
  - Results returned
  - Success/failure status

#### **2. Providing Feedback**
After each query result:
1. **Rate the Response**: Click 👍 (helpful) or 👎 (not helpful)
2. **Add Comments** (optional): Provide specific feedback about accuracy, completeness, or suggestions
3. **Submit Feedback**: Click "Submit Feedback" to save to MLflow

#### **3. Monitoring Performance**
Check the sidebar for real-time statistics:
- **Total Queries**: Number of queries processed
- **Success Rate**: Percentage of successful queries
- **Average Response Time**: System performance metrics
- **User Satisfaction**: Percentage of positive feedback
- **Approach Usage**: Breakdown by processing method

### **In MLflow UI:**

#### **1. Launch MLflow Dashboard**
```bash
python mlflow_config.py ui
```

#### **2. Explore Experiments**
- Navigate to "FIS_Text2SQL_Banking" experiment
- View all query runs with detailed metrics
- Filter by approach, success rate, or time period
- Analyze user feedback and comments

#### **3. Compare Performance**
- Compare response times across approaches
- Identify most successful query patterns
- Track user satisfaction trends over time

---

## 📈 Analytics & Reporting

### **Export Data for Analysis**
```bash
# Export all experiment data to CSV
python mlflow_config.py export experiment_data.csv

# View summary statistics
python mlflow_config.py export
```

### **Key Metrics Tracked**
| Metric | Description | Use Case |
|--------|-------------|----------|
| `execution_time_seconds` | Query processing time | Performance optimization |
| `success` | Query success (1) or failure (0) | Reliability monitoring |
| `user_rating` | User feedback (1=helpful, 0=not helpful) | Quality assessment |
| `approach_used` | Pattern Match/AI-Powered/AutoGen | Approach comparison |
| `result_count` | Number of results returned | Query effectiveness |

### **Performance Analysis Queries**

#### **1. Success Rate by Approach**
```python
import mlflow
import pandas as pd

runs = mlflow.search_runs(experiment_ids=["your_experiment_id"])
success_by_approach = runs.groupby('params.approach')['metrics.success'].mean()
print(success_by_approach)
```

#### **2. Average Response Time**
```python
avg_time_by_approach = runs.groupby('params.approach')['metrics.execution_time_seconds'].mean()
print(avg_time_by_approach)
```

#### **3. User Satisfaction Analysis**
```python
satisfaction = runs[runs['metrics.user_rating'].notna()]
satisfaction_by_approach = satisfaction.groupby('params.approach')['metrics.user_rating'].mean()
print(satisfaction_by_approach)
```

---

## 🔍 Monitoring & Alerting

### **Performance Thresholds**
Monitor these key indicators:
- **Success Rate** < 90% → Investigate system issues
- **Average Response Time** > 10 seconds → Performance optimization needed
- **User Satisfaction** < 70% → Query quality improvement required

### **Daily Monitoring Routine**
```bash
# 1. Export daily data
python mlflow_config.py export daily_report_$(date +%Y%m%d).csv

# 2. Check MLflow UI for anomalies
python mlflow_config.py ui

# 3. Review user feedback comments
# Check MLflow UI → Experiments → Recent runs → User comments
```

### **Weekly Analysis**
1. **Approach Performance**: Compare Pattern Match vs AI-Powered vs AutoGen
2. **Query Patterns**: Identify most common questions and success rates
3. **User Feedback**: Review comments for improvement opportunities
4. **System Optimization**: Adjust thresholds and improve underperforming approaches

---

## 🛠 Configuration Options

### **Environment Variables**
```bash
# MLflow tracking URI (default: ./mlflow_tracking)
export MLFLOW_TRACKING_URI="sqlite:///mlflow.db"

# Or use remote tracking server
export MLFLOW_TRACKING_URI="http://mlflow-server:5000"
```

### **Retention Policy**
```bash
# Cleanup runs older than 90 days
python mlflow_config.py cleanup 90
```

### **Custom Experiment Names**
Modify `mlflow_tracking.py`:
```python
# Change experiment name
tracker = Text2SQLMLflowTracker(experiment_name="Your_Custom_Experiment")
```

---

## 📊 Sample Analytics Workflow

### **1. Daily Performance Check**
```python
from mlflow_tracking import get_tracker

tracker = get_tracker()
stats = tracker.get_experiment_stats()

print(f"Total queries today: {stats['total_runs']}")
print(f"Success rate: {stats['successful_runs']/stats['total_runs']*100:.1f}%")
print(f"Average response time: {stats['average_execution_time']:.2f}s")
print(f"User satisfaction: {stats.get('average_user_rating', 0)*100:.1f}%")
```

### **2. Weekly Quality Review**
```python
import mlflow
import pandas as pd
from datetime import datetime, timedelta

# Get runs from last 7 days
week_ago = datetime.now() - timedelta(days=7)
filter_string = f"start_time >= {int(week_ago.timestamp() * 1000)}"

runs = mlflow.search_runs(filter_string=filter_string)
print(f"Queries this week: {len(runs)}")

# Analyze feedback
feedback_runs = runs[runs['metrics.user_rating'].notna()]
positive_feedback = len(feedback_runs[feedback_runs['metrics.user_rating'] == 1])
print(f"Positive feedback: {positive_feedback}/{len(feedback_runs)}")

# Review comments
comments = feedback_runs['params.user_comment'].dropna()
print("\nUser Comments:")
for comment in comments[-5:]:  # Last 5 comments
    print(f"- {comment}")
```

### **3. Model Performance Comparison**
```python
# Compare approaches
approach_stats = runs.groupby('params.approach').agg({
    'metrics.success': 'mean',
    'metrics.execution_time_seconds': 'mean',
    'metrics.user_rating': 'mean'
}).round(3)

print("Approach Performance:")
print(approach_stats)
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **1. MLflow Database Lock**
```bash
# If SQLite database is locked
rm ./mlflow_tracking/mlflow.db-wal
rm ./mlflow_tracking/mlflow.db-shm
```

#### **2. Missing Feedback UI**
- Ensure `render_feedback_ui()` is called after `display_unified_results()`
- Check that `run_id` is properly generated and passed

#### **3. Statistics Not Updating**
- Restart Streamlit application: `streamlit run unified_text2sql_streamlit.py`
- Clear Streamlit cache: Delete `.streamlit` folder

### **Logging Debug Information**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run application with debug logging
streamlit run unified_text2sql_streamlit.py
```

---

## 🎯 Best Practices

### **1. User Feedback Strategy**
- **Encourage Feedback**: Explain how feedback improves the system
- **Make it Easy**: Simple thumbs up/down with optional comments
- **Follow Up**: Use feedback to improve query patterns and responses

### **2. Performance Optimization**
- **Monitor Trends**: Weekly analysis of response times and success rates
- **A/B Testing**: Compare different approaches for similar questions
- **Continuous Improvement**: Use feedback to refine SQL generation logic

### **3. Data Quality**
- **Regular Exports**: Weekly CSV exports for external analysis
- **Anomaly Detection**: Alert on unusual patterns or performance drops
- **User Education**: Share insights with business users to improve question quality

---

## 📈 Future Enhancements

### **Planned Features**
1. **Automated Model Retraining**: Use feedback to improve AI models
2. **Advanced Analytics**: Predictive analysis and pattern recognition
3. **Integration with BI Tools**: Export to Power BI, Tableau
4. **Real-time Alerts**: Slack/Email notifications for system issues
5. **A/B Testing Framework**: Systematic approach comparison
6. **Natural Language Feedback Analysis**: Sentiment analysis of comments

### **Contributing**
- Submit feedback and suggestions
- Report issues and performance problems
- Contribute to experiment analysis and optimization

---

## 📞 Support

For questions or issues with MLOps features:
1. Check MLflow UI for experiment details
2. Review logs in `./mlflow_tracking/` directory  
3. Export data for external analysis
4. Contact the development team with specific use cases

**MLflow UI**: http://localhost:5000 (when running `python mlflow_config.py ui`)
**Streamlit App**: http://localhost:8503 (when running `streamlit run unified_text2sql_streamlit.py`)

---

This MLOps integration transforms the FIS Banking Text2SQL system from a simple query tool into a comprehensive, learning system that continuously improves through user feedback and performance monitoring.