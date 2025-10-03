#!/usr/bin/env python
"""
Convert banking data dictionary to SPIDER format for AutoGen
"""
import json
import os
from pathlib import Path

def convert_to_spider_format():
    """Convert our banking data dictionary to SPIDER tables.json format"""
    print("=== CONVERTING TO SPIDER FORMAT ===")
    
    # Load our banking data dictionary
    banking_dict_file = Path("text_2_sql/data_dictionary_output/banking_data_dictionary.json")
    
    if not banking_dict_file.exists():
        print(f"❌ Banking data dictionary not found: {banking_dict_file}")
        return False
    
    with open(banking_dict_file, 'r') as f:
        banking_data = json.load(f)
    
    print(f"📋 Converting {len(banking_data)} tables to SPIDER format...")
    
    # Create SPIDER format structure
    spider_data = []
    
    db_entry = {
        "column_names": [[-1, "*"]],  # -1 is special for "*"
        "column_names_original": [[-1, "*"]],
        "column_types": ["text"],
        "db_id": "banking_db",
        "foreign_keys": [],
        "primary_keys": [],
        "table_names": [],
        "table_names_original": []
    }
    
    column_index = 1  # Start at 1 since 0 is "*"
    table_index = 0
    
    for entity in banking_data:
        table_name = entity["Entity"]
        table_description = entity["Definition"]
        
        # Add table
        db_entry["table_names"].append(table_name.lower())
        db_entry["table_names_original"].append(table_name)
        
        # Add columns for this table
        for attr in entity["Attributes"]:
            col_name = attr["Attribute"] 
            col_type = attr.get("DataType", "TEXT").lower()
            
            # Add to column lists
            db_entry["column_names"].append([table_index, col_name.lower()])
            db_entry["column_names_original"].append([table_index, col_name])
            
            # Map SQL types to SPIDER types
            if "int" in col_type or "key" in col_name.lower():
                spider_type = "number"
            elif "decimal" in col_type or "float" in col_type:
                spider_type = "number" 
            elif "date" in col_type or "time" in col_type:
                spider_type = "time"
            else:
                spider_type = "text"
                
            db_entry["column_types"].append(spider_type)
            
            # Check for primary keys
            if attr.get("IsPrimaryKey", False):
                db_entry["primary_keys"].append(column_index)
            
            # Check for foreign keys (basic detection)
            if col_name.upper().endswith("_KEY") and not attr.get("IsPrimaryKey", False):
                # This is likely a foreign key, but we'd need more info to map it properly
                # For now, we'll skip complex FK relationships
                pass
            
            column_index += 1
        
        table_index += 1
    
    spider_data.append(db_entry)
    
    # Save SPIDER format file
    output_file = Path("text_2_sql/data_dictionary_output/tables.json")
    
    with open(output_file, 'w') as f:
        json.dump(spider_data, f, indent=2)
    
    print(f"✅ SPIDER format created: {output_file}")
    print(f"   - Tables: {len(db_entry['table_names'])}")
    print(f"   - Columns: {len(db_entry['column_names']) - 1}")  # -1 for the "*" entry
    print(f"   - Primary Keys: {len(db_entry['primary_keys'])}")
    
    return True

if __name__ == "__main__":
    convert_to_spider_format()