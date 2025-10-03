#!/usr/bin/env python
"""
Test AutoGen database access with the corrected schema
"""
import sqlite3
import os
from dotenv import load_dotenv

def create_sample_response_for_risk_criteria():
    """Create the expected response for the risk criteria question"""
    
    load_dotenv('text_2_sql/.env')
    db_path = os.getenv('Text2Sql__Sqlite__Database')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🎯 EXPECTED AUTOGEN RESPONSE FOR: 'What are the criteria used to classify customers into different risk ratings?'")
    print("=" * 100)
    
    # Query 1: Get all risk rating fields and their descriptions
    print("1. RISK CLASSIFICATION FIELDS IN DATABASE:")
    print("-" * 50)
    
    risk_fields = [
        "LINE_OFFICER_RISK_RATING_CODE",
        "OFFICER_RISK_RATING_DESC", 
        "CREDIT_REVIEW_RISK_RATING_CODE",
        "CREDIT_REVIEW_RISK_RATING_DESC",
        "REGULATOR_RISK_RATING_CODE", 
        "REGULATOR_RISK_RATING_DESC"
    ]
    
    for field in risk_fields:
        cursor.execute(f"SELECT DISTINCT {field} FROM CUSTOMER_DIMENSION WHERE {field} IS NOT NULL LIMIT 5")
        values = [row[0] for row in cursor.fetchall()]
        print(f"• {field}: {', '.join(values[:3])}...")
    
    # Query 2: Show the actual risk rating distribution
    print("\n2. ACTUAL RISK RATING DISTRIBUTION:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT 
            OFFICER_RISK_RATING_DESC,
            COUNT(*) as customer_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM CUSTOMER_DIMENSION 
        WHERE OFFICER_RISK_RATING_DESC IS NOT NULL 
        GROUP BY OFFICER_RISK_RATING_DESC 
        ORDER BY customer_count DESC
    """)
    
    results = cursor.fetchall()
    for rating, count, pct in results:
        print(f"• {rating}: {count} customers ({pct}%)")
    
    # Query 3: Show multiple rating sources comparison
    print("\n3. MULTI-SOURCE RISK ASSESSMENT:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT 
            c.CUSTOMER_NAME,
            c.OFFICER_RISK_RATING_DESC as officer_rating,
            c.CREDIT_REVIEW_RISK_RATING_DESC as credit_review_rating,
            c.REGULATOR_RISK_RATING_DESC as regulator_rating,
            SUM(CAST(l.CURRENT_PRINCIPAL_BALANCE AS REAL)) as total_exposure
        FROM CUSTOMER_DIMENSION c
        LEFT JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
        WHERE c.OFFICER_RISK_RATING_DESC IS NOT NULL
        GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME, c.OFFICER_RISK_RATING_DESC, c.CREDIT_REVIEW_RISK_RATING_DESC, c.REGULATOR_RISK_RATING_DESC
        ORDER BY total_exposure DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    print("Top 10 customers by exposure with multi-source ratings:")
    for row in results:
        name, officer, credit, regulator, exposure = row
        exposure_str = f"${exposure:,.0f}" if exposure else "No active loans"
        print(f"• {name}: Officer={officer}, Credit={credit}, Regulator={regulator}, Exposure={exposure_str}")
    
    print("\n" + "=" * 100)
    print("🎯 WHAT AUTOGEN SHOULD RETURN:")
    print("=" * 100)
    
    print("""
Based on the FIS Banking database analysis, customers are classified into different risk ratings using THREE distinct evaluation sources:

1. **OFFICER RISK RATINGS** (OFFICER_RISK_RATING_DESC):
   - Primary ratings: A STABLE, A+ STABLE, EXCELLENT CREDIT, STRONG CREDIT, GOOD CREDIT
   - Most common rating: A STABLE (809 customers)
   - Used by loan officers for day-to-day risk assessment

2. **CREDIT REVIEW RATINGS** (CREDIT_REVIEW_RISK_RATING_DESC):  
   - Independent credit review assessment
   - Provides secondary validation of officer ratings
   - Used for portfolio oversight and validation

3. **REGULATOR RATINGS** (REGULATOR_RISK_RATING_DESC):
   - Regulatory compliance ratings
   - Aligned with banking regulatory requirements
   - Used for regulatory reporting and compliance

**Multi-Dimensional Assessment**: The database shows that customers receive ratings from all three sources, providing a comprehensive risk profile. For example, major borrowers like BORROWER 1 have ratings across all three dimensions to ensure thorough risk evaluation.

**Rating Distribution**: The portfolio shows concentration in higher-quality credits, with EXCELLENT CREDIT and A STABLE representing the largest customer segments, indicating a conservative risk profile.
""")
    
    conn.close()

if __name__ == "__main__":
    create_sample_response_for_risk_criteria()