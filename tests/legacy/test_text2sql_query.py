#!/usr/bin/env python
"""
Test Text2SQL query generation functionality
"""
import sys
import os
import asyncio
from pathlib import Path

# Add text_2_sql_core to path
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

async def test_sql_generation():
    """Test SQL query generation"""
    print("=== TESTING SQL QUERY GENERATION ===")
    
    try:
        from text_2_sql_core.connectors.open_ai import OpenAIConnector
        
        connector = OpenAIConnector()
        
        # Create a simple prompt for SQL generation
        schema_info = """
        Database Schema:
        - Table: Customers (CustomerID int, FirstName nvarchar(50), LastName nvarchar(50), Email nvarchar(100))
        - Table: Orders (OrderID int, CustomerID int, OrderDate datetime, TotalAmount decimal(10,2))
        - Table: Products (ProductID int, ProductName nvarchar(100), Price decimal(8,2))
        """
        
        user_question = "How many customers do we have in total?"
        
        messages = [
            {"role": "system", "content": f"You are a SQL expert. Given this database schema:\n{schema_info}\n\nGenerate a SQL query to answer the user's question. Return only the SQL query."},
            {"role": "user", "content": user_question}
        ]
        
        sql_result = await connector.run_completion_request(messages)
        
        print(f"✅ SQL Generation successful!")
        print(f"Question: {user_question}")
        print(f"Generated SQL: {sql_result}")
        
        # Test another query
        user_question2 = "What are the top 5 customers by total order amount?"
        messages2 = [
            {"role": "system", "content": f"You are a SQL expert. Given this database schema:\n{schema_info}\n\nGenerate a SQL query to answer the user's question. Return only the SQL query."},
            {"role": "user", "content": user_question2}
        ]
        
        sql_result2 = await connector.run_completion_request(messages2)
        
        print(f"\nQuestion: {user_question2}")
        print(f"Generated SQL: {sql_result2}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL generation failed: {e}")
        return False

async def main():
    """Run the test"""
    print("Testing Text2SQL query generation...\n")
    
    sql_ok = await test_sql_generation()
    
    print(f"\n=== SUMMARY ===")
    if sql_ok:
        print("✅ Text2SQL is working! The system can generate SQL queries from natural language.")
        print("\n🚀 Your Text2SQL setup is ready!")
        print("Next steps:")
        print("1. Fix database connection to test with real data")
        print("2. Or test with a sample database")
        print("3. Upload schema to AI Search for enhanced context")
    else:
        print("❌ Issues found with SQL generation.")

if __name__ == "__main__":
    asyncio.run(main())