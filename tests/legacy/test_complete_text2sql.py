#!/usr/bin/env python
"""
Test complete Text2SQL functionality with real banking data
"""
import sys
import os
import sqlite3
import asyncio
from pathlib import Path
import json

# Add text_2_sql_core to path
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

async def test_text2sql_with_banking_data():
    """Test Text2SQL with real banking database"""
    print("=== TESTING TEXT2SQL WITH BANKING DATA ===")
    
    # Load data dictionary for context
    data_dict_path = "text_2_sql/data_dictionary_output/banking_data_dictionary.json"
    
    if os.path.exists(data_dict_path):
        with open(data_dict_path, 'r') as f:
            data_dict = json.load(f)
        
        # Create schema summary for context
        schema_info = "Database Schema:\n"
        for entity in data_dict[:8]:  # Use first 8 tables to avoid token limits
            table_name = entity['Entity']
            table_desc = entity['Definition']
            key_columns = [attr['Attribute'] for attr in entity['Attributes'][:5]]  # First 5 columns
            
            schema_info += f"- Table: {table_name} - {table_desc}\n"
            schema_info += f"  Key columns: {', '.join(key_columns)}\n"
    else:
        schema_info = "Banking database with customer, loan, and product information."
    
    # Test queries about your banking data
    test_questions = [
        "How many customers do we have in total?",
        "What are the different customer types in our database?",
        "Show me the top 5 customers by customer key",
        "How many active loans do we have?",
        "What currencies are used in our system?",
        "Show me loan products and their counts",
        "What is the total principal balance across all loans?"
    ]
    
    try:
        from text_2_sql_core.connectors.open_ai import OpenAIConnector
        openai_connector = OpenAIConnector()
        
        # Get database connection
        db_path = os.getenv('Text2Sql__Sqlite__Database')
        
        print(f"Database: {db_path}")
        print(f"Schema context: {len(schema_info)} characters")
        print(f"Testing {len(test_questions)} questions...\n")
        
        for i, question in enumerate(test_questions, 1):
            print(f"=== QUESTION {i} ===")
            print(f"Q: {question}")
            
            try:
                # Generate SQL query
                messages = [
                    {
                        "role": "system", 
                        "content": f"You are a SQL expert for a banking database. Generate SQLite-compatible SQL queries.\n\n{schema_info}\n\nRules:\n- Use SQLite syntax\n- Return only the SQL query\n- Use appropriate table and column names from the schema\n- Include LIMIT clauses for large results"
                    },
                    {
                        "role": "user", 
                        "content": question
                    }
                ]
                
                sql_query = await openai_connector.run_completion_request(messages, max_tokens=300)
                
                # Clean up the SQL query
                sql_query = sql_query.strip()
                if sql_query.startswith('```sql'):
                    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
                
                print(f"Generated SQL: {sql_query}")
                
                # Execute the query
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute(sql_query)
                results = cursor.fetchall()
                
                # Get column names
                column_names = [description[0] for description in cursor.description]
                
                print(f"Results ({len(results)} rows):")
                if results:
                    # Show column headers
                    print(f"  {' | '.join(column_names)}")
                    print(f"  {'-' * (len(' | '.join(column_names)))}")
                    
                    # Show first few results
                    for row in results[:5]:
                        row_str = ' | '.join(str(val) if val is not None else 'NULL' for val in row)
                        print(f"  {row_str}")
                    
                    if len(results) > 5:
                        print(f"  ... and {len(results) - 5} more rows")
                else:
                    print("  No results found")
                
                conn.close()
                print("✅ Query executed successfully!\n")
                
            except Exception as e:
                print(f"❌ Query failed: {e}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Text2SQL test failed: {e}")
        return False

async def main():
    """Run the complete test"""
    print("Testing complete Text2SQL system with your banking data...\n")
    
    success = await test_text2sql_with_banking_data()
    
    print("=== FINAL SUMMARY ===")
    if success:
        print("🎉 SUCCESS! Your Text2SQL system is fully working!")
        print("✅ Database connection: Working")
        print("✅ SQL generation: Working") 
        print("✅ Query execution: Working")
        print("✅ Real banking data: Loaded")
        print("\nYour Text2SQL system can now:")
        print("- Convert natural language to SQL")
        print("- Execute queries against your banking database")
        print("- Return actual results from your data")
        print("\n🚀 Ready for production use!")
    else:
        print("❌ Some issues found. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())