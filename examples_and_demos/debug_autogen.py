#!/usr/bin/env python
"""
Debug script to test AutoGen inner components directly
"""
import sys
import os
from pathlib import Path
import asyncio
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

async def test_autogen_components():
    """Test AutoGen components step by step"""
    try:
        print("=== Testing AutoGen Components ===")
        
        # Test 1: Environment variables
        print(f"1. Environment Variables:")
        print(f"   SPIDER_DATA_DIR: {os.getenv('SPIDER_DATA_DIR')}")
        print(f"   Text2Sql__DatabaseEngine: {os.getenv('Text2Sql__DatabaseEngine')}")
        print(f"   Text2Sql__Sqlite__Database: {os.getenv('Text2Sql__Sqlite__Database')}")
        
        # Test 2: Database Connector
        print(f"\n2. Database Connector:")
        from text_2_sql_core.connectors.factory import ConnectorFactory
        db_connector = ConnectorFactory.get_database_connector()
        print(f"   Connector type: {type(db_connector)}")
        
        # Test 3: Simple SQL query
        print(f"\n3. Direct SQL Query Test:")
        result = await db_connector.query_execution_with_limit("SELECT COUNT(*) as count FROM CUSTOMER_DIMENSION")
        print(f"   Query result: {result}")
        
        # Test 4: Schema Selection Agent
        print(f"\n4. Schema Selection Agent:")
        from text_2_sql_core.custom_agents.sql_schema_selection_agent import SqlSchemaSelectionAgentCustomAgent
        schema_agent = SqlSchemaSelectionAgentCustomAgent()
        schema_result = await schema_agent.process_message("How many customers do we have?")
        print(f"   Schema result: {schema_result}")
        
        # Test 5: Inner AutoGen System
        print(f"\n5. Inner AutoGen System:")
        from autogen_text_2_sql.inner_autogen_text_2_sql import InnerAutoGenText2Sql
        inner_system = InnerAutoGenText2Sql()
        
        # Test the agents
        agents = inner_system.get_all_agents()
        print(f"   Number of agents: {len(agents)}")
        for agent in agents:
            print(f"   - {agent.name}: {agent.description}")
            
        print(f"\n6. Testing Inner AutoGen Flow:")
        results = []
        async for message in inner_system.process_user_message(
            "How many customers do we have?",
            injected_parameters={}
        ):
            results.append(message)
            print(f"   Inner message: {type(message).__name__} - {message}")
        
        final_result = results[-1] if results else None
        print(f"   Final inner result: {final_result}")
        
        return final_result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_autogen_components())
    print(f"\nFinal result: {result}")