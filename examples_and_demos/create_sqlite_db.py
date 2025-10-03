#!/usr/bin/env python
"""
Create SQLite database from CSV files
"""
import sqlite3
import pandas as pd
import os
from pathlib import Path

def create_sqlite_database():
    """Create SQLite database from CSV files"""
    print("=== CREATING SQLITE DATABASE FROM CSV FILES ===")
    
    # Database path
    db_path = "/Users/ahmedm4air/Documents/fis/data/fis_database.db"
    csv_dir = "/Users/ahmedm4air/Documents/fis/data/csv"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    
    # Get all CSV files
    csv_files = list(Path(csv_dir).glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files")
    
    tables_created = []
    
    for csv_file in csv_files:
        try:
            print(f"Processing: {csv_file.name}")
            
            # Read tab-delimited files with error handling
            df = pd.read_csv(
                csv_file, 
                sep='\t', 
                dtype=str, 
                na_values=[''], 
                keep_default_na=False,
                quoting=3,  # QUOTE_NONE
                on_bad_lines='skip',  # Skip problematic lines
                engine='python'  # More flexible parsing
            )
            
            # Clean column names (remove spaces, special chars)
            df.columns = df.columns.str.strip()
            
            # Table name from filename (remove .csv extension)
            table_name = csv_file.stem
            
            # Convert empty strings to None for better SQL handling
            df = df.replace('', None)
            
            # Write to SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            tables_created.append(table_name)
            print(f"✅ Created table: {table_name} ({len(df)} rows, {len(df.columns)} columns)")
            
        except Exception as e:
            print(f"❌ Failed to process {csv_file.name}: {e}")
    
    # Create some basic indexes for performance
    try:
        cursor = conn.cursor()
        
        # Add indexes on common key fields
        key_columns = ['CUSTOMER_KEY', 'PRODUCT_KEY', 'MONTH_ID', 'INVESTOR_KEY', 'OWNER_KEY']
        
        for table in tables_created:
            for col in key_columns:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_{col} ON {table}({col})")
                except:
                    pass  # Column might not exist in this table
        
        conn.commit()
        print("✅ Created indexes for key columns")
        
    except Exception as e:
        print(f"⚠️  Index creation failed: {e}")
    
    # Display database summary
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n=== DATABASE SUMMARY ===")
    print(f"Database created: {db_path}")
    print(f"Total tables: {len(tables)}")
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} rows")
    
    conn.close()
    
    return db_path

if __name__ == "__main__":
    db_path = create_sqlite_database()
    print(f"\n🎉 SQLite database ready: {db_path}")