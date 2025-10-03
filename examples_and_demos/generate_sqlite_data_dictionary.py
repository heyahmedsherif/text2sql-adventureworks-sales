#!/usr/bin/env python
"""
Generate data dictionary for SQLite database
"""
import sqlite3
import json
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add text_2_sql_core to path
text_2_sql_path = Path(__file__).parent / "text_2_sql" / "text_2_sql_core" / "src"
sys.path.insert(0, str(text_2_sql_path))

load_dotenv('text_2_sql/.env')

async def generate_description(table_name, columns, openai_connector):
    """Generate AI description for a table"""
    try:
        # Create context about the table
        column_info = ", ".join([f"{col[1]} {col[2]}" for col in columns])
        
        messages = [
            {
                "role": "system", 
                "content": "You are a database expert. Generate a concise, helpful description (1-2 sentences) for this database table based on its name and columns. Focus on what business purpose this table serves."
            },
            {
                "role": "user", 
                "content": f"Table: {table_name}\nColumns: {column_info}\n\nGenerate a brief description of what this table contains and its business purpose."
            }
        ]
        
        description = await openai_connector.run_completion_request(messages, max_tokens=150)
        return description.strip()
        
    except Exception as e:
        print(f"⚠️  Failed to generate AI description for {table_name}: {e}")
        return f"Table containing {table_name.lower().replace('_', ' ')} information"

async def generate_column_description(table_name, column_name, column_type, openai_connector):
    """Generate AI description for a column"""
    try:
        messages = [
            {
                "role": "system", 
                "content": "You are a database expert. Generate a very brief description (5-10 words) for this database column based on its name and type."
            },
            {
                "role": "user", 
                "content": f"Table: {table_name}\nColumn: {column_name} ({column_type})\n\nGenerate a brief description:"
            }
        ]
        
        description = await openai_connector.run_completion_request(messages, max_tokens=50)
        return description.strip()
        
    except Exception as e:
        return f"{column_name.lower().replace('_', ' ')}"

async def create_data_dictionary():
    """Create data dictionary from SQLite database"""
    print("=== GENERATING SQLITE DATA DICTIONARY ===")
    
    # Get database path
    db_path = os.getenv('Text2Sql__Sqlite__Database')
    output_dir = Path("text_2_sql/data_dictionary_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Database: {db_path}")
    print(f"Output directory: {output_dir}")
    
    # Initialize OpenAI for descriptions
    from text_2_sql_core.connectors.open_ai import OpenAIConnector
    openai_connector = OpenAIConnector()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(tables)} tables")
    
    all_entities = []
    
    for table_name in tables:
        try:
            print(f"Processing table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Generate table description
            table_description = await generate_description(table_name, columns, openai_connector)
            
            # Process columns
            attributes = []
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                is_pk = col[5] == 1
                
                # Generate column description (limit to important columns to save API calls)
                if len(attributes) < 10:  # Only describe first 10 columns
                    col_description = await generate_column_description(table_name, col_name, col_type, openai_connector)
                else:
                    col_description = col_name.lower().replace('_', ' ')
                
                attributes.append({
                    "Attribute": col_name,
                    "DataType": col_type or "TEXT",
                    "Definition": col_description,
                    "IsPrimaryKey": is_pk
                })
            
            # Create entity entry
            entity = {
                "Entity": table_name,
                "EntitySchema": "main",
                "Definition": table_description,
                "Attributes": attributes
            }
            
            all_entities.append(entity)
            
            print(f"✅ {table_name}: {len(attributes)} columns")
            
        except Exception as e:
            print(f"❌ Failed to process {table_name}: {e}")
    
    # Save data dictionary
    output_file = output_dir / "banking_data_dictionary.json"
    
    with open(output_file, 'w') as f:
        json.dump(all_entities, f, indent=2)
    
    print(f"\n✅ Data dictionary created: {output_file}")
    print(f"Total entities: {len(all_entities)}")
    
    conn.close()
    
    return output_file

if __name__ == "__main__":
    asyncio.run(create_data_dictionary())