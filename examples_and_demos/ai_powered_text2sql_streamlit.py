#!/usr/bin/env python
"""
AI-Powered Text2SQL Streamlit App for FIS Banking
Uses Azure OpenAI for intelligent SQL generation from natural language
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
import openai
from openai import AsyncAzureOpenAI
import re

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
    page_title="🤖 AI-Powered FIS Banking Text2SQL",
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
def initialize_openai_client():
    """Initialize Azure OpenAI client"""
    try:
        client = AsyncAzureOpenAI(
            azure_endpoint=os.getenv('OpenAI__Endpoint'),
            api_key=os.getenv('OpenAI__ApiKey'),
            api_version="2024-02-01"
        )
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Azure OpenAI: {e}")
        return None

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

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_database_schema():
    """Get detailed database schema for AI context"""
    try:
        db_path = os.getenv('Text2Sql__Sqlite__Database')
        if not db_path or not os.path.exists(db_path):
            return None
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        schema_info = {}
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get sample data for context
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()
            
            schema_info[table_name] = {
                'columns': [{'name': col[1], 'type': col[2], 'nullable': not col[3]} for col in columns],
                'sample_data': sample_data[:2],  # Just 2 rows for context
                'column_names': [col[1] for col in columns]
            }
        
        conn.close()
        return schema_info
    except Exception as e:
        logger.error(f"Failed to get database schema: {e}")
        return None

def create_schema_context(schema_info):
    """Create a comprehensive schema context for the AI"""
    if not schema_info:
        return "No schema information available."
    
    context = "DATABASE SCHEMA FOR FIS BANKING SYSTEM:\n\n"
    
    # Key tables description
    table_descriptions = {
        'CUSTOMER_DIMENSION': 'Contains customer information including names, risk ratings, and industry codes',
        'CL_DETAIL_FACT': 'Contains loan details including current balances, original amounts, and loan keys',
        'LOAN_PRODUCT_DIMENSION': 'Contains loan product information and descriptions',
        'BRANCH_DIMENSION': 'Contains branch information and codes',
        'OFFICER_DIMENSION': 'Contains loan officer information',
        'DATE_DIMENSION': 'Contains date information for temporal analysis',
    }
    
    for table_name, table_data in schema_info.items():
        description = table_descriptions.get(table_name, 'Banking data table')
        context += f"TABLE: {table_name}\n"
        context += f"Description: {description}\n"
        context += f"Columns: {', '.join([f'{col["name"]} ({col["type"]})' for col in table_data['columns']])}\n"
        
        # Add key column insights
        if table_name == 'CUSTOMER_DIMENSION':
            context += "Key columns: CUSTOMER_KEY (primary key), CUSTOMER_NAME, OFFICER_RISK_RATING_DESC (risk levels), PRIMARY_INDUSTRY_CODE\n"
        elif table_name == 'CL_DETAIL_FACT':
            context += "Key columns: CUSTOMER_KEY (foreign key), CURRENT_PRINCIPAL_BALANCE (current loan amount), ORIGINAL_BALANCE, PAST_DUE_AMOUNT\n"
        
        context += "\n"
    
    context += """
IMPORTANT RELATIONSHIPS:
- CUSTOMER_DIMENSION.CUSTOMER_KEY = CL_DETAIL_FACT.CUSTOMER_KEY (join customers with their loans)
- Use CURRENT_PRINCIPAL_BALANCE > 0 for active loans
- OFFICER_RISK_RATING_DESC contains risk levels: 'PASS', 'SPECIAL MENTION', 'SUBSTANDARD', 'DOUBTFUL', 'LOSS'
- Higher risk ratings (SUBSTANDARD, DOUBTFUL, LOSS) indicate higher delinquency probability

DELINQUENCY ANALYSIS GUIDELINES:
- Past due amounts: Use PAST_DUE_AMOUNT > 0
- High risk customers: OFFICER_RISK_RATING_DESC IN ('SUBSTANDARD', 'DOUBTFUL', 'LOSS')  
- Large exposures: High CURRENT_PRINCIPAL_BALANCE relative to ORIGINAL_BALANCE ratios
"""
    
    return context

async def generate_sql_with_ai(question, schema_context, client):
    """Generate SQL using Azure OpenAI"""
    try:
        system_prompt = f"""You are an expert SQL analyst for a banking system. Generate precise SQL queries based on natural language questions.

{schema_context}

RULES:
1. Generate only valid SQLite syntax
2. Use appropriate JOINs when accessing multiple tables
3. Include meaningful column aliases
4. Use WHERE clauses to filter for relevant data
5. For delinquency analysis, consider risk ratings and past due amounts
6. Order results by relevance (highest risk, largest amounts, etc.)
7. Limit results to reasonable numbers (10-20 rows unless specifically asked)
8. NEVER use functions or syntax not supported by SQLite

RESPONSE FORMAT:
Return ONLY the SQL query, no explanations or comments."""

        user_prompt = f"""Question: {question}

Generate a SQL query to answer this question using the FIS banking database schema provided."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the SQL query
        sql_query = re.sub(r'^```sql\s*', '', sql_query)
        sql_query = re.sub(r'^```\s*', '', sql_query)
        sql_query = re.sub(r'\s*```$', '', sql_query)
        sql_query = sql_query.strip()
        
        return sql_query
        
    except Exception as e:
        logger.error(f"AI SQL generation failed: {e}")
        return None

async def process_natural_language_query(question, db_connector, openai_client, schema_info):
    """Process natural language query using AI-powered SQL generation"""
    try:
        # Create schema context
        schema_context = create_schema_context(schema_info)
        
        # Generate SQL using AI
        sql_query = await generate_sql_with_ai(question, schema_context, openai_client)
        
        if not sql_query:
            return {
                'sql_query': None,
                'results': None,
                'success': False,
                'error': 'Failed to generate SQL query'
            }
        
        # Execute the query
        result = await db_connector.query_execution(sql_query)
        
        return {
            'sql_query': sql_query,
            'results': result,
            'success': True,
            'explanation': f"AI-generated SQL query for: '{question}'"
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
    
    st.success("✅ AI-generated SQL query executed successfully!")
    
    # Show SQL query
    with st.expander("🤖 AI-Generated SQL Query", expanded=True):
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
                st.metric(col_name.replace('_', ' ').title(), f"{value:,}" if isinstance(value, (int, float)) else value)
            else:
                # Format numeric columns
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        # Check if it's a monetary value
                        if 'balance' in col.lower() or 'amount' in col.lower():
                            df[col] = df[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)
                        else:
                            df[col] = df[col].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
                
                st.dataframe(df, use_container_width=True)
                
                # Show summary stats
                st.caption(f"📈 {len(df)} rows returned")
                
                # Add insights for delinquency-related queries
                if 'risk' in response['sql_query'].lower() or 'delinq' in response['sql_query'].lower() or 'past_due' in response['sql_query'].lower():
                    st.info("💡 **Insight**: This analysis shows loan delinquency risk factors. Higher risk ratings and past due amounts indicate increased probability of default.")
        else:
            st.info("No results found")
    else:
        st.warning("No data returned")

def main():
    """Main application"""
    
    # Header
    st.title("🤖 AI-Powered FIS Banking Text2SQL")
    st.markdown("**Ask complex banking questions in natural language - powered by Azure OpenAI**")
    
    # Initialize systems
    with st.spinner("🔧 Initializing AI-powered Text2SQL system..."):
        openai_client = initialize_openai_client()
        db_connector = initialize_text2sql_system()
        schema_info = get_database_schema()
    
    if not openai_client or not db_connector or not schema_info:
        st.error("❌ Cannot initialize AI system. Please check configuration.")
        st.stop()
    
    # Sidebar with database info
    with st.sidebar:
        st.header("📊 Banking Database")
        
        st.metric("🏦 Tables", len(schema_info))
        total_columns = sum(len(table['columns']) for table in schema_info.values())
        st.metric("📊 Total Columns", total_columns)
        
        # Key tables
        st.subheader("🔑 Key Tables")
        key_tables = ['CUSTOMER_DIMENSION', 'CL_DETAIL_FACT', 'LOAN_PRODUCT_DIMENSION']
        for table in key_tables:
            if table in schema_info:
                with st.expander(f"{table}"):
                    cols = [col['name'] for col in schema_info[table]['columns'][:5]]
                    st.write("**Sample Columns:**")
                    for col in cols:
                        st.write(f"• {col}")
        
        # AI Status
        st.markdown("---")
        st.subheader("🤖 AI Status")
        st.write("🟢 Azure OpenAI: Connected")
        st.write("🟢 Database: Connected")
        st.write("🟢 Schema: Loaded")
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Ask Your Banking Question")
        
        # Example questions
        example_questions = [
            "",  # Empty option
            "Which loans are most likely to go delinquent?",
            "Show me customers with the highest risk ratings and their loan exposures",
            "What is the average loan balance by industry?",
            "Which customers have past due amounts greater than $10,000?",
            "Show me the distribution of loans by risk rating",
            "Which loan officers have the highest risk portfolios?",
            "What percentage of our loan portfolio is considered high risk?",
            "Show me customers whose current balance is significantly lower than original balance",
            "Which industries have the most customers in default risk categories?"
        ]
        
        # Question input
        selected_question = st.selectbox(
            "Select an example question:",
            example_questions,
            index=0
        )
        
        custom_question = st.text_area(
            "Or ask your own complex banking question:",
            height=100,
            placeholder="e.g., Which customers in the technology industry have risk ratings above 'PASS' and loan balances over $500,000?"
        )
        
        # Determine final question
        final_question = custom_question.strip() if custom_question.strip() else selected_question
        
        # Query execution
        col_a, col_b = st.columns([1, 4])
        
        with col_a:
            execute_button = st.button("🤖 Ask AI", type="primary", disabled=not final_question)
        
        with col_b:
            if final_question:
                st.write(f"**Question:** {final_question}")
        
        # Process query
        if execute_button and final_question:
            start_time = datetime.now()
            
            with st.spinner("🤖 AI is analyzing your question and generating SQL..."):
                # Process the query
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response = loop.run_until_complete(
                        process_natural_language_query(final_question, db_connector, openai_client, schema_info)
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
            st.caption(f"⏱️ AI processing time: {processing_time:.2f} seconds")
    
    with col2:
        st.subheader("📈 Query History")
        
        if st.session_state.query_history:
            for i, query in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    st.write(f"**Q:** {query['question'][:80]}..." if len(query['question']) > 80 else f"**Q:** {query['question']}")
                    status = "✅" if query['success'] else "❌"
                    st.write(f"**Status:** {status}")
                    st.write(f"**Time:** {query['processing_time']:.2f}s")
                    st.write(f"**When:** {query['timestamp'].strftime('%H:%M:%S')}")
        else:
            st.info("No AI queries yet")
        
        # Performance metrics
        if st.session_state.query_history:
            st.markdown("---")
            st.subheader("📊 AI Performance")
            
            total_queries = len(st.session_state.query_history)
            successful_queries = sum(1 for q in st.session_state.query_history if q['success'])
            avg_time = sum(q['processing_time'] for q in st.session_state.query_history) / total_queries
            
            st.metric("AI Queries", total_queries)
            st.metric("Success Rate", f"{successful_queries/total_queries*100:.1f}%")
            st.metric("Avg AI Time", f"{avg_time:.2f}s")

    # Footer
    st.markdown("---")
    st.markdown("**🤖 AI-Powered FIS Banking Text2SQL** | Azure OpenAI + Document Intelligence | Complex Question Understanding")

if __name__ == "__main__":
    main()