#!/usr/bin/env python
"""
Test SQLite database connection for Text2SQL
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv('text_2_sql/.env')

def test_sqlite_connection():
    """Test SQLite database connection"""
    print("=== TESTING SQLITE DATABASE CONNECTION ===")
    
    db_path = os.getenv('Text2Sql__Sqlite__Database')
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ Connection successful!")
        print(f"Found {len(tables)} tables:")
        
        for table in tables[:10]:  # Show first 10 tables
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")
        
        # Test a sample query from your banking data
        print(f"\n=== SAMPLE DATA ===")
        cursor.execute("SELECT CUSTOMER_NAME, CUSTOMER_TYPE_DESCRIPTION FROM CUSTOMER_DIMENSION LIMIT 5")
        customers = cursor.fetchall()
        
        print("Sample customers:")
        for customer in customers:
            print(f"  - {customer[0]} ({customer[1]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_sqlite_connection()