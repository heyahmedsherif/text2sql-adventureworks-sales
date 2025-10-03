# 🎯 How to Add Pattern Matching Queries - Step-by-Step Guide

## 📍 Overview
This guide shows you exactly how to add new queries to the pattern matching system in the FIS Banking Text2SQL application.

---

## 🔍 Step 1: Locate the Pattern Matching Code

### **File to Edit:**
```
unified_text2sql_streamlit.py
```

### **Section to Find:**
Look for this section around **line 140**:
```python
# Pattern matching queries (Fast approach)
PATTERN_QUERIES = {
    "how many customers": "SELECT COUNT(*) as customer_count FROM CUSTOMER_DIMENSION",
    "total loan": "SELECT SUM(CURRENT_PRINCIPAL_BALANCE) as total_balance FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
    # ... more patterns
}
```

---

## 🛠 Step 2: Add Your New Pattern

### **Current Structure:**
```python
PATTERN_QUERIES = {
    "pattern_key": "SQL_QUERY",
    "another_pattern": "ANOTHER_SQL_QUERY",
    # Add your new pattern here
}
```

### **How to Add a New Pattern:**

#### **Example: Adding "loan count" pattern**

**BEFORE:**
```python
PATTERN_QUERIES = {
    "how many customers": "SELECT COUNT(*) as customer_count FROM CUSTOMER_DIMENSION",
    "total loan": "SELECT SUM(CURRENT_PRINCIPAL_BALANCE) as total_balance FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
    "active loans": "SELECT COUNT(*) as active_loan_count FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0"
}
```

**AFTER:**
```python
PATTERN_QUERIES = {
    "how many customers": "SELECT COUNT(*) as customer_count FROM CUSTOMER_DIMENSION",
    "total loan": "SELECT SUM(CURRENT_PRINCIPAL_BALANCE) as total_balance FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
    "loan count": "SELECT COUNT(*) as loan_count FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",  # ← NEW PATTERN
    "active loans": "SELECT COUNT(*) as active_loan_count FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0"
}
```

### **Syntax Rules:**
1. **Pattern Key**: Short phrase users might say (lowercase)
2. **SQL Query**: Valid SQL that returns data
3. **Comma**: Don't forget the comma after each entry
4. **Quotes**: Use double quotes for keys, can use triple quotes for multi-line SQL

---

## 📝 Step 3: Write Your SQL Query

### **Template:**
```python
"your_pattern_key": "SELECT column_name as alias FROM table_name WHERE condition"
```

### **Examples of Good Patterns:**

#### **Simple Count Query:**
```python
"branch count": "SELECT COUNT(DISTINCT BRANCH_ID) as branch_count FROM CUSTOMER_DIMENSION"
```

#### **Simple Sum Query:**
```python
"past due total": "SELECT SUM(PAST_DUE_AMOUNT) as total_past_due FROM CL_DETAIL_FACT WHERE PAST_DUE_AMOUNT > 0"
```

#### **Multi-line Query with JOIN:**
```python
"customer loans": """SELECT c.CUSTOMER_NAME, COUNT(*) as loan_count, SUM(l.CURRENT_PRINCIPAL_BALANCE) as total_balance
                    FROM CUSTOMER_DIMENSION c
                    JOIN CL_DETAIL_FACT l ON c.CUSTOMER_KEY = l.CUSTOMER_KEY
                    WHERE l.CURRENT_PRINCIPAL_BALANCE > 0
                    GROUP BY c.CUSTOMER_KEY, c.CUSTOMER_NAME
                    ORDER BY total_balance DESC
                    LIMIT 10"""
```

---

## 🎨 Step 4: Update Example Questions (Optional)

### **File Section to Find:**
Look for this section around **line 636**:
```python
# Comprehensive example questions
example_questions = [
    "",
    # Pattern matching examples
    "How many customers do we have?",
    "What is our total loan portfolio value?", 
    # Add your examples here
]
```

### **How to Add Examples:**
```python
example_questions = [
    "",
    # Pattern matching examples
    "How many customers do we have?",
    "What is our total loan portfolio value?",
    "How many loans do we have?",  # ← NEW EXAMPLE for "loan count" pattern
    "What's our total past due amount?",  # ← NEW EXAMPLE for "past due total" pattern
]
```

---

## 🧪 Step 5: Test Your Changes

### **Testing Process:**

#### **1. Save the File**
- Save `unified_text2sql_streamlit.py` after making changes

#### **2. Restart Streamlit**
```bash
# Stop current Streamlit (Ctrl+C)
# Then restart:
streamlit run unified_text2sql_streamlit.py
```

#### **3. Test the Pattern**
1. Go to the app in your browser
2. Type a question containing your pattern
3. Look for "⚡ Pattern Match - Instant response"

#### **4. Test Variations**
- "How many loans?" (should match "loan count")
- "What's the loan count?" (should match "loan count") 
- "Show me total past due" (should match "past due total")

---

## 📊 Step 6: Verify It Works

### **What You Should See:**

#### **Successful Pattern Match:**
```
⚡ Pattern Match - Instant response (0.01s)

📊 Results
[Your data table here]

📝 Rate This Response
○ 👍 Yes  ○ 👎 No
Comments: [text box]
```

#### **If Pattern Doesn't Match:**
- Question goes to AI-Powered or AutoGen instead
- Takes longer (2-15 seconds vs <1 second)
- Shows different success message

---

## 🎯 Complete Example: Adding "Average Loan Size"

### **Step 1: Identify the Need**
Users frequently ask: "What's our average loan size?"

### **Step 2: Write the SQL**
```sql
SELECT AVG(CURRENT_PRINCIPAL_BALANCE) as average_loan_size 
FROM CL_DETAIL_FACT 
WHERE CURRENT_PRINCIPAL_BALANCE > 0
```

### **Step 3: Choose Pattern Key**
Pattern key: `"average loan"` (already exists!) or `"loan size"`

### **Step 4: Add to PATTERN_QUERIES**
```python
PATTERN_QUERIES = {
    # ... existing patterns ...
    "loan size": "SELECT AVG(CURRENT_PRINCIPAL_BALANCE) as average_loan_size FROM CL_DETAIL_FACT WHERE CURRENT_PRINCIPAL_BALANCE > 0",
    # ... rest of patterns ...
}
```

### **Step 5: Add Example**
```python
example_questions = [
    # ... existing examples ...
    "What's our average loan size?",
    # ... rest of examples ...
]
```

### **Step 6: Test**
- Ask: "What's our average loan size?" → Should trigger Pattern Match
- Ask: "Show me the loan size" → Should trigger Pattern Match

---

## 🚨 Common Mistakes to Avoid

### **❌ Syntax Errors**
```python
# WRONG - Missing comma
PATTERN_QUERIES = {
    "pattern1": "SELECT * FROM table1"
    "pattern2": "SELECT * FROM table2"  # ← Missing comma above
}

# CORRECT
PATTERN_QUERIES = {
    "pattern1": "SELECT * FROM table1",  # ← Comma added
    "pattern2": "SELECT * FROM table2"
}
```

### **❌ SQL Errors**
```python
# WRONG - Invalid SQL
"bad pattern": "SELECT COUNT FROM table"  # ← Missing (*)

# CORRECT
"good pattern": "SELECT COUNT(*) as count FROM table"
```

### **❌ Pattern Key Issues**
```python
# WRONG - Too generic (matches everything)
"what is": "SELECT COUNT(*) FROM table"

# WRONG - Too specific (matches almost nothing)
"what is our total loan portfolio value in dollars": "SELECT SUM(...)"

# CORRECT - Just right
"loan portfolio": "SELECT SUM(...)"
```

---

## 📋 Quick Reference Template

### **Copy-Paste Template:**
```python
# Add this to PATTERN_QUERIES dictionary:
"your_pattern_key": "SELECT your_columns FROM your_table WHERE your_conditions",

# Add this to example_questions list:
"Your example question?",
```

### **Pattern Key Guidelines:**
- **2-3 words maximum**
- **Use terms users actually say**
- **Make it distinctive**
- **Keep it simple**

### **SQL Guidelines:**
- **Test the SQL first** in a database tool
- **Use meaningful column aliases** (`as count`, `as total_balance`)
- **Include WHERE clauses** to filter relevant data
- **Keep it fast** (simple queries only)

---

## ✅ Checklist

Before deploying your new pattern:

- [ ] Pattern key is 2-3 words
- [ ] SQL query tested and works
- [ ] Comma added after previous entry
- [ ] Example question added to dropdown
- [ ] File saved
- [ ] Streamlit restarted
- [ ] Pattern matching tested with variations
- [ ] Response time is under 1 second

---

Now you have the complete process to add your own pattern matching queries! The key is to identify frequently asked questions and create fast, simple SQL queries for them.