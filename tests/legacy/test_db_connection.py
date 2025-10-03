#!/usr/bin/env python
"""
Test Azure SQL Database connection with Microsoft Entra authentication
"""
import pyodbc
from dotenv import load_dotenv
import os
import subprocess
import json

# Load environment variables from text_2_sql/.env
load_dotenv('text_2_sql/.env')

def get_azure_token():
    """Get Azure access token using Azure CLI"""
    try:
        # Get token for SQL Database
        result = subprocess.run([
            'az', 'account', 'get-access-token', '--resource', 'https://database.windows.net/'
        ], capture_output=True, text=True, check=True)
        
        token_info = json.loads(result.stdout)
        return token_info['accessToken']
    except Exception as e:
        print(f"Failed to get Azure token: {e}")
        return None

def test_connection():
    print("=== TESTING AZURE SQL DATABASE CONNECTION ===")
    
    # Get connection details from environment
    database_name = os.getenv('Text2Sql__Tsql__Database')
    server_name = "fisinternal.database.windows.net"
    
    print(f"Database: {database_name}")
    print(f"Server: {server_name}")
    
    # Get Azure token
    print("Getting Azure access token...")
    token = get_azure_token()
    if not token:
        return False
    
    print("✓ Successfully obtained Azure access token")
    
    # Build connection string with token
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};Encrypt=Yes;TrustServerCertificate=No;Connection Timeout=30;"
    
    try:
        # Test connection with token
        print("Attempting to connect...")
        
        # Create connection with access token
        token_bytes = token.encode('utf-16-le')
        token_struct = struct.pack('<I', len(token_bytes)) + token_bytes
        
        conn_attrs = {
            1256: token_struct  # SQL_COPT_SS_ACCESS_TOKEN
        }
        
        conn = pyodbc.connect(connection_string, attrs_before=conn_attrs)
        
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
    import struct
    test_connection()