#!/usr/bin/env python
"""
Generate correct schema file for AutoGen with proper case sensitivity
"""
import sqlite3
import os
import json
from dotenv import load_dotenv

def generate_spider_schema():
    load_dotenv('text_2_sql/.env')
    db_path = os.getenv('Text2Sql__Sqlite__Database')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Focus on main banking tables
    main_tables = ['CUSTOMER_DIMENSION', 'CL_DETAIL_FACT', 'LOAN_PRODUCT_DIMENSION']
    tables = [t for t in tables if t in main_tables]
    
    print(f"Creating schema for tables: {tables}")
    
    column_names = [[-1, "*"]]  # Start with wildcard
    column_types = ["text"]
    table_names = []
    
    column_index = 0
    table_index = 0
    
    for table in tables:
        table_names.append(table)
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        print(f"\nTable: {table}")
        for col in columns:
            column_index += 1
            col_name = col[1]  # Column name
            col_type = col[2].lower()  # Column type
            
            column_names.append([table_index, col_name])
            
            # Map SQLite types to standard types
            if 'int' in col_type:
                column_types.append('number')
            elif 'real' in col_type or 'float' in col_type or 'double' in col_type:
                column_types.append('number')
            else:
                column_types.append('text')
            
            print(f"  {col_name} ({col_type})")
        
        table_index += 1
    
    # Create Spider format schema
    schema = {
        "column_names": column_names,
        "column_types": column_types,
        "db_id": "fis_database",
        "foreign_keys": [
            # Add the main relationship: CUSTOMER_DIMENSION.CUSTOMER_KEY = CL_DETAIL_FACT.CUSTOMER_KEY
            # Find column indices for the foreign key relationship
        ],
        "primary_keys": [],
        "table_names": table_names
    }
    
    # Find foreign key indices
    customer_key_customer = None
    customer_key_cl = None
    
    for i, (table_idx, col_name) in enumerate(column_names[1:], 1):  # Skip wildcard
        if table_idx == 0 and col_name == "CUSTOMER_KEY":  # CUSTOMER_DIMENSION
            customer_key_customer = i
        elif table_idx == 1 and col_name == "CUSTOMER_KEY":  # CL_DETAIL_FACT
            customer_key_cl = i
    
    if customer_key_customer and customer_key_cl:
        schema["foreign_keys"] = [[customer_key_cl, customer_key_customer]]
        print(f"\nAdded foreign key: CL_DETAIL_FACT.CUSTOMER_KEY -> CUSTOMER_DIMENSION.CUSTOMER_KEY")
    
    # Save corrected schema
    with open('text_2_sql/data_dictionary_output/tables_corrected.json', 'w') as f:
        json.dump([schema], f, indent=2)
    
    print(f"\n✅ Generated corrected schema with {len(table_names)} tables and {len(column_names)-1} columns")
    print("✅ Saved to: text_2_sql/data_dictionary_output/tables_corrected.json")
    
    # Also backup and replace the original
    import shutil
    shutil.copy('text_2_sql/data_dictionary_output/tables.json', 'text_2_sql/data_dictionary_output/tables_backup.json')
    shutil.copy('text_2_sql/data_dictionary_output/tables_corrected.json', 'text_2_sql/data_dictionary_output/tables.json')
    print("✅ Backed up original and replaced with corrected schema")
    
    conn.close()
    
    return schema

if __name__ == "__main__":
    generate_spider_schema()