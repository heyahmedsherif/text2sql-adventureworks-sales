#!/usr/bin/env python
"""
AutoGen Multi-Agent Text2SQL Streamlit App for FIS Banking
Uses the full AutoGen multi-agent system with query caching and advanced reasoning
"""
import streamlit as st
import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Add paths for the text2sql modules
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
autogen_path = Path(__file__).parent / "text_2_sql" / "autogen" / "src"
sys.path.insert(0, str(text_2_sql_path))
sys.path.insert(0, str(autogen_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🤖 AutoGen Multi-Agent Text2SQL",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'autogen_system' not in st.session_state:
    st.session_state.autogen_system = None
if 'cache_hits' not in st.session_state:
    st.session_state.cache_hits = 0
if 'cache_misses' not in st.session_state:
    st.session_state.cache_misses = 0

@st.cache_resource
def initialize_autogen_system():
    """Initialize the AutoGen multi-agent system"""
    try:
        from autogen_text_2_sql.autogen_text_2_sql import AutogenText2Sql
        
        # Initialize with caching enabled
        autogen_system = AutogenText2Sql(
            thread_id="streamlit_session",
            enable_cache=True,  # Enable query caching
            enable_column_value_store=True  # Enable enhanced column understanding
        )
        
        return autogen_system
        
    except Exception as e:
        logger.error(f"Failed to initialize AutoGen system: {e}")
        st.error(f"❌ Failed to initialize AutoGen: {e}")
        return None

def get_database_stats():
    """Get database statistics"""
    try:
        import sqlite3
        db_path = os.getenv('Text2Sql__Sqlite__Database')
        if not db_path or not os.path.exists(db_path):
            return None
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        total_rows = 0
        total_columns = 0
        table_info = {}
        
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
            
            table_info[table_name] = {
                'columns': column_count,
                'rows': row_count
            }
        
        conn.close()
        return {
            'total_tables': len(tables),
            'total_rows': total_rows,
            'total_columns': total_columns,
            'tables': table_info
        }
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return None

def parse_autogen_response(response):
    """Parse AutoGen response to extract SQL and results"""
    try:
        if isinstance(response, dict):
            # Look for answer and sources
            if 'answer' in response:
                answer = response['answer']
                sources = response.get('sources', [])
                
                # Extract SQL and results from sources
                sql_query = None
                results = []
                
                for source in sources:
                    if 'sql_query' in source:
                        sql_query = source['sql_query']
                    if 'sql_rows' in source:
                        results = source['sql_rows']
                
                return {
                    'success': True,
                    'answer': answer,
                    'sql_query': sql_query,
                    'results': results,
                    'sources': sources
                }
        
        # Fallback parsing
        response_text = str(response)
        return {
            'success': True,
            'answer': response_text,
            'sql_query': None,
            'results': None,
            'sources': []
        }
        
    except Exception as e:
        logger.error(f"Failed to parse AutoGen response: {e}")
        return {
            'success': False,
            'error': str(e),
            'answer': None,
            'sql_query': None,
            'results': None
        }

async def process_with_autogen(question, autogen_system):
    """Process question using AutoGen multi-agent system"""
    try:
        start_time = datetime.now()
        
        # Use AutoGen to process the question
        response = await autogen_system.query_database_async(question)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Parse the response
        parsed_response = parse_autogen_response(response)
        parsed_response['processing_time'] = processing_time
        
        # Check if this was a cache hit (faster response usually indicates cache hit)
        if processing_time < 2.0:
            st.session_state.cache_hits += 1
            parsed_response['cache_hit'] = True
        else:
            st.session_state.cache_misses += 1
            parsed_response['cache_hit'] = False
        
        return parsed_response
        
    except Exception as e:
        logger.error(f"AutoGen processing failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'answer': None,
            'sql_query': None,
            'results': None,
            'processing_time': 0,
            'cache_hit': False
        }

def display_autogen_results(response):
    """Display AutoGen multi-agent results"""
    if not response['success']:
        st.error(f"❌ AutoGen processing failed: {response.get('error', 'Unknown error')}")
        return
    
    # Show cache status
    cache_status = "🚀 Cache Hit" if response.get('cache_hit') else "🔄 AI Processing"
    st.success(f"✅ {cache_status} - Multi-agent analysis complete!")
    
    # Show the AI answer
    if response.get('answer'):
        st.subheader("🤖 AutoGen Multi-Agent Answer")
        st.write(response['answer'])
    
    # Show SQL query if available
    if response.get('sql_query'):
        with st.expander("🔧 Generated SQL Query", expanded=False):
            st.code(response['sql_query'], language='sql')
    
    # Show results if available
    if response.get('results'):
        st.subheader("📊 Query Results")
        
        try:
            import pandas as pd
            df = pd.DataFrame(response['results'])
            
            if len(df) > 0:
                # Format numeric columns
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        if 'balance' in col.lower() or 'amount' in col.lower():
                            df[col] = df[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)
                        else:
                            df[col] = df[col].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
                
                st.dataframe(df, use_container_width=True)
                st.caption(f"📈 {len(df)} rows returned by multi-agent system")
            else:
                st.info("No data returned")
        except Exception as e:
            st.write(response['results'])
    
    # Show agent sources
    if response.get('sources'):
        with st.expander("🔍 Multi-Agent Process Details", expanded=False):
            for i, source in enumerate(response['sources'], 1):
                st.write(f"**Agent {i} Output:**")
                if isinstance(source, dict):
                    for key, value in source.items():
                        if key != 'sql_rows':  # Don't show raw data twice
                            st.write(f"• {key}: {value}")
                else:
                    st.write(f"• {source}")
                st.write("---")

def main():
    """Main application"""
    
    # Header
    st.title("🤖 AutoGen Multi-Agent Text2SQL System")
    st.markdown("**Advanced multi-agent reasoning with query caching for FIS Banking**")
    
    # Initialize AutoGen system
    with st.spinner("🔧 Initializing AutoGen multi-agent system..."):
        autogen_system = initialize_autogen_system()
        db_stats = get_database_stats()
    
    if not autogen_system:
        st.error("❌ Cannot initialize AutoGen system. Please check configuration.")
        st.stop()
    
    # Sidebar with system info
    with st.sidebar:
        st.header("🤖 AutoGen System Status")
        
        st.write("✅ **Multi-Agent System**: Active")
        st.write("✅ **Query Cache**: Enabled") 
        st.write("✅ **Column Value Store**: Enabled")
        st.write("✅ **Schema Selection**: AI-Powered")
        
        # Cache statistics
        st.subheader("⚡ Cache Performance")
        total_queries = st.session_state.cache_hits + st.session_state.cache_misses
        if total_queries > 0:
            cache_rate = (st.session_state.cache_hits / total_queries) * 100
            st.metric("Cache Hit Rate", f"{cache_rate:.1f}%")
            st.metric("Cache Hits", st.session_state.cache_hits)
            st.metric("AI Processes", st.session_state.cache_misses)
        else:
            st.info("No queries processed yet")
        
        # Database info
        if db_stats:
            st.subheader("📊 Banking Database")
            st.metric("Tables", db_stats['total_tables'])
            st.metric("Total Records", f"{db_stats['total_rows']:,}")
            st.metric("Total Columns", db_stats['total_columns'])
            
            # Top tables by size
            st.subheader("📋 Largest Tables")
            sorted_tables = sorted(db_stats['tables'].items(), key=lambda x: x[1]['rows'], reverse=True)
            for table_name, info in sorted_tables[:5]:
                st.write(f"• {table_name}: {info['rows']:,} rows")
        
        # Agent Flow Info
        st.subheader("🔄 Agent Flow")
        st.write("""
        **7-Agent Process:**
        1. Query Rewrite Agent
        2. Cache Check Agent  
        3. Schema Selection Agent
        4. SQL Disambiguation Agent
        5. Query Generation Agent
        6. Query Correction Agent
        7. Answer Formatting Agent
        """)
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Ask Complex Banking Questions")
        st.info("💡 **Tip**: AutoGen agents will collaborate to understand complex questions and provide accurate SQL + insights!")
        
        # Advanced banking questions
        advanced_questions = [
            "",  # Empty option
            "Which loans are most likely to go delinquent based on risk factors?",
            "Show me a comprehensive analysis of our highest risk customers and their total exposure",
            "What are the early warning indicators for loan defaults in our portfolio?",
            "Compare loan performance across different industries and identify concerning trends",
            "Which customers have deteriorating loan-to-value ratios that might indicate problems?",
            "Analyze the correlation between past due amounts and final loan outcomes",
            "What percentage of loans in each risk category actually become problematic?",
            "Show me customers who started with good ratings but now have concerning patterns",
            "Identify geographic or industry concentrations that represent portfolio risks",
            "What is the typical progression from 'PASS' rating to higher risk categories?"
        ]
        
        # Question input
        selected_question = st.selectbox(
            "Select a complex banking question:",
            advanced_questions,
            index=0
        )
        
        custom_question = st.text_area(
            "Or ask your own complex question (AutoGen agents will collaborate):",
            height=120,
            placeholder="e.g., Perform a multi-dimensional risk analysis identifying customers with multiple warning signs: high risk ratings, increasing past due amounts, and declining industry performance."
        )
        
        # Determine final question
        final_question = custom_question.strip() if custom_question.strip() else selected_question
        
        # Query execution
        col_a, col_b = st.columns([1, 4])
        
        with col_a:
            execute_button = st.button("🤖 Launch Agents", type="primary", disabled=not final_question)
        
        with col_b:
            if final_question:
                st.write(f"**Question:** {final_question}")
        
        # Process query with AutoGen
        if execute_button and final_question:
            with st.spinner("🤖 Multi-agent system collaborating on your question..."):
                # Show agent progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                agent_steps = [
                    "Query Rewrite Agent analyzing question...",
                    "Cache Agent checking for similar questions...",
                    "Schema Selection Agent finding relevant tables...", 
                    "SQL Disambiguation Agent clarifying requirements...",
                    "Query Generation Agent creating SQL...",
                    "Query Correction Agent validating syntax...",
                    "Answer Formatting Agent preparing response..."
                ]
                
                # Simulate agent progress (AutoGen doesn't provide real-time updates)
                for i, step in enumerate(agent_steps):
                    status_text.text(step)
                    progress_bar.progress((i + 1) / len(agent_steps))
                    if i < len(agent_steps) - 1:  # Don't sleep on last step
                        asyncio.run(asyncio.sleep(0.5))
                
                # Process with AutoGen
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response = loop.run_until_complete(
                        process_with_autogen(final_question, autogen_system)
                    )
                finally:
                    loop.close()
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
            
            # Display results
            display_autogen_results(response)
            
            # Add to history
            st.session_state.query_history.append({
                'question': final_question,
                'response': response,
                'timestamp': datetime.now()
            })
            
            # Show processing details
            processing_time = response.get('processing_time', 0)
            cache_status = "Cache Hit" if response.get('cache_hit') else "AI Processing"
            st.caption(f"⏱️ {cache_status}: {processing_time:.2f} seconds | 🤖 7-Agent Collaboration")
    
    with col2:
        st.subheader("📈 Agent Activity")
        
        if st.session_state.query_history:
            for i, query in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    st.write(f"**Q:** {query['question'][:70]}..." if len(query['question']) > 70 else f"**Q:** {query['question']}")
                    
                    response = query['response']
                    status = "✅" if response['success'] else "❌"
                    cache_icon = "⚡" if response.get('cache_hit') else "🤖"
                    
                    st.write(f"**Status:** {status} {cache_icon}")
                    st.write(f"**Time:** {response.get('processing_time', 0):.2f}s")
                    st.write(f"**When:** {query['timestamp'].strftime('%H:%M:%S')}")
        else:
            st.info("No agent queries yet")
        
        # System performance
        if st.session_state.query_history:
            st.markdown("---")
            st.subheader("🔬 Agent Performance")
            
            total_queries = len(st.session_state.query_history)
            successful_queries = sum(1 for q in st.session_state.query_history if q['response']['success'])
            avg_time = sum(q['response'].get('processing_time', 0) for q in st.session_state.query_history) / total_queries
            
            st.metric("Total Queries", total_queries)
            st.metric("Success Rate", f"{successful_queries/total_queries*100:.1f}%")
            st.metric("Avg Response Time", f"{avg_time:.2f}s")

    # Footer
    st.markdown("---")
    st.markdown("""
    **🤖 AutoGen Multi-Agent Text2SQL System** | 
    7-Agent Collaboration | Query Caching | Schema Intelligence | 
    Powered by Azure OpenAI
    """)

if __name__ == "__main__":
    main()