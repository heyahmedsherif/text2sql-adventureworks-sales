#!/usr/bin/env python
"""
Create exact schema context from SQLite database
"""
import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv('text_2_sql/.env')

def create_exact_schema_context():
    """Create precise schema context with actual column names"""
    print("=== CREATING EXACT SCHEMA CONTEXT ===")
    
    db_path = os.getenv('Text2Sql__Sqlite__Database')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema_context = "BANKING DATABASE SCHEMA - EXACT COLUMN NAMES:\n\n"
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # Get sample data to understand content
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        sample = cursor.fetchone()
        
        schema_context += f"TABLE: {table}\n"
        schema_context += f"Columns ({len(columns)}):\n"
        
        for i, col in enumerate(columns):
            col_name = col[1]
            col_type = col[2]
            sample_val = sample[i] if sample and i < len(sample) else "NULL"
            
            # Truncate long sample values
            if sample_val and len(str(sample_val)) > 50:
                sample_val = str(sample_val)[:47] + "..."
                
            schema_context += f"  - {col_name} ({col_type}) [example: {sample_val}]\n"
        
        schema_context += "\n"
    
    # Add relationship information
    schema_context += """KEY RELATIONSHIPS:
- CUSTOMER_DIMENSION.CUSTOMER_KEY -> CL_DETAIL_FACT.CUSTOMER_KEY 
- LOAN_PRODUCT_DIMENSION.PRODUCT_KEY -> CL_DETAIL_FACT.PRODUCT_KEY
- MONTH_DIMENSION.MONTH_ID -> CL_DETAIL_FACT.MONTH_ID
- INVESTOR_DIMENSION.INVESTOR_KEY -> CL_DETAIL_FACT.INVESTOR_KEY
- OWNER_DIMENSION.OWNER_KEY -> CL_DETAIL_FACT.OWNER_KEY

IMPORTANT NOTES:
- Use EXACT column names as shown above
- Customer info is in CUSTOMER_DIMENSION table
- Loan details are in CL_DETAIL_FACT table  
- Customer types are in CUSTOMER_TYPE_DESCRIPTION column
- Risk ratings are in OFFICER_RISK_RATING_DESC column
- Industry codes are in PRIMARY_INDUSTRY_CODE column
- Loan balances are in CURRENT_PRINCIPAL_BALANCE column
"""
    
    # Save schema context
    output_file = "text_2_sql/data_dictionary_output/exact_schema_context.txt"
    with open(output_file, 'w') as f:
        f.write(schema_context)
    
    conn.close()
    
    print(f"✅ Exact schema context created: {output_file}")
    print(f"Schema includes {len(tables)} tables with precise column names")
    
    return output_file

if __name__ == "__main__":
    create_exact_schema_context()