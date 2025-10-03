#!/usr/bin/env python
"""
Unified Text2SQL Streamlit App - Powered by Claude AI
Combines pattern matching, Claude AI-powered SQL generation, and AutoGen multi-agent system
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
import re
import time
import uuid

# Import MLflow tracking
from mlflow_tracking import get_tracker, render_mlflow_stats

# Add paths for the text2sql modules
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
autogen_path = Path(__file__).parent / "text_2_sql" / "autogen" / "src"
sys.path.insert(0, str(text_2_sql_path))
sys.path.insert(0, str(autogen_path))

from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv("text_2_sql/.env")

# Load Streamlit Cloud secrets into environment variables
# This allows the app to work seamlessly in both local and cloud environments
if hasattr(st, 'secrets') and len(st.secrets) > 0:
    for key, value in st.secrets.items():
        os.environ[key] = str(value)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🤖 Text2SQL with Claude AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "processing_mode" not in st.session_state:
    st.session_state.processing_mode = "Smart Auto"
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "current_run_id" not in st.session_state:
    st.session_state.current_run_id = None
if "mlflow_tracker" not in st.session_state:
    st.session_state.mlflow_tracker = get_tracker()


@st.cache_resource
def initialize_systems():
    """Initialize all Text2SQL systems"""
    systems = {
        "db_connector": None,
        "llm_client": None,
        "llm_provider": None,
        "autogen_system": None,
        "schema_info": None,
    }

    # Initialize database connector
    try:
        from text_2_sql_core.connectors.sqlite_sql import SQLiteSqlConnector

        systems["db_connector"] = SQLiteSqlConnector()
    except Exception as e:
        logger.error(f"Database connector failed: {e}")

    # Initialize LLM client (Claude or OpenAI based on LLM_PROVIDER)
    try:
        provider = os.getenv("LLM_PROVIDER", "claude").lower()

        if provider in ["claude", "anthropic"]:
            from anthropic import AsyncAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
            systems["llm_client"] = AsyncAnthropic(api_key=api_key)
            systems["llm_provider"] = "claude"
        else:
            from openai import AsyncOpenAI
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OpenAI__ApiKey")
            systems["llm_client"] = AsyncOpenAI(api_key=api_key)
            systems["llm_provider"] = "openai"
    except Exception as e:
        logger.error(f"LLM client failed: {e}")
        systems["llm_client"] = None
        systems["llm_provider"] = None

    # Initialize AutoGen system (with error handling)
    try:
        from autogen_text_2_sql.autogen_text_2_sql import AutoGenText2Sql
        from autogen_text_2_sql.state_store import InMemoryStateStore

        state_store = InMemoryStateStore()
        systems["autogen_system"] = AutoGenText2Sql(
            state_store=state_store,
            thread_id="streamlit_session",
            enable_cache=True,
            enable_column_value_store=True,
        )
    except Exception as e:
        logger.warning(f"AutoGen system not available: {e}")
        systems["autogen_system"] = None

    # Get database schema
    systems["schema_info"] = get_database_schema()

    return systems


@st.cache_data(ttl=600)
def get_database_schema():
    """Get detailed database schema"""
    try:
        db_path = os.getenv("Text2Sql__Sqlite__Database")
        if not db_path or not os.path.exists(db_path):
            return None

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        schema_info = {}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            schema_info[table_name] = {
                "columns": [{"name": col[1], "type": col[2]} for col in columns],
                "row_count": row_count,
                "column_names": [col[1] for col in columns],
            }

        conn.close()
        return schema_info
    except Exception as e:
        logger.error(f"Failed to get database schema: {e}")
        return None


# Pattern matching queries (Fast approach) - AdventureWorks schema
PATTERN_QUERIES = {
    "how many customers": "SELECT COUNT(*) as customer_count FROM Customer",
    "total customers": "SELECT COUNT(*) as customer_count FROM Customer",
    "how many products": "SELECT COUNT(*) as product_count FROM Product",
    "total products": "SELECT COUNT(*) as product_count FROM Product",
    "how many orders": "SELECT COUNT(*) as order_count FROM SalesOrderHeader",
    "total orders": "SELECT COUNT(*) as order_count FROM SalesOrderHeader",
    "total sales": "SELECT SUM(TotalDue) as total_sales FROM SalesOrderHeader",
    "average order": "SELECT AVG(TotalDue) as average_order_value FROM SalesOrderHeader",
    "top customers": """SELECT c.FirstName || ' ' || c.LastName as CustomerName, SUM(s.TotalDue) as TotalSales
                       FROM Customer c
                       JOIN SalesOrderHeader s ON c.CustomerID = s.CustomerID
                       GROUP BY c.CustomerID, CustomerName
                       ORDER BY TotalSales DESC LIMIT 10""",
    "top products": """SELECT p.Name, COUNT(sod.SalesOrderDetailID) as TimesSold, SUM(sod.LineTotal) as TotalRevenue
                      FROM Product p
                      JOIN SalesOrderDetail sod ON p.ProductID = sod.ProductID
                      GROUP BY p.ProductID, p.Name
                      ORDER BY TotalRevenue DESC LIMIT 10""",
    "product categories": """SELECT pc.Name as Category, COUNT(p.ProductID) as ProductCount
                            FROM ProductCategory pc
                            LEFT JOIN Product p ON pc.ProductCategoryID = p.ProductCategoryID
                            GROUP BY pc.ProductCategoryID, pc.Name
                            ORDER BY ProductCount DESC""",
    "recent orders": """SELECT SalesOrderID, OrderDate, TotalDue, Status
                       FROM SalesOrderHeader
                       ORDER BY OrderDate DESC LIMIT 10""",
}


def detect_processing_mode(question):
    """Determine the best processing mode for the question"""
    question_lower = question.lower()

    # Check for pattern match
    for pattern in PATTERN_QUERIES.keys():
        if pattern in question_lower:
            return "Pattern Match"

    # Check complexity indicators for AutoGen
    complex_indicators = [
        "analysis",
        "compare",
        "correlation",
        "trend",
        "comprehensive",
        "multi-dimensional",
        "progression",
        "deteriorating",
        "concerning patterns",
        "early warning",
        "multiple warning signs",
    ]

    if any(indicator in question_lower for indicator in complex_indicators):
        return "AutoGen Multi-Agent"

    return "AI-Powered"


async def process_pattern_match(question, db_connector):
    """Process using pattern matching (fastest)"""
    question_lower = question.lower()

    for pattern, sql_query in PATTERN_QUERIES.items():
        if pattern in question_lower:
            try:
                result = await db_connector.query_execution(sql_query)
                return {
                    "method": "Pattern Match",
                    "sql_query": sql_query,
                    "results": result,
                    "success": True,
                    "explanation": f"Matched pattern '{pattern}'",
                }
            except Exception as e:
                return {
                    "method": "Pattern Match",
                    "sql_query": sql_query,
                    "results": None,
                    "success": False,
                    "error": str(e),
                }

    return None


async def process_ai_powered(question, db_connector, llm_client, llm_provider, schema_info):
    """Process using AI SQL generation (Claude or OpenAI)"""
    try:
        # Create schema context
        schema_context = create_schema_context(schema_info)

        system_prompt = f"""You are an expert SQL analyst. Generate precise SQL queries for the AdventureWorks sales database.

{schema_context}

IMPORTANT NOTES:
- This is AdventureWorks, a sales/retail database (NOT a banking/loan database)
- For questions about "portfolio" or "loans", interpret them as sales/revenue questions
- Use SUM(TotalDue) or SUM(SubTotal) from SalesOrderHeader for total sales/revenue
- Use COUNT(*) on Customer for customer counts
- Use Product table for product information

RULES:
1. Generate only valid SQLite syntax
2. Use appropriate JOINs when accessing multiple tables
3. Order results by relevance (highest values, most recent, etc.)
4. Limit results to reasonable numbers (10-20 rows)
5. Use proper column names as they exist in the schema above
6. Table names are case-sensitive: Customer, Product, SalesOrderHeader, etc.

Return ONLY the SQL query, no explanations or markdown formatting."""

        user_prompt = f"Question: {question}"

        # Use Claude or OpenAI based on provider
        if llm_provider == "claude":
            response = await llm_client.messages.create(
                model=os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"),
                max_tokens=1000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            sql_query = response.content[0].text.strip()
        else:
            # OpenAI
            response = await llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=500,
            )
            sql_query = response.choices[0].message.content.strip()

        # Clean up SQL query
        sql_query = re.sub(r"^```sql\s*", "", sql_query)
        sql_query = re.sub(r"^```\s*", "", sql_query)
        sql_query = re.sub(r"\s*```$", "", sql_query)
        sql_query = sql_query.strip()

        # Execute the query
        result = await db_connector.query_execution(sql_query)

        return {
            "method": f"AI-Powered ({llm_provider.upper()})",
            "sql_query": sql_query,
            "results": result,
            "success": True,
            "explanation": f"AI-generated SQL using {llm_provider.upper()}: '{question}'",
        }

    except Exception as e:
        logger.error(f"AI processing failed: {e}")
        return {
            "method": "AI-Powered",
            "sql_query": None,
            "results": None,
            "success": False,
            "error": str(e),
        }


def process_autogen_sync(question):
    """Synchronous wrapper for AutoGen multi-agent system - creates fresh system in isolated thread"""
    import asyncio
    import os
    import sys
    from pathlib import Path
    from dotenv import load_dotenv
    from text_2_sql_core.payloads.interaction_payloads import UserMessagePayload

    # Reload environment variables in the new thread
    load_dotenv("text_2_sql/.env")

    # Verify key environment variables are loaded
    logger.info(f"Thread ENV - SPIDER_DATA_DIR: {os.getenv('SPIDER_DATA_DIR')}")
    logger.info(
        f"Thread ENV - Text2Sql__DatabaseEngine: {os.getenv('Text2Sql__DatabaseEngine')}"
    )
    logger.info(
        f"Thread ENV - Text2Sql__Sqlite__Database: {os.getenv('Text2Sql__Sqlite__Database')}"
    )

    async def run_autogen():
        try:
            # Create a fresh AutoGen system in this thread to avoid event loop conflicts
            text_2_sql_path = Path("text_2_sql/text_2_sql_core/src")
            autogen_path = Path("text_2_sql/autogen/src")

            if str(text_2_sql_path) not in sys.path:
                sys.path.insert(0, str(text_2_sql_path))
            if str(autogen_path) not in sys.path:
                sys.path.insert(0, str(autogen_path))

            from autogen_text_2_sql.autogen_text_2_sql import AutoGenText2Sql
            from autogen_text_2_sql.state_store import InMemoryStateStore

            # Create a new AutoGen system instance in this thread with proper state store
            state_store = InMemoryStateStore()
            fresh_autogen_system = AutoGenText2Sql(
                state_store=state_store,
                thread_id="autogen_thread",
                use_case="Banking and financial data analysis",
                enable_cache=True,
                enable_column_value_store=True,
            )

            # Create the user message payload
            payload = UserMessagePayload(user_message=question, injected_parameters={})

            # Process the message using the correct method
            response_data = None
            async for response_payload in fresh_autogen_system.process_user_message(
                "thread_1", payload
            ):
                if (
                    hasattr(response_payload, "payload_type")
                    and response_payload.payload_type.value != "processing_update"
                ):
                    response_data = response_payload
                    break

            if not response_data:
                return {
                    "method": "AutoGen Multi-Agent",
                    "success": False,
                    "error": "No response received from AutoGen system",
                }

            # Parse AutoGen response based on payload type
            response_type = response_data.payload_type.value if hasattr(response_data, 'payload_type') else 'unknown'
            
            # Handle disambiguation requests (user choices)
            if response_type == 'disambiguation_requests':
                disambiguation_requests = getattr(response_data.body, 'disambiguation_requests', [])
                
                # Extract user choices and questions
                user_choices = []
                clarification_questions = []
                
                for req in disambiguation_requests:
                    if hasattr(req, 'assistant_question') and req.assistant_question:
                        clarification_questions.append(req.assistant_question)
                    if hasattr(req, 'user_choices') and req.user_choices:
                        user_choices.extend(req.user_choices)
                
                return {
                    "method": "AutoGen Multi-Agent",
                    "response_type": "disambiguation",
                    "clarification_questions": clarification_questions,
                    "user_choices": user_choices,
                    "success": True,
                    "explanation": "AutoGen is requesting clarification to provide better analysis",
                }
            
            # Handle answer with sources (normal response)
            elif response_type == 'answer_with_sources' or hasattr(response_data, "body"):
                sources = (
                    getattr(response_data.body, "sources", [])
                    if hasattr(response_data, "body")
                    else []
                )
                sql_query = None
                results = []

                for source in sources:
                    if hasattr(source, "sql_query"):
                        sql_query = source.sql_query
                    if hasattr(source, "sql_rows"):
                        results = source.sql_rows

                # Check for follow-up suggestions
                follow_up_suggestions = []
                if hasattr(response_data.body, 'follow_up_suggestions'):
                    follow_up_suggestions = response_data.body.follow_up_suggestions

                # Get answer safely
                answer = getattr(response_data, 'answer', None) or getattr(response_data.body, 'answer', 'Analysis completed successfully')

                return {
                    "method": "AutoGen Multi-Agent",
                    "response_type": "answer",
                    "answer": answer,
                    "sql_query": sql_query,
                    "results": results,
                    "follow_up_suggestions": follow_up_suggestions,
                    "sources": (
                        [
                            {"sql_query": s.sql_query, "sql_rows": s.sql_rows}
                            for s in sources
                        ]
                        if sources
                        else []
                    ),
                    "success": True,
                    "explanation": "AutoGen multi-agent processing completed",
                }

            return {
                "method": "AutoGen Multi-Agent",
                "response_type": "unknown",
                "answer": str(response_data),
                "sql_query": None,
                "results": None,
                "success": True,
                "explanation": f"AutoGen processing completed (type: {response_type})",
            }

        except Exception as e:
            logger.error(f"AutoGen processing failed: {e}")
            import traceback

            logger.error(f"AutoGen traceback: {traceback.format_exc()}")
            return {
                "method": "AutoGen Multi-Agent",
                "success": False,
                "error": f"AutoGen processing failed: {str(e)}",
            }

    # Run in a new event loop in the current thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(run_autogen())
        return result
    finally:
        loop.close()


async def process_autogen(question, autogen_system):
    """Process using AutoGen multi-agent system - thread-safe wrapper"""
    import concurrent.futures
    import threading

    try:
        # Run AutoGen in a separate thread to avoid event loop conflicts
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(process_autogen_sync, question)
            result = future.result(timeout=120)  # 2 minute timeout
            return result

    except Exception as e:
        logger.error(f"AutoGen processing failed: {e}")
        return {"method": "AutoGen Multi-Agent", "success": False, "error": str(e)}


def create_schema_context(schema_info):
    """Create schema context for AI"""
    if not schema_info:
        return "No schema information available."

    context = "ADVENTUREWORKS DATABASE SCHEMA:\n\n"

    # AdventureWorks table descriptions
    table_descriptions = {
        "Customer": "Customer information: names, contact details",
        "Product": "Product catalog: names, categories, prices",
        "SalesOrderHeader": "Sales orders: totals, dates, customer IDs, status",
        "SalesOrderDetail": "Order line items: products, quantities, prices",
        "ProductCategory": "Product categories and names",
        "Address": "Customer addresses",
        "CustomerAddress": "Links customers to addresses",
    }

    for table_name, table_data in schema_info.items():
        description = table_descriptions.get(table_name, "Data table")
        context += f"TABLE: {table_name}\n"
        context += f"Description: {description}\n"
        context += f"Columns: {', '.join([col['name'] for col in table_data['columns']])}\n\n"

    context += """
KEY RELATIONSHIPS:
- Customer.CustomerID = SalesOrderHeader.CustomerID
- SalesOrderHeader.SalesOrderID = SalesOrderDetail.SalesOrderID
- Product.ProductID = SalesOrderDetail.ProductID
- Product.ProductCategoryID = ProductCategory.ProductCategoryID
- Customer.CustomerID = CustomerAddress.CustomerID
- Address.AddressID = CustomerAddress.AddressID
"""
    return context


async def unified_query_processor(question, systems):
    """Main unified processing logic"""
    mode = st.session_state.processing_mode

    # Smart Auto mode - detect best approach
    if mode == "Smart Auto":
        mode = detect_processing_mode(question)
        st.info(f"🤖 Auto-selected: **{mode}** processing")

    start_time = datetime.now()

    # Try pattern matching first if not explicitly using other modes
    if mode in ["Smart Auto", "Pattern Match"]:
        pattern_result = await process_pattern_match(question, systems["db_connector"])
        if pattern_result:
            pattern_result["processing_time"] = (
                datetime.now() - start_time
            ).total_seconds()
            return pattern_result

    # Use AI-powered approach
    if mode in ["Smart Auto", "AI-Powered"] and systems["llm_client"]:
        ai_result = await process_ai_powered(
            question,
            systems["db_connector"],
            systems["llm_client"],
            systems["llm_provider"],
            systems["schema_info"],
        )
        ai_result["processing_time"] = (datetime.now() - start_time).total_seconds()
        return ai_result

    # Use AutoGen approach
    if mode == "AutoGen Multi-Agent" and systems["autogen_system"]:
        autogen_result = await process_autogen(question, systems["autogen_system"])
        autogen_result["processing_time"] = (
            datetime.now() - start_time
        ).total_seconds()
        return autogen_result

    # Fallback
    return {
        "method": "Fallback",
        "success": False,
        "error": f"No suitable processing method available for mode: {mode}",
    }


def display_unified_results(response):
    """Display results from any processing method with MLflow logging and feedback collection"""

    # Get MLflow tracker
    tracker = st.session_state.mlflow_tracker

    # Log experiment to MLflow (for both successful and failed queries)
    question = response.get("question", "")
    method = response.get("method", "Unknown")
    processing_time = response.get("processing_time", 0)

    run_id = tracker.log_query_experiment(
        question=question,
        approach=method,
        result=response,
        execution_time=processing_time,
        session_id=st.session_state.session_id,
    )

    # Store current run_id for feedback collection
    st.session_state.current_run_id = run_id

    if not response["success"]:
        st.error(
            f"❌ {response.get('method', 'Processing')} failed: {response.get('error', 'Unknown error')}"
        )

        # Feedback for failed queries is handled in main()
        return

    # Method-specific success messages
    if method == "Pattern Match":
        st.success(f"⚡ {method} - Instant response ({processing_time:.2f}s)")
    elif method == "AI-Powered":
        st.success(f"🤖 {method} - AI SQL generation ({processing_time:.2f}s)")
    elif method == "AutoGen Multi-Agent":
        st.success(f"🔄 {method} - Multi-agent collaboration ({processing_time:.2f}s)")

    # Handle AutoGen disambiguation responses (user choices)
    if response.get("response_type") == "disambiguation":
        st.subheader("🤔 AutoGen Needs Clarification")
        
        # Show clarification questions
        if response.get("clarification_questions"):
            for question in response["clarification_questions"]:
                st.info(f"💬 **Question**: {question}")
        
        # Show user choices
        if response.get("user_choices"):
            st.subheader("🎯 Please Select Options:")
            user_choices = response["user_choices"]
            
            # Create multiselect for user choices
            selected_choices = st.multiselect(
                "Select the risk rating sources you want to analyze:",
                options=user_choices,
                default=user_choices,  # Select all by default
                key=f"disambiguation_choices_{st.session_state.current_run_id}"
            )
            
            if st.button("🔄 Continue Analysis with Selected Options", key=f"continue_analysis_{st.session_state.current_run_id}"):
                if selected_choices:
                    # Create a follow-up question based on selected choices
                    choices_text = ", ".join(selected_choices)
                    st.info(f"🔄 Continuing analysis with: {choices_text}")
                    
                    # You could trigger a new AutoGen request here with the selected choices
                    # For now, we'll just show the selection
                    st.success("✅ Choices recorded! You can now ask a more specific question about these rating sources.")
                else:
                    st.warning("Please select at least one option to continue.")
        
        return  # Don't show other sections for disambiguation responses
    
    # Show AutoGen answer if available (normal response)
    if response.get("answer"):
        st.subheader("🎯 Analysis")
        st.write(response["answer"])

    # Show SQL query
    if response.get("sql_query"):
        with st.expander(f"🔧 Generated SQL Query ({method})", expanded=False):
            st.code(response["sql_query"], language="sql")

    # Show results
    if response.get("results"):
        st.subheader("📊 Results")

        try:
            df = pd.DataFrame(response["results"])

            if len(df) > 0:
                # Format numeric columns
                for col in df.columns:
                    if df[col].dtype in ["int64", "float64"]:
                        if "balance" in col.lower() or "amount" in col.lower():
                            df[col] = df[col].apply(
                                lambda x: f"${x:,.2f}" if pd.notnull(x) else x
                            )
                        else:
                            df[col] = df[col].apply(
                                lambda x: f"{x:,}" if pd.notnull(x) else x
                            )

                st.dataframe(df, use_container_width=True)

                # Add insights for delinquency queries
                if (
                    "risk" in response.get("sql_query", "").lower()
                    or "delinq" in str(response).lower()
                ):
                    st.info(
                        "💡 **Insight**: Higher risk ratings (SUBSTANDARD, DOUBTFUL, LOSS) and past due amounts indicate increased delinquency probability."
                    )

                st.caption(f"📈 {len(df)} rows | Method: {method}")
            else:
                st.info("No results found")

        except Exception as e:
            st.write(response["results"])

    # Show AutoGen sources if available
    if response.get("sources"):
        with st.expander("🔍 Multi-Agent Details", expanded=False):
            for i, source in enumerate(response["sources"], 1):
                st.write(f"**Agent {i}:** {source}")

    # MLflow feedback collection is handled in main() after display_unified_results


def main():
    """Main unified application"""

    # Header
    st.title("🤖 Text2SQL with Claude AI")
    st.markdown(
        "**Smart processing: Pattern matching → AI-powered → Multi-agent collaboration**"
    )

    # Initialize all systems
    with st.spinner("🔧 Initializing unified Text2SQL systems..."):
        systems = initialize_systems()

    if not systems["db_connector"]:
        st.error("❌ Cannot initialize database connection.")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Processing Mode")

        mode_options = ["Smart Auto", "Pattern Match", "AI-Powered"]
        if systems["autogen_system"]:
            mode_options.append("AutoGen Multi-Agent")

        st.session_state.processing_mode = st.selectbox(
            "Select processing approach:", mode_options, index=0
        )

        # Mode descriptions
        if st.session_state.processing_mode == "Smart Auto":
            st.info("🤖 Automatically selects the best approach")
        elif st.session_state.processing_mode == "Pattern Match":
            st.info("⚡ Instant responses for common questions")
        elif st.session_state.processing_mode == "AI-Powered":
            st.info("🧠 AI generates SQL for complex questions")
        elif st.session_state.processing_mode == "AutoGen Multi-Agent":
            st.info("🔄 7-agent collaboration with caching")

        # System status
        st.subheader("🔧 System Status")
        st.write("✅ Database: Connected")
        st.write("✅ Pattern Matching: Ready")

        if systems["llm_client"]:
            provider_name = systems.get("llm_provider", "unknown").upper()
            st.write(f"✅ AI-Powered: Ready ({provider_name})")
        else:
            st.write("❌ AI-Powered: Not available")

        if systems["autogen_system"]:
            st.write("✅ AutoGen: Ready")
        else:
            st.write("⚠️ AutoGen: Not available")

        # Database stats
        if systems["schema_info"]:
            st.subheader("📊 Database")
            st.metric("Tables", len(systems["schema_info"]))
            total_rows = sum(
                table["row_count"] for table in systems["schema_info"].values()
            )
            st.metric("Total Records", f"{total_rows:,}")

        # MLflow tracking statistics
        render_mlflow_stats(st.session_state.mlflow_tracker)

    # Main content
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("💬 Ask Your Banking Question")

        # Comprehensive example questions
        example_questions = [
            "",
            # Pattern matching examples
            "How many customers do we have?",
            "What is our total loan portfolio value?",
            "What's our loan portfolio size?",
            "Show me the top 5 customers by loan balance",
            "Which loans are most likely to go delinquent?",
            "What's our total customers count?",
            # AI-powered examples
            "What percentage of our loan portfolio is considered high risk?",
            "Show me customers with past due amounts greater than $10,000",
            "Which customers have risk ratings that don't match their loan performance?",
            # AutoGen examples (if available)
            "Perform a comprehensive risk analysis identifying multiple warning signs across our portfolio",
            "Analyze the correlation between risk ratings, past due amounts, and industry trends",
        ]

        selected_question = st.selectbox(
            "Select an example:", example_questions, index=0
        )

        custom_question = st.text_area(
            "Or ask your own question:",
            height=100,
            placeholder="e.g., Which customers show early warning signs of potential default based on multiple risk factors?",
        )

        final_question = (
            custom_question.strip() if custom_question.strip() else selected_question
        )

        # Execute query
        if st.button("🔍 Process Query", type="primary", disabled=not final_question):
            with st.spinner(
                f"🤖 Processing with {st.session_state.processing_mode} approach..."
            ):

                try:
                    # Record start time for MLflow logging
                    start_time = time.time()

                    # Use asyncio.run to handle event loop properly
                    response = asyncio.run(
                        unified_query_processor(final_question, systems)
                    )

                    # Calculate execution time and add to response
                    execution_time = time.time() - start_time
                    response["processing_time"] = execution_time
                    response["question"] = final_question

                except Exception as e:
                    execution_time = (
                        time.time() - start_time if "start_time" in locals() else 0
                    )
                    st.error(f"Error processing query: {e}")
                    response = {
                        "success": False,
                        "error": str(e),
                        "method": "Error",
                        "processing_time": execution_time,
                        "question": final_question,
                    }

            # Display results
            display_unified_results(response)

            # FEEDBACK SECTION
            if (
                hasattr(st.session_state, "current_run_id")
                and st.session_state.current_run_id
            ):
                st.markdown("---")
                st.subheader("📝 Feedback")

                # Use timestamp to ensure unique keys
                feedback_key = (
                    f"feedback_{st.session_state.current_run_id}_{int(time.time())}"
                )

                # Single feedback selectbox
                feedback_rating = st.selectbox(
                    "How would you rate this response?",
                    ["Select rating...", "👍 Helpful", "👎 Not helpful"],
                    key=f"rating_{feedback_key}",
                )

                # Optional comment
                feedback_comment = st.text_area(
                    "Additional comments (optional):",
                    placeholder="What worked well? What could be improved?",
                    key=f"comment_{feedback_key}",
                    height=60,
                )

                # Submit button
                if st.button("Submit Feedback", key=f"submit_{feedback_key}"):
                    if feedback_rating != "Select rating...":
                        rating = 1 if feedback_rating == "👍 Helpful" else 0

                        try:
                            st.session_state.mlflow_tracker.log_user_feedback(
                                run_id=st.session_state.current_run_id,
                                user_rating=rating,
                                user_comment=feedback_comment,
                                user_id=st.session_state.get("user_id", "anonymous"),
                            )

                            # Show detailed confirmation
                            success_msg = f"✅ Thank you for your feedback!\n\n"
                            success_msg += f"**Rating:** {feedback_rating}\n"
                            if feedback_comment.strip():
                                success_msg += f"**Comment:** {feedback_comment}\n"
                            success_msg += f"**Logged to MLflow run:** `{st.session_state.current_run_id}`"

                            st.success(success_msg)

                            # Clear the run_id to prevent duplicate submissions
                            st.session_state.current_run_id = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error submitting feedback: {e}")
                    else:
                        st.warning("Please select a rating before submitting.")
            else:
                st.info("💡 Process a query above to provide feedback")

            # Add to history
            st.session_state.query_history.append(
                {
                    "question": final_question,
                    "response": response,
                    "timestamp": datetime.now(),
                }
            )

    with col2:
        st.subheader("📈 Query History")

        if st.session_state.query_history:
            for i, query in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    response = query["response"]
                    method = response.get("method", "Unknown")

                    st.write(f"**Question:** {query['question'][:50]}...")
                    st.write(f"**Method:** {method}")
                    st.write(f"**Status:** {'✅' if response['success'] else '❌'}")
                    if response.get("processing_time"):
                        st.write(f"**Time:** {response['processing_time']:.2f}s")
        else:
            st.info("No queries yet")

    # Footer
    st.markdown("---")
    st.markdown(
        "**🤖 Text2SQL with Claude AI** | Pattern Matching + AI-Powered + Multi-Agent | Powered by Anthropic"
    )


if __name__ == "__main__":
    main()
