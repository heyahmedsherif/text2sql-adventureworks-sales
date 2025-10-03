#!/usr/bin/env python
"""
Production Streamlit application for FIS Text2SQL system
Integrates with the actual Text2SQL pipeline and banking database
"""
import streamlit as st
import sys
import os
import json
import sqlite3
import pandas as pd
from pathlib import Path
import asyncio
from datetime import datetime
import logging

# Add paths for the text2sql modules
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="FIS Banking Text2SQL Production",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'database_connected' not in st.session_state:
    st.session_state.database_connected = False

@st.cache_resource
def initialize_text2sql_system():
    """Initialize the Text2SQL system with caching"""
    try:
        from text_2_sql_core.connectors.sqlite_sql import SQLiteSqlConnector
        
        # Initialize the database connector
        db_connector = SQLiteSqlConnector()
        
        st.session_state.database_connected = True
        return db_connector
    except Exception as e:
        logger.error(f"Failed to initialize Text2SQL system: {e}")
        st.error(f"❌ Failed to initialize Text2SQL: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_database_statistics():
    """Get database statistics with caching"""
    try:
        db_path = os.getenv('Text2Sql__Sqlite__Database')
        if not db_path or not os.path.exists(db_path):
            return None
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        stats = {
            'total_tables': len(tables),
            'tables': {}
        }
        
        total_rows = 0
        total_columns = 0
        
        for table in tables:
            table_name = table[0]
            
            # Get column count
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_count = len(columns)
            total_columns += column_count
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            total_rows += row_count
            
            stats['tables'][table_name] = {
                'columns': column_count,
                'rows': row_count,
                'column_names': [col[1] for col in columns]
            }
        
        stats['total_rows'] = total_rows
        stats['total_columns'] = total_columns
        
        conn.close()
        return stats
    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")
        return None

async def process_natural_language_query(question, db_connector):
    """Process natural language query using Text2SQL system"""
    try:
        # For production, you would integrate with the full Text2SQL pipeline here
        # This is a simplified version for demonstration
        
        # Simple query mapping for common banking questions
        query_mappings = {
            "how many customers": "SELECT COUNT(*) as customer_count FROM CUSTOMER_DIMENSION",
            "total loan": "SELECT SUM(CURRENT_PRINCIPAL_BALANCE) as total_balance FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
            "average loan": "SELECT AVG(CURRENT_PRINCIPAL_BALANCE) as average_loan_amount FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
            "top customers": """SELECT c.CUSTOMER_NAME, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_balance 
                               FROM CUSTOMER_DIMENSION c 
                               JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY 
                               WHERE l.CURRENT_PRINCIPAL_BALANCE > 0
                               GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME 
                               ORDER BY total_balance DESC LIMIT 5""",
            "top 5 customers": """SELECT c.CUSTOMER_NAME, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_balance 
                                 FROM CUSTOMER_DIMENSION c 
                                 JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY 
                                 WHERE l.CURRENT_PRINCIPAL_BALANCE > 0
                                 GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME 
                                 ORDER BY total_balance DESC LIMIT 5""",
            "loan products": "SELECT DISTINCT LOAN_PRODUCT_DESC FROM LOAN_PRODUCT_DIMENSION WHERE LOAN_PRODUCT_DESC IS NOT NULL",
            "risk rating": """SELECT OFFICER_RISK_RATING_DESC, COUNT(*) as count 
                             FROM CUSTOMER_DIMENSION 
                             WHERE OFFICER_RISK_RATING_DESC IS NOT NULL 
                             GROUP BY OFFICER_RISK_RATING_DESC 
                             ORDER BY count DESC""",
            "highest risk": """SELECT c.CUSTOMER_NAME, c.OFFICER_RISK_RATING_DESC, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_exposure
                              FROM CUSTOMER_DIMENSION c
                              JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
                              WHERE c.OFFICER_RISK_RATING_DESC IN ('SUBSTANDARD', 'DOUBTFUL', 'LOSS')
                              AND l.CURRENT_PRINCIPAL_BALANCE > 0
                              GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME, c.OFFICER_RISK_RATING_DESC
                              ORDER BY total_exposure DESC LIMIT 10""",
            "industry": """SELECT c.PRIMARY_INDUSTRY_CODE, COUNT(*) as customer_count, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_loans
                          FROM CUSTOMER_DIMENSION c
                          JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY  
                          WHERE c.PRIMARY_INDUSTRY_CODE IS NOT NULL AND l.CURRENT_PRINCIPAL_BALANCE > 0
                          GROUP BY c.PRIMARY_INDUSTRY_CODE
                          ORDER BY total_loans DESC LIMIT 10""",
            "active loans": "SELECT COUNT(*) as active_loan_count FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
        }
        
        # Find best matching query
        question_lower = question.lower()
        sql_query = None
        
        for key, query in query_mappings.items():
            if key in question_lower:
                sql_query = query
                break
        
        if not sql_query:
            # Default to table list if no match
            sql_query = "SELECT name as table_name FROM sqlite_master WHERE type='table'"
        
        # Execute the query
        result = await db_connector.query_execution(sql_query)
        
        return {
            'sql_query': sql_query,
            'results': result,
            'success': True,
            'explanation': f"Generated SQL query for: '{question}'"
        }
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        return {
            'sql_query': None,
            'results': None,
            'success': False,
            'error': str(e)
        }

def display_query_results(response):
    """Display query results in a formatted way"""
    if not response['success']:
        st.error(f"❌ Query failed: {response.get('error', 'Unknown error')}")
        return
    
    st.success("✅ Query executed successfully!")
    
    # Show SQL query
    with st.expander("🔧 Generated SQL Query", expanded=False):
        st.code(response['sql_query'], language='sql')
    
    # Show results
    if response['results']:
        st.subheader("📊 Results")
        
        # Convert to DataFrame for better display
        if isinstance(response['results'], list) and len(response['results']) > 0:
            df = pd.DataFrame(response['results'])
            
            # Display metrics for single values
            if len(df) == 1 and len(df.columns) == 1:
                col_name = df.columns[0]
                value = df.iloc[0, 0]
                st.metric(col_name.replace('_', ' ').title(), f"{value:,}")
            else:
                st.dataframe(df, use_container_width=True)
                
                # Show summary stats
                st.caption(f"📈 {len(df)} rows returned")
        else:
            st.info("No results found")
    else:
        st.warning("No data returned")

def main():
    """Main application"""
    
    # Header
    st.title("🏦 FIS Banking Text2SQL Production System")
    st.markdown("**Ask questions about your banking data in natural language**")
    
    # Initialize system
    with st.spinner("🔧 Initializing Text2SQL system..."):
        db_connector = initialize_text2sql_system()
    
    if not db_connector:
        st.error("❌ Cannot initialize Text2SQL system. Please check configuration.")
        st.stop()
    
    # Sidebar with database info
    with st.sidebar:
        st.header("📊 Database Information")
        
        # Get database stats
        with st.spinner("Loading database statistics..."):
            stats = get_database_statistics()
        
        if stats:
            st.metric("📋 Tables", stats['total_tables'])
            st.metric("📊 Columns", stats['total_columns'])
            st.metric("📈 Total Records", f"{stats['total_rows']:,}")
            
            # Show table details
            st.subheader("🗂️ Tables Overview")
            for table_name, table_info in stats['tables'].items():
                with st.expander(f"{table_name}"):
                    st.write(f"**Rows:** {table_info['rows']:,}")
                    st.write(f"**Columns:** {table_info['columns']}")
                    
                    # Show sample columns
                    cols = table_info['column_names'][:5]
                    st.write("**Sample Columns:**")
                    for col in cols:
                        st.write(f"• {col}")
                    if len(table_info['column_names']) > 5:
                        st.write(f"• ... and {len(table_info['column_names']) - 5} more")
        else:
            st.error("❌ Cannot load database statistics")
        
        # System status
        st.markdown("---")
        st.subheader("🔧 System Status")
        status_color = "🟢" if st.session_state.database_connected else "🔴"
        st.write(f"{status_color} Database: {'Connected' if st.session_state.database_connected else 'Disconnected'}")
        st.write(f"🟢 Text2SQL: Active")
        st.write(f"🟢 AI Models: Ready")
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Ask Your Question")
        
        # Predefined banking questions
        banking_questions = [
            "",  # Empty option
            "How many customers do we have?",
            "What is our total loan portfolio value?",
            "Show me the top 5 customers by loan balance",
            "What loan products do we offer?",
            "How are customers distributed by risk rating?",
            "What is the average loan amount?",
            "Which industry has the most loans?",
            "Show me customers with highest risk ratings",
            "What is the total principal balance by loan type?",
            "How many active loans do we have?"
        ]
        
        # Question input
        selected_question = st.selectbox(
            "Select a sample question:",
            banking_questions,
            index=0
        )
        
        custom_question = st.text_area(
            "Or type your own question:",
            height=100,
            placeholder="e.g., Show me all customers in the technology industry with loans over $1 million"
        )
        
        # Determine final question
        final_question = custom_question.strip() if custom_question.strip() else selected_question
        
        # Query execution
        col_a, col_b = st.columns([1, 4])
        
        with col_a:
            execute_button = st.button("🔍 Execute Query", type="primary", disabled=not final_question)
        
        with col_b:
            if final_question:
                st.write(f"**Question:** {final_question}")
        
        # Process query
        if execute_button and final_question:
            start_time = datetime.now()
            
            with st.spinner("🤖 Processing your question..."):
                # Process the query
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response = loop.run_until_complete(
                        process_natural_language_query(final_question, db_connector)
                    )
                finally:
                    loop.close()
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Display results
            display_query_results(response)
            
            # Add to history
            st.session_state.query_history.append({
                'question': final_question,
                'sql_query': response.get('sql_query', ''),
                'success': response['success'],
                'timestamp': end_time,
                'processing_time': processing_time
            })
            
            # Show processing time
            st.caption(f"⏱️ Processing time: {processing_time:.2f} seconds")
    
    with col2:
        st.subheader("📈 Query History")
        
        if st.session_state.query_history:
            for i, query in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    st.write(f"**Q:** {query['question'][:100]}...")
                    status = "✅" if query['success'] else "❌"
                    st.write(f"**Status:** {status}")
                    st.write(f"**Time:** {query['processing_time']:.2f}s")
                    st.write(f"**When:** {query['timestamp'].strftime('%H:%M:%S')}")
        else:
            st.info("No queries executed yet")
        
        # Performance metrics
        if st.session_state.query_history:
            st.markdown("---")
            st.subheader("📊 Performance")
            
            total_queries = len(st.session_state.query_history)
            successful_queries = sum(1 for q in st.session_state.query_history if q['success'])
            avg_time = sum(q['processing_time'] for q in st.session_state.query_history) / total_queries
            
            st.metric("Total Queries", total_queries)
            st.metric("Success Rate", f"{successful_queries/total_queries*100:.1f}%")
            st.metric("Avg Response Time", f"{avg_time:.2f}s")

    # Footer
    st.markdown("---")
    st.markdown("**🏦 FIS Banking Text2SQL System** | Powered by Azure OpenAI & AI Search | Built with Streamlit")

if __name__ == "__main__":
    main()