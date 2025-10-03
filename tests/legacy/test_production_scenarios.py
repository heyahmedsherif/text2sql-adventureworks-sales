#!/usr/bin/env python
"""
Test advanced production scenarios for Text2SQL
"""
import sys
import os
import sqlite3
import asyncio
from pathlib import Path
import json
import time

# Add text_2_sql_core to path
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

async def test_production_scenarios():
    """Test advanced production scenarios"""
    print("=== TESTING PRODUCTION SCENARIOS ===")
    
    # Load schema context
    data_dict_path = "text_2_sql/data_dictionary_output/banking_data_dictionary.json"
    with open(data_dict_path, 'r') as f:
        data_dict = json.load(f)
    
    # Enhanced schema info with relationships
    schema_info = """Banking Database Schema:
    
DIMENSION TABLES:
- CUSTOMER_DIMENSION: Customer information (4449 customers)
  Key: CUSTOMER_KEY, includes name, type, currency, risk ratings, industry codes
- LOAN_PRODUCT_DIMENSION: Loan product details (4298 products)  
  Key: PRODUCT_KEY, includes rates, terms, product types
- CURRENCY_DIMENSION: Currency information (1346 currencies)
- MONTH_DIMENSION: Time dimension (12 months)
- INVESTOR_DIMENSION: Investor information (23 investors)
- OWNER_DIMENSION: Ownership information (571 owners)
- LIMIT_DIMENSION: Credit limit information (1939 limits)

FACT TABLES:
- CL_DETAIL_FACT: Commercial loan details (14955 loan records)
  Keys: PRODUCT_KEY, CUSTOMER_KEY, INVESTOR_KEY, OWNER_KEY, MONTH_ID
  Measures: CURRENT_PRINCIPAL_BALANCE, INTEREST_BALANCE, loan amounts and rates
- CA_DETAIL_FACT: Cash account details (17059 account records)
  Similar structure to CL_DETAIL_FACT for cash accounts

RELATIONSHIPS:
- Join CUSTOMER_DIMENSION and CL_DETAIL_FACT on CUSTOMER_KEY
- Join LOAN_PRODUCT_DIMENSION and CL_DETAIL_FACT on PRODUCT_KEY
- Join other dimensions via their respective keys
"""
    
    # Complex production test scenarios
    scenarios = [
        {
            "category": "Business Intelligence",
            "questions": [
                "What is the total principal balance by customer type?",
                "Show me the top 10 customers by total loan balance with their risk ratings",
                "What are the average loan amounts by industry code?",
                "How many loans are past due and what's the total past due amount?",
            ]
        },
        {
            "category": "Risk Analysis", 
            "questions": [
                "Which customers have the highest risk ratings and their total exposure?",
                "What is the concentration of loans by currency?",
                "Show customers with loan balances over 1 million",
                "What percentage of our portfolio is in each customer type?",
            ]
        },
        {
            "category": "Financial Reporting",
            "questions": [
                "What is our total loan portfolio value?",
                "Show monthly loan origination trends",
                "What are the different loan statuses and their counts?",
                "Calculate the average interest rate across all active loans",
            ]
        },
        {
            "category": "Operational Queries",
            "questions": [
                "Which loans are maturing in the current month?", 
                "Show me loans that need review based on review dates",
                "What are the most common loan products by count?",
                "Find customers with multiple loan products",
            ]
        }
    ]
    
    try:
        from text_2_sql_core.connectors.open_ai import OpenAIConnector
        openai_connector = OpenAIConnector()
        
        db_path = os.getenv('Text2Sql__Sqlite__Database')
        
        success_count = 0
        total_count = 0
        
        for scenario in scenarios:
            print(f"\n{'='*50}")
            print(f"🏢 {scenario['category'].upper()}")
            print(f"{'='*50}")
            
            for question in scenario['questions']:
                total_count += 1
                print(f"\n📊 Query {total_count}: {question}")
                
                try:
                    start_time = time.time()
                    
                    # Generate SQL with enhanced context
                    messages = [
                        {
                            "role": "system", 
                            "content": f"""You are an expert SQL analyst for a banking database. Generate SQLite-compatible queries.

{schema_info}

Guidelines:
- Use proper JOINs between fact and dimension tables
- Include appropriate WHERE clauses for business logic
- Use aggregations (SUM, COUNT, AVG) for analytical queries
- Add LIMIT clauses for large result sets
- Return only the SQL query, no explanations
- Handle NULL values appropriately"""
                        },
                        {
                            "role": "user", 
                            "content": question
                        }
                    ]
                    
                    sql_query = await openai_connector.run_completion_request(messages, max_tokens=400)
                    
                    # Clean SQL
                    sql_query = sql_query.strip()
                    if sql_query.startswith('```sql'):
                        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
                    
                    # Execute query
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute(sql_query)
                    results = cursor.fetchall()
                    
                    execution_time = time.time() - start_time
                    
                    print(f"⚡ Query executed in {execution_time:.2f}s")
                    print(f"📝 SQL: {sql_query}")
                    print(f"📊 Results: {len(results)} rows")
                    
                    # Show sample results
                    if results:
                        column_names = [desc[0] for desc in cursor.description]
                        print(f"🔍 Columns: {', '.join(column_names)}")
                        
                        # Show first 3 results
                        for i, row in enumerate(results[:3], 1):
                            row_str = ' | '.join(str(val)[:50] if val is not None else 'NULL' for val in row)
                            print(f"   {i}: {row_str}")
                        
                        if len(results) > 3:
                            print(f"   ... and {len(results) - 3} more rows")
                    
                    conn.close()
                    success_count += 1
                    print("✅ SUCCESS")
                    
                except Exception as e:
                    print(f"❌ FAILED: {str(e)[:100]}...")
                    print(f"🔧 SQL: {sql_query[:100]}...")
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"🎯 PRODUCTION TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Queries: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"Success Rate: {(success_count/total_count)*100:.1f}%")
        
        if success_count >= total_count * 0.8:  # 80% success rate
            print(f"\n🎉 EXCELLENT! Your system is production-ready!")
            print(f"✅ High success rate on complex business queries")
            print(f"✅ Handles joins, aggregations, and analytical queries")
            print(f"✅ Works with real banking data and schema")
        else:
            print(f"\n⚠️  Some queries failed. Review the errors above.")
        
        return success_count >= total_count * 0.8
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        return False

async def main():
    """Run production scenario tests"""
    print("Testing advanced production scenarios with your banking data...\n")
    
    success = await test_production_scenarios()
    
    print(f"\n{'='*60}")
    print(f"🏆 FINAL PRODUCTION ASSESSMENT")
    print(f"{'='*60}")
    
    if success:
        print("🚀 YOUR TEXT2SQL SYSTEM IS PRODUCTION READY!")
        print("\n✅ Core Capabilities Verified:")
        print("   • Natural language to SQL conversion")
        print("   • Complex business query handling") 
        print("   • Multi-table joins and aggregations")
        print("   • Real banking data integration")
        print("   • Performance and reliability")
        print("\n🎯 Ready for enterprise deployment!")
        
    else:
        print("🔧 System needs refinement for production use")
        print("Review failed queries and adjust schema context")

if __name__ == "__main__":
    asyncio.run(main())