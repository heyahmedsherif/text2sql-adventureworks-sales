#!/usr/bin/env python
"""
Fix schema file to include column_names_original field that AutoGen expects
"""
import json
import os

def fix_schema_file():
    """Add missing column_names_original field to schema"""
    
    schema_file = 'text_2_sql/data_dictionary_output/tables.json'
    
    # Read current schema
    with open(schema_file, 'r') as f:
        schema_data = json.load(f)
    
    # Get the schema object (it's in a list)
    schema = schema_data[0]
    
    print("🔧 Fixing AutoGen schema file...")
    print(f"Current keys: {list(schema.keys())}")
    
    # Add column_names_original if missing
    if 'column_names_original' not in schema:
        print("Adding missing 'column_names_original' field...")
        # Copy column_names to column_names_original
        schema['column_names_original'] = schema['column_names'].copy()
    
    # Add table_names_original if missing
    if 'table_names_original' not in schema:
        print("Adding missing 'table_names_original' field...")
        # Copy table_names to table_names_original
        schema['table_names_original'] = schema['table_names'].copy()
    
    # Ensure we have the proper foreign key relationship
    # Find CUSTOMER_KEY columns for the foreign key
    customer_key_indices = []
    for i, (table_idx, col_name) in enumerate(schema['column_names']):
        if col_name == "CUSTOMER_KEY" and table_idx >= 0:
            customer_key_indices.append((i, table_idx))
    
    if len(customer_key_indices) >= 2:
        # Create foreign key: CL_DETAIL_FACT.CUSTOMER_KEY -> CUSTOMER_DIMENSION.CUSTOMER_KEY
        # Find which is which based on table index
        customer_dim_idx = None
        cl_detail_idx = None
        
        for col_idx, table_idx in customer_key_indices:
            table_name = schema['table_names'][table_idx]
            if table_name == "CUSTOMER_DIMENSION":
                customer_dim_idx = col_idx
            elif table_name == "CL_DETAIL_FACT":
                cl_detail_idx = col_idx
        
        if customer_dim_idx and cl_detail_idx:
            schema['foreign_keys'] = [[cl_detail_idx, customer_dim_idx]]
            print(f"Added foreign key: CL_DETAIL_FACT.CUSTOMER_KEY ({cl_detail_idx}) -> CUSTOMER_DIMENSION.CUSTOMER_KEY ({customer_dim_idx})")
    
    # Write back the fixed schema
    with open(schema_file, 'w') as f:
        json.dump(schema_data, f, indent=2)
    
    print("✅ Schema file fixed!")
    print(f"Final keys: {list(schema.keys())}")
    
    # Verify the fix
    print("\n🔍 Verification:")
    print(f"Tables: {schema['table_names']}")
    print(f"Foreign keys: {schema['foreign_keys']}")
    print(f"Column names original length: {len(schema['column_names_original'])}")

if __name__ == "__main__":
    fix_schema_file()