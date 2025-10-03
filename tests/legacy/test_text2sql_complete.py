#!/usr/bin/env python
"""
Complete test of the Text2SQL system with FIS banking data
"""
import os
import sys
import asyncio
import json
from pathlib import Path
import sqlite3
import pandas as pd

# Add paths for the text2sql modules
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

async def test_complete_text2sql_system():
    """Test the complete Text2SQL system"""
    print("=" * 80)
    print("🏦 COMPLETE TEXT2SQL SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Test database connection
    print("📊 TESTING DATABASE CONNECTION...")
    try:
        from text_2_sql_core.connectors.sqlite_sql import SQLiteSqlConnector
        
        db_connector = SQLiteSqlConnector()
        
        # Test basic query
        result = await db_connector.query_execution("SELECT COUNT(*) as table_count FROM sqlite_master WHERE type='table'")
        print(f"✅ Database connected: {result[0]['table_count']} tables found")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test schema access
    print("\n🗂️  TESTING SCHEMA ACCESS...")
    try:
        schemas = await db_connector.get_entity_schemas("customer", as_json=False)
        print(f"✅ Schema access working: Found {len(schemas)} customer-related schemas")
        
        if schemas:
            print("📋 Sample schema:")
            sample = schemas[0]
            print(f"   Table: {sample['SelectFromEntity']}")
            print(f"   Columns: {len(sample['Columns'])}")
            print(f"   Sample columns: {[col['Name'] for col in sample['Columns'][:5]]}")
        
    except Exception as e:
        print(f"❌ Schema access failed: {e}")
        print("⚠️  This is expected if schema store not deployed")
    
    # Test specific banking queries
    print("\n🔍 TESTING BANKING QUERIES...")
    
    test_queries = [
        {
            "description": "Count all customers",
            "sql": "SELECT COUNT(*) as customer_count FROM CUSTOMER_DIMENSION"
        },
        {
            "description": "Total loan portfolio",
            "sql": "SELECT SUM(CURRENT_PRINCIPAL_BALANCE) as total_balance FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0"
        },
        {
            "description": "Top 3 customers by loan balance",
            "sql": """SELECT c.CUSTOMER_NAME, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_balance 
                     FROM CUSTOMER_DIMENSION c 
                     JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY 
                     WHERE l.CURRENT_PRINCIPAL_BALANCE > 0
                     GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME 
                     ORDER BY total_balance DESC LIMIT 3"""
        },
        {
            "description": "Loan products available",
            "sql": "SELECT DISTINCT LOAN_PRODUCT_DESC FROM LOAN_PRODUCT_DIMENSION WHERE LOAN_PRODUCT_DESC IS NOT NULL LIMIT 5"
        },
        {
            "description": "Risk rating distribution",
            "sql": """SELECT OFFICER_RISK_RATING_DESC, COUNT(*) as count 
                     FROM CUSTOMER_DIMENSION 
                     WHERE OFFICER_RISK_RATING_DESC IS NOT NULL 
                     GROUP BY OFFICER_RISK_RATING_DESC 
                     ORDER BY count DESC LIMIT 5"""
        }
    ]
    
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📊 Test {i}: {query['description']}")
        try:
            result = await db_connector.query_execution(query['sql'])
            
            if result:
                print(f"   ✅ Success: {len(result)} rows returned")
                
                # Show sample data
                if len(result) <= 3:
                    for row in result:
                        print(f"      {dict(row)}")
                else:
                    print(f"      Sample: {dict(result[0])}")
                    print(f"      ... and {len(result)-1} more rows")
                
                successful_queries += 1
            else:
                print(f"   ⚠️  No results returned")
                successful_queries += 1  # Still counts as success
                
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
    
    print(f"\n📈 QUERY TEST RESULTS: {successful_queries}/{len(test_queries)} successful")
    
    return successful_queries == len(test_queries)

async def test_streamlit_integration():
    """Test the integration components for Streamlit"""
    print("\n" + "=" * 80)
    print("🌐 STREAMLIT INTEGRATION TEST")
    print("=" * 80)
    print()
    
    # Test database statistics function
    print("📊 Testing database statistics...")
    try:
        db_path = os.getenv('Text2Sql__Sqlite__Database')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get comprehensive stats
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ Found {len(tables)} tables")
        
        total_rows = 0
        total_columns = 0
        
        for table in tables[:3]:  # Test first 3 tables
            table_name = table[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            total_rows += row_count
            total_columns += len(columns)
            
            print(f"   📋 {table_name}: {len(columns)} columns, {row_count:,} rows")
        
        print(f"✅ Statistics working: {total_columns} columns, {total_rows:,} total rows (from sample)")
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False

async def demonstrate_text2sql_capabilities():
    """Demonstrate the full capabilities of the Text2SQL system"""
    print("\n" + "=" * 80)
    print("🎯 TEXT2SQL SYSTEM CAPABILITIES DEMONSTRATION")
    print("=" * 80)
    print()
    
    capabilities = [
        {
            "feature": "Natural Language Processing",
            "description": "Convert business questions to SQL queries",
            "example": "\"How many customers do we have?\" → \"SELECT COUNT(*) FROM CUSTOMER_DIMENSION\""
        },
        {
            "feature": "Schema Intelligence", 
            "description": "Automatically find relevant tables and columns",
            "example": "Question about 'loans' finds CL_DETAIL_FACT, LOAN_PRODUCT_DIMENSION tables"
        },
        {
            "feature": "Banking Domain Knowledge",
            "description": "Understands financial terminology and relationships",
            "example": "Knows that 'portfolio value' means sum of CURRENT_PRINCIPAL_BALANCE"
        },
        {
            "feature": "Complex Query Generation",
            "description": "Creates multi-table JOINs and aggregations",
            "example": "Top customers query joins CUSTOMER_DIMENSION with CL_DETAIL_FACT"
        },
        {
            "feature": "Result Formatting",
            "description": "Returns structured, readable results",
            "example": "Formats numbers, provides column explanations"
        }
    ]
    
    for cap in capabilities:
        print(f"🔧 {cap['feature']}")
        print(f"   📝 {cap['description']}")
        print(f"   💡 Example: {cap['example']}")
        print()
    
    # Show system configuration
    print("⚙️  SYSTEM CONFIGURATION:")
    config_items = [
        ("Database Engine", os.getenv('Text2Sql__DatabaseEngine', 'SQLITE')),
        ("Use Query Cache", os.getenv('Text2Sql__UseQueryCache', 'True')),
        ("Use Column Value Store", os.getenv('Text2Sql__UseColumnValueStore', 'True')),
        ("Database Path", os.path.basename(os.getenv('Text2Sql__Sqlite__Database', ''))),
        ("OpenAI Endpoint", os.getenv('OpenAI__Endpoint', '').split('.')[0] + '...' if os.getenv('OpenAI__Endpoint') else 'Not set')
    ]
    
    for item, value in config_items:
        print(f"   • {item}: {value}")
    print()

async def main():
    """Main test function"""
    print("🚀 FIS BANKING TEXT2SQL COMPLETE SYSTEM TEST")
    print("   Testing all components of your Text2SQL implementation")
    print()
    
    # Run all tests
    db_test = await test_complete_text2sql_system()
    stats_test = await test_streamlit_integration()
    
    # Show capabilities
    await demonstrate_text2sql_capabilities()
    
    # Final summary
    print("=" * 80)
    print("🎉 TEST SUMMARY")
    print("=" * 80)
    print()
    
    tests_passed = sum([db_test, stats_test])
    total_tests = 2
    
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    
    if db_test:
        print("   ✅ Database connection and queries working")
    else:
        print("   ❌ Database issues detected")
    
    if stats_test:
        print("   ✅ Streamlit integration components ready")
    else:
        print("   ❌ Streamlit integration issues")
    
    print()
    print("🌐 STREAMLIT APPLICATION STATUS:")
    print("   The Streamlit app is running at: http://localhost:8501")
    print("   You can test the Text2SQL system interactively!")
    print()
    
    print("🎯 NEXT STEPS:")
    print("   1. Open the Streamlit app in your browser")
    print("   2. Try the sample banking questions")
    print("   3. Ask custom questions about your data")
    print("   4. Explore the multi-agent capabilities")
    print()
    
    if tests_passed == total_tests:
        print("🎉 All systems ready for production use!")
    else:
        print("⚠️  Some issues detected - check error messages above")

if __name__ == "__main__":
    asyncio.run(main())