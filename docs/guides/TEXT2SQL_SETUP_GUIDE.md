# Text2SQL Setup and Testing Guide

## Current Status ✅

Your Text2SQL environment is now configured and ready for testing. Here's what has been completed:

### 1. Environment Configuration ✅
- **Azure OpenAI**: Configured with gpt-4o-mini deployment
- **Azure AI Search**: Configured with vector search capabilities  
- **Azure Storage**: Configured for data storage
- **Database Connection**: Configured for your Azure SQL Database "fis"

### 2. Infrastructure Deployment ✅
All Azure AI Search indexes have been successfully deployed:
- ✅ Text2SQL Schema Store (vector search for database schema)
- ✅ Text2SQL Query Cache (stores previous queries)
- ✅ Text2SQL Column Value Store (stores sample data)

### 3. Configuration Files ✅
- **Main config**: `deploy_ai_search_indexes/.env` - Azure services
- **Text2SQL config**: `text_2_sql/.env` - Application settings

## Next Steps for You to Complete

### Step 1: Generate Database Schema Dictionary

Run this command to generate a data dictionary from your Azure SQL database:

```bash
cd text_2_sql
conda activate claude-dstoolkit
python -m text_2_sql_core.data_dictionary.cli TSQL -o data_dictionary_output -gen
```

This will:
- Connect to your `fis` database 
- Extract all table schemas, columns, and relationships
- Use OpenAI to generate helpful descriptions for each table/column
- Save files to `data_dictionary_output/` folder

### Step 2: Upload Schema to AI Search

After generating the data dictionary, upload it to your schema store:

```bash
cd ../deploy_ai_search_indexes
python -c "
from src.deploy_ai_search_indexes.text_2_sql_schema_store import Text2SqlSchemaStoreAISearch
store = Text2SqlSchemaStoreAISearch()
store.upload_data_dictionary('../text_2_sql/data_dictionary_output/')
"
```

### Step 3: Test Text2SQL Queries

Now you can test natural language to SQL conversion:

```bash
cd ../text_2_sql
python -c "
from text_2_sql_core.connectors.factory import create_text_2_sql_connector
connector = create_text_2_sql_connector()
result = connector.ask('How many records are in the database?')
print(result)
"
```

## Testing Different Query Types

Try these example queries:

### Basic Queries
```python
# Count records
connector.ask("How many total records do we have?")

# Show tables
connector.ask("What tables are available in this database?")

# Simple aggregation  
connector.ask("What is the average value in the sales table?")
```

### Advanced Queries
```python
# Joins and filtering
connector.ask("Show me customers who placed orders in the last 30 days")

# Complex aggregations
connector.ask("What are the top 5 products by revenue this quarter?")

# Date-based analysis
connector.ask("Show monthly sales trends for the past year")
```

## Architecture Overview

Your setup includes:

1. **Schema Store**: Vector search over database schema with AI-generated descriptions
2. **Query Cache**: Remembers successful queries for faster responses  
3. **Column Value Store**: Sample data for better query context
4. **Azure OpenAI**: Powers the natural language understanding and SQL generation
5. **Database Connection**: Direct connection to your Azure SQL Database

## Troubleshooting

### Database Connection Issues
If you get connection errors, try:
1. Ensure you're logged into Azure CLI: `az login`
2. Set correct subscription: `az account set --subscription "MCAPS-Hybrid-AhmedSherif"`
3. Check firewall rules on your Azure SQL server
4. Verify you have db_datareader permissions on the 'fis' database

### Authentication Issues
The connection string uses `Authentication=ActiveDirectoryIntegrated` which should work with your Azure CLI login.

### Performance Tips
- The first query may be slower as it builds the semantic understanding
- Subsequent similar queries will be faster due to caching
- More specific queries generally work better than very broad ones

## File Locations

- **Main configuration**: `deploy_ai_search_indexes/.env`
- **Text2SQL configuration**: `text_2_sql/.env` 
- **Data dictionary output**: `text_2_sql/data_dictionary_output/`
- **Test scripts**: Root directory (`test_*.py`)

Your Text2SQL system is ready! Start with Step 1 above to generate your database schema dictionary.