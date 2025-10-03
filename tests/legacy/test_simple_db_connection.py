#!/usr/bin/env python
"""
Test Azure SQL Database connection using simple connection string approach
"""
import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables from text_2_sql/.env
load_dotenv('text_2_sql/.env')

def test_connection():
    print("=== TESTING AZURE SQL DATABASE CONNECTION ===")
    
    # Get connection details from environment
    connection_string = os.getenv('Text2Sql__Tsql__ConnectionString')
    database_name = os.getenv('Text2Sql__Tsql__Database')
    
    print(f"Database: {database_name}")
    print(f"Connection string: {connection_string}")
    
    try:
        # Test connection
        print("Attempting to connect...")
        conn = pyodbc.connect(connection_string)
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        
        print("✓ Connection successful!")
        print(f"SQL Server Version: {version[0]}")
        
        # Get basic schema info
        cursor.execute("""
            SELECT 
                SCHEMA_NAME(t.schema_id) as schema_name,
                t.name as table_name,
                COUNT(c.column_id) as column_count
            FROM sys.tables t
            LEFT JOIN sys.columns c ON t.object_id = c.object_id
            GROUP BY t.schema_id, t.name
            ORDER BY schema_name, table_name
        """)
        
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables:")
        for table in tables[:10]:  # Show first 10 tables
            print(f"  - {table.schema_name}.{table.table_name} ({table.column_count} columns)")
        
        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more tables")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()