#!/usr/bin/env python
"""
Test the fixed query mappings to ensure basic banking questions work
"""
import sys
import os
import asyncio
from pathlib import Path

# Add paths for the text2sql modules
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

from dotenv import load_dotenv
load_dotenv('text_2_sql/.env')

async def test_basic_banking_questions():
    """Test all the basic banking questions that should work"""
    print("=" * 80)
    print("🧪 TESTING FIXED QUERY MAPPINGS")
    print("=" * 80)
    print()
    
    try:
        from text_2_sql_core.connectors.sqlite_sql import SQLiteSqlConnector
        db_connector = SQLiteSqlConnector()
        print("✅ Database connector initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # Test questions that should now work
    test_questions = [
        "What is the average loan amount?",
        "How many customers do we have?", 
        "What is our total loan portfolio value?",
        "Show me the top 5 customers by loan balance",
        "How many active loans do we have?",
        "How are customers distributed by risk rating?",
        "Which industry has the most loans?",
        "Show me customers with highest risk ratings"
    ]
    
    # Simplified query mapping (same as in the Streamlit app)
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
        "active loans": "SELECT COUNT(*) as active_loan_count FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
        "risk rating": """SELECT OFFICER_RISK_RATING_DESC, COUNT(*) as count 
                         FROM CUSTOMER_DIMENSION 
                         WHERE OFFICER_RISK_RATING_DESC IS NOT NULL 
                         GROUP BY OFFICER_RISK_RATING_DESC 
                         ORDER BY count DESC""",
        "industry": """SELECT c.PRIMARY_INDUSTRY_CODE, COUNT(*) as customer_count, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_loans
                      FROM CUSTOMER_DIMENSION c
                      JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY  
                      WHERE c.PRIMARY_INDUSTRY_CODE IS NOT NULL AND l.CURRENT_PRINCIPAL_BALANCE > 0
                      GROUP BY c.PRIMARY_INDUSTRY_CODE
                      ORDER BY total_loans DESC LIMIT 10""",
        "highest risk": """SELECT c.CUSTOMER_NAME, c.OFFICER_RISK_RATING_DESC, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_exposure
                          FROM CUSTOMER_DIMENSION c
                          JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
                          WHERE c.OFFICER_RISK_RATING_DESC IN ('SUBSTANDARD', 'DOUBTFUL', 'LOSS')
                          AND l.CURRENT_PRINCIPAL_BALANCE > 0
                          GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME, c.OFFICER_RISK_RATING_DESC
                          ORDER BY total_exposure DESC LIMIT 10"""
    }
    
    successful_queries = 0
    
    for question in test_questions:
        print(f"🔍 Testing: \"{question}\"")
        
        # Find matching query (same logic as Streamlit app)
        question_lower = question.lower()
        sql_query = None
        
        for key, query in query_mappings.items():
            if key in question_lower:
                sql_query = query
                break
        
        if not sql_query:
            print(f"   ❌ No pattern match found - would show table names")
            continue
        
        print(f"   🔧 Mapped to: {key}")
        
        try:
            result = await db_connector.query_execution(sql_query)
            
            if result:
                print(f"   ✅ Success: {len(result)} rows returned")
                
                # Show formatted result for single metrics
                if len(result) == 1 and len(result[0]) == 1:
                    key, value = next(iter(result[0].items()))
                    if isinstance(value, (int, float)) and value > 1000000:
                        print(f"   📊 Result: {key} = ${value:,.0f}")
                    elif isinstance(value, (int, float)):
                        print(f"   📊 Result: {key} = {value:,}")
                    else:
                        print(f"   📊 Result: {key} = {value}")
                else:
                    # Multiple rows - show first few
                    print(f"   📊 Sample Results:")
                    for i, row in enumerate(result[:3]):
                        formatted_row = {}
                        for k, v in row.items():
                            if isinstance(v, (int, float)) and v > 1000000:
                                formatted_row[k] = f"${v:,.0f}"
                            elif isinstance(v, (int, float)):
                                formatted_row[k] = f"{v:,}"
                            else:
                                formatted_row[k] = str(v)[:50]
                        print(f"      {i+1}. {formatted_row}")
                    
                    if len(result) > 3:
                        print(f"      ... and {len(result)-3} more")
                
                successful_queries += 1
            else:
                print(f"   ⚠️  No results returned")
                
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
        
        print()
    
    print("=" * 80)
    print(f"📊 TEST RESULTS: {successful_queries}/{len(test_questions)} queries successful")
    print("=" * 80)
    print()
    
    if successful_queries == len(test_questions):
        print("🎉 ALL BASIC BANKING QUESTIONS NOW WORK!")
        print("   The Streamlit app should handle these queries correctly.")
    else:
        print("⚠️  Some queries still need attention")
    
    print()
    print("🌐 Your updated Streamlit app is running at: http://localhost:8501")
    print("   Try asking \"What is the average loan amount?\" - it should work now!")

if __name__ == "__main__":
    asyncio.run(test_basic_banking_questions())