#!/usr/bin/env python
"""
Find optimal AutoGen demo questions that will generate meaningful results
"""
import sqlite3
import os
from dotenv import load_dotenv

def test_question_data_availability():
    """Test questions to see which ones will return meaningful data"""
    
    load_dotenv('text_2_sql/.env')
    db_path = os.getenv('Text2Sql__Sqlite__Database')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Test Query 1: Multi-dimensional risk analysis with ownership patterns
    print("🎯 DEMO QUESTION 1: Multi-dimensional portfolio risk analysis")
    print("Question: 'Perform a comprehensive analysis of our portfolio identifying customers with multiple risk factors and varying ownership patterns'")
    print("-" * 80)
    
    query1 = """
    SELECT 
        c.CUSTOMER_NAME,
        c.OFFICER_RISK_RATING_DESC,
        c.CREDIT_REVIEW_RISK_RATING_DESC,
        COUNT(l.PRODUCT_KEY) as total_loans,
        SUM(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) as total_exposure,
        AVG(CAST(l.OWNERSHIP_PERCENT AS REAL)) as avg_ownership,
        COUNT(CASE WHEN CAST(l.OWNERSHIP_PERCENT AS REAL) < 100 THEN 1 END) as syndicated_loans
    FROM CUSTOMER_DIMENSION c
    JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
    WHERE CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL) > 0
      AND c.OFFICER_RISK_RATING_DESC IS NOT NULL
    GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME, c.OFFICER_RISK_RATING_DESC, c.CREDIT_REVIEW_RISK_RATING_DESC
    HAVING COUNT(l.PRODUCT_KEY) > 1
    ORDER BY total_exposure DESC
    LIMIT 10
    """
    
    cursor.execute(query1)
    results1 = cursor.fetchall()
    print(f"Results: {len(results1)} customers with multiple loans and risk factors")
    for i, row in enumerate(results1[:3], 1):
        print(f"{i}. {row[0]} - Risk: {row[1]} - Loans: {row[3]} - Exposure: ${row[4]:,.0f} - Avg Ownership: {row[5]:.1f}%")
    
    print("\n" + "=" * 80)
    
    # Test Query 2: Trend analysis with risk correlation
    print("🎯 DEMO QUESTION 2: Portfolio concentration analysis with risk correlation")
    print("Question: 'Analyze portfolio concentration trends showing the correlation between customer risk ratings and loan syndication patterns'")
    print("-" * 80)
    
    query2 = """
    SELECT 
        c.OFFICER_RISK_RATING_DESC as risk_rating,
        COUNT(DISTINCT c.CUSTOMER_KEY) as unique_customers,
        COUNT(l.PRODUCT_KEY) as total_loans,
        SUM(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) as total_portfolio_value,
        AVG(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) as avg_loan_size,
        COUNT(CASE WHEN CAST(l.OWNERSHIP_PERCENT AS REAL) = 100 THEN 1 END) as fully_owned_loans,
        COUNT(CASE WHEN CAST(l.OWNERSHIP_PERCENT AS REAL) < 100 THEN 1 END) as syndicated_loans,
        AVG(CAST(l.OWNERSHIP_PERCENT AS REAL)) as avg_ownership_percent
    FROM CUSTOMER_DIMENSION c
    JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
    WHERE CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL) > 0
      AND c.OFFICER_RISK_RATING_DESC IS NOT NULL
    GROUP BY c.OFFICER_RISK_RATING_DESC
    ORDER BY total_portfolio_value DESC
    """
    
    cursor.execute(query2)
    results2 = cursor.fetchall()
    print(f"Results: {len(results2)} risk rating categories with portfolio analysis")
    for i, row in enumerate(results2[:5], 1):
        syndication_ratio = (row[6] / row[2] * 100) if row[2] > 0 else 0
        print(f"{i}. {row[0]}: {row[1]} customers, ${row[3]:,.0f} portfolio, {syndication_ratio:.1f}% syndicated")
    
    print("\n" + "=" * 80)
    
    # Test Query 3: Alternative complex question
    print("🎯 DEMO QUESTION 3: Large exposure concentration analysis")
    print("Question: 'Identify concerning patterns in our largest exposures including multi-dimensional risk assessment across different rating agencies'")
    print("-" * 80)
    
    query3 = """
    SELECT 
        c.CUSTOMER_NAME,
        SUM(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) as total_exposure,
        c.OFFICER_RISK_RATING_DESC as officer_rating,
        c.CREDIT_REVIEW_RISK_RATING_DESC as credit_review_rating,
        c.REGULATOR_RISK_RATING_DESC as regulator_rating,
        COUNT(l.PRODUCT_KEY) as loan_count,
        AVG(CAST(l.OWNERSHIP_PERCENT AS REAL)) as avg_ownership,
        CASE 
            WHEN SUM(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) > 100000000 THEN 'VERY HIGH'
            WHEN SUM(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) > 50000000 THEN 'HIGH'
            WHEN SUM(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) > 10000000 THEN 'MEDIUM'
            ELSE 'LOW'
        END as exposure_category
    FROM CUSTOMER_DIMENSION c
    JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
    WHERE CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL) > 0
    GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME, c.OFFICER_RISK_RATING_DESC, c.CREDIT_REVIEW_RISK_RATING_DESC, c.REGULATOR_RISK_RATING_DESC
    ORDER BY total_exposure DESC
    LIMIT 15
    """
    
    cursor.execute(query3)
    results3 = cursor.fetchall()
    print(f"Results: {len(results3)} customers with large exposure analysis")
    for i, row in enumerate(results3[:5], 1):
        print(f"{i}. {row[0]} - ${row[1]:,.0f} ({row[7]}) - Officer: {row[2]} - Loans: {row[5]}")
    
    conn.close()
    
    print("\n" + "🎯" * 20)
    print("RECOMMENDED DEMO QUESTIONS FOR AUTOGEN:")
    print("🎯" * 20)
    
    print("\n1. 📊 BEST FOR COMPLEX ANALYSIS:")
    print("'Perform a comprehensive analysis of our portfolio identifying customers with multiple risk factors and varying ownership patterns'")
    print("✅ Shows multi-agent coordination, risk analysis, and ownership complexity")
    
    print("\n2. 📈 BEST FOR TREND CORRELATION:")
    print("'Analyze portfolio concentration trends showing the correlation between customer risk ratings and loan syndication patterns'")
    print("✅ Demonstrates statistical analysis, correlation detection, and business insights")
    
    print("\n3. 🔍 ALTERNATIVE COMPLEX QUESTION:")
    print("'Identify concerning patterns in our largest exposures including multi-dimensional risk assessment across different rating agencies'")
    print("✅ Showcases pattern detection, multi-dimensional analysis, and risk assessment")

if __name__ == "__main__":
    test_question_data_availability()