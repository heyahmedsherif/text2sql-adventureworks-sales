# 📁 Entity Matching/Relationship Files Location Guide

## 📋 Overview

This guide explains where the entity relationship and schema information is located in your FIS Banking Text2SQL system, how relationships are currently handled, and how to modify them if needed.

---

## 🎯 Primary Schema Files

### **1. Main Schema File**
```
/text_2_sql/data_dictionary_output/tables.json
```
- **Purpose**: Spider format schema used by AutoGen Multi-Agent system
- **Contains**: Column definitions, table names, data types, database structure
- **Format**: JSON format compatible with Spider text-to-SQL framework
- **Note**: `"foreign_keys": []` (currently empty - no explicit relationships defined)

### **2. Business Data Dictionary**
```
/text_2_sql/data_dictionary_output/banking_data_dictionary.json
```
- **Purpose**: Human-readable entity definitions and business context
- **Contains**: 
  - Entity descriptions with business purpose
  - Attribute definitions with data types
  - Business context for each table and column
- **Format**: Structured JSON with business-friendly descriptions

### **3. Exact Schema Context**
```
/text_2_sql/data_dictionary_output/exact_schema_context.txt
```
- **Purpose**: Complete column listing with real data examples
- **Contains**: 
  - All column names with exact casing
  - Data types for each column
  - Sample values from actual database
- **Format**: Plain text, human-readable

---

## 🔍 Current Database Structure

### **Tables Identified:**
1. **CUSTOMER_DIMENSION** - Customer information and risk ratings (116 columns)
2. **CL_DETAIL_FACT** - Loan/credit details and balances

### **Key Relationship Columns:**
- **CUSTOMER_KEY** - Appears in both tables, serves as the join key
- **Primary relationship**: `CUSTOMER_DIMENSION.CUSTOMER_KEY = CL_DETAIL_FACT.CUSTOMER_KEY`

---

## 🔗 How Relationships Are Currently Handled

### **❌ Missing Explicit Relationships**
Your current schema files **don't contain explicit foreign key relationships**. The `tables.json` shows:
```json
{
  "db_id": "fis_database",
  "table_names": ["CUSTOMER_DIMENSION", "CL_DETAIL_FACT"],
  "foreign_keys": [],  // ← Empty - no explicit relationships
  "column_names": [...],
  "column_types": [...]
}
```

### **✅ Implicit Relationships (Working Solution)**
Relationships are **inferred and hardcoded** in three ways:

#### **1. In Pattern Matching Queries:**
Relationships are **hardcoded in SQL** within the `PATTERN_QUERIES` dictionary:
```python
"top customers": """SELECT c.CUSTOMER_NAME, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_balance 
                   FROM CUSTOMER_DIMENSION c 
                   JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY 
                   WHERE l.CURRENT_PRINCIPAL_BALANCE > 0
                   GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME 
                   ORDER BY total_balance DESC LIMIT 5"""
```

#### **2. In AI-Powered Approach:**
The AI **infers relationships** based on:
- Column name similarities (`CUSTOMER_KEY` appears in both tables)
- Business context from the data dictionary
- Schema information provided in prompts

#### **3. In AutoGen Multi-Agent:**
The agents **intelligently discover relationships** using:
- Schema selection agent analyzes column names
- Query generation agent infers joins from context
- Column value store provides sample data for context

---

## 📊 Current Relationship Pattern

### **Primary Relationship:**
```sql
-- Customer to Loans relationship (One-to-Many)
CUSTOMER_DIMENSION.CUSTOMER_KEY = CL_DETAIL_FACT.CUSTOMER_KEY

-- Example usage in queries:
FROM CUSTOMER_DIMENSION c 
JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
```

### **Business Logic:**
- **One Customer** can have **Many Loans/Credit Lines**
- **CUSTOMER_KEY** serves as the linking field
- Most queries join these tables for comprehensive analysis

---

## 🛠 How to Add Explicit Relationships (Optional)

If you want to add explicit relationship definitions to improve AI accuracy:

### **1. Update tables.json**
Add foreign key definitions in Spider format:
```json
{
  "db_id": "fis_database",
  "table_names": ["CUSTOMER_DIMENSION", "CL_DETAIL_FACT"],
  "foreign_keys": [
    [
      [1, 1],  // Table 1 (CL_DETAIL_FACT), Column 1 (CUSTOMER_KEY)
      [0, 1]   // References Table 0 (CUSTOMER_DIMENSION), Column 1 (CUSTOMER_KEY)
    ]
  ],
  // ... rest of schema
}
```

### **2. Update banking_data_dictionary.json**
Add relationship descriptions:
```json
{
  "Entity": "CL_DETAIL_FACT",
  "Definition": "Loan details table. Related to CUSTOMER_DIMENSION via CUSTOMER_KEY.",
  "Relationships": [
    {
      "RelatedEntity": "CUSTOMER_DIMENSION",
      "RelationshipType": "Many-to-One",
      "JoinCondition": "CL_DETAIL_FACT.CUSTOMER_KEY = CUSTOMER_DIMENSION.CUSTOMER_KEY",
      "Description": "Each loan record belongs to one customer"
    }
  ],
  "Attributes": [...]
}
```

### **3. Update Schema Context**
Add relationship documentation to `exact_schema_context.txt`:
```
RELATIONSHIPS:
- CUSTOMER_DIMENSION → CL_DETAIL_FACT (One-to-Many)
  Join: CUSTOMER_DIMENSION.CUSTOMER_KEY = CL_DETAIL_FACT.CUSTOMER_KEY
  Business Rule: One customer can have multiple loans/credit lines
```

---

## 🎯 Recommended Approach

### **✅ Current System Works Well**
Your current **implicit relationship** approach is effective because:
- Pattern matching has optimized, tested SQL queries
- AI-powered approach successfully infers relationships from column names
- AutoGen agents intelligently discover table connections
- Performance is excellent with current approach

### **🤔 When to Add Explicit Relationships**
Consider adding explicit relationships if you want to:
- **Add more complex queries** to pattern matching
- **Improve AI accuracy** for unusual relationship patterns
- **Document relationships** formally for business users
- **Support additional tables** with non-obvious connections

### **💡 Best Practice**
For most use cases, **keep the current implicit approach** and add explicit relationships only when:
1. Adding new tables with unclear relationships
2. AI-generated queries are missing obvious joins
3. You need formal documentation for compliance/audit

---

## 📝 File Modification Examples

### **Adding a New Table Relationship**
If you add a new table (e.g., `BRANCH_DIMENSION`):

#### **1. Update Pattern Queries:**
```python
"branch customers": """SELECT b.BRANCH_NAME, COUNT(DISTINCT c.CUSTOMER_KEY) as customer_count
                      FROM BRANCH_DIMENSION b
                      JOIN CUSTOMER_DIMENSION c ON b.BRANCH_ID = c.BRANCH_ID
                      GROUP BY b.BRANCH_ID, b.BRANCH_NAME
                      ORDER BY customer_count DESC"""
```

#### **2. Update Schema Files:**
- Add table to `tables.json`
- Add entity to `banking_data_dictionary.json`  
- Update `exact_schema_context.txt`

---

## 🔍 Troubleshooting Relationship Issues

### **Problem: AI generates wrong joins**
**Solution**: Add explicit relationship in `tables.json` or improve column naming

### **Problem: Pattern matching needs new relationship**
**Solution**: Add new pattern with correct JOIN syntax

### **Problem: AutoGen misses obvious relationship**
**Solution**: Check that `CUSTOMER_KEY` column names match exactly

---

## 📚 Reference Files

### **Schema Files:**
- `text_2_sql/data_dictionary_output/tables.json` - Spider format schema
- `text_2_sql/data_dictionary_output/banking_data_dictionary.json` - Business context
- `text_2_sql/data_dictionary_output/exact_schema_context.txt` - Column listing

### **Code Files:**
- `unified_text2sql_streamlit.py` - Pattern matching queries (line ~140)
- `text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_schema_selection_agent.py` - Schema selection logic
- `text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py` - Schema retrieval logic

### **Sample Files:**
- `text_2_sql/sample_data_dictionary/sample_schema.json` - Example with relationships

---

## 💡 Summary

Your FIS Banking Text2SQL system uses **implicit relationships** that work effectively through:
- Hardcoded optimized SQL in pattern matching
- AI inference from column names and business context  
- Intelligent agent discovery in AutoGen

This approach provides excellent performance and accuracy while remaining flexible and maintainable. Explicit relationships are optional and should only be added when the current approach doesn't meet specific needs.

The relationship logic is currently embedded in your SQL queries and works effectively for the banking use case! 🏦