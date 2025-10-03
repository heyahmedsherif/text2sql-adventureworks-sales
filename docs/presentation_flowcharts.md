# 🏦 FIS Banking Text2SQL - Visual Flowcharts and Azure Architecture

## **Approach 1: Pattern Matching Flowchart**

```
┌─────────────────────┐
│   User Question     │
│ "How many customers │
│   do we have?"      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Pattern Recognition│
│      Engine         │
│                     │
│ • "how many customers"
│ • "total loan"      │
│ • "risk rating"     │
│ • "delinquent"      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Pattern Match?    │
│                     │
│    ✓ Found Match    │
│    ✗ No Match       │
└──────┬──────────────┘
       │              
       ▼              
┌─────────────────────┐
│  Pre-built SQL      │
│    Execution        │
│                     │
│ SELECT COUNT(*)     │
│ FROM CUSTOMER_      │
│ DIMENSION           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   SQLite Database   │
│   (Local/Cloud)     │
│                     │
│ • Customer Data     │
│ • Loan Portfolio    │
│ • Risk Ratings      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Results         │
│                     │
│ Customer Count: 4449│
│                     │
│ ⚡ Response: <1 sec  │
└─────────────────────┘
```

### **Azure Services Used - Pattern Matching**
```
┌─────────────────────────────────────────┐
│           NO AZURE SERVICES             │
│                                         │
│  ✓ Local SQLite Database               │
│  ✓ Pattern Recognition (Local Logic)   │
│  ✓ Pre-defined SQL Queries            │
│                                         │
│  💰 Cost: $0 per query                │
│  ⚡ Speed: <1 second                   │
│  🎯 Accuracy: 100% for 8 patterns     │
└─────────────────────────────────────────┘
```

---

## **Approach 2: AI-Powered Flowchart**

```
┌─────────────────────┐
│   User Question     │
│ "Show me loan trends│
│ by customer segment"│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   Azure OpenAI     │    │   Azure AI Search   │
│   GPT-4o-mini      │◄───┤  Schema Retrieval   │
│                    │    │                     │
│ • Natural Language │    │ • Database Tables   │
│ • SQL Generation   │    │ • Column Metadata   │
│ • Banking Context  │    │ • Relationships     │
└──────────┬─────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   SQL Query         │
│   Generation        │
│                     │
│ SELECT c.SEGMENT,   │
│ AVG(l.BALANCE),     │
│ COUNT(*) FROM...    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Query Execution   │
│                     │
│ • SQLite Database   │
│ • Result Formatting │
│ • Error Handling    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Results         │
│                     │
│ • Loan Trends Table │
│ • Formatted Output  │
│ ⚡ Response: 2-5 sec │
└─────────────────────┘
```

### **Azure Services Used - AI-Powered**
```
┌─────────────────────────────────────────────────────────────┐
│                    AZURE SERVICES STACK                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧠 AZURE OPENAI SERVICE                                   │
│     ├── Endpoint: fisopenaipoc.openai.azure.com           │
│     ├── Model: GPT-4o-mini                                 │
│     ├── Function: SQL Generation + Banking Context         │
│     └── Cost: ~$0.01-0.03 per query                       │
│                                                             │
│  🔍 AZURE AI SEARCH                                        │
│     ├── Schema Store Index                                 │
│     ├── Semantic Search Enabled                            │
│     ├── Function: Database Context Retrieval               │
│     └── Cost: ~$0.01-0.02 per query                       │
│                                                             │
│  🗄️ LOCAL DATABASE                                         │
│     ├── SQLite (fis_database.db)                          │
│     ├── Banking Tables & Relationships                     │
│     └── Query Execution Layer                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  💰 Total Cost: ~$0.02-0.05 per query                     │
│  ⚡ Performance: 2-5 seconds                               │
│  🎯 Flexibility: Handles novel questions                   │
└─────────────────────────────────────────────────────────────┘
```

---

## **Approach 3: AutoGen Multi-Agent Flowchart**

```
┌─────────────────────┐
│   User Question     │
│"Comprehensive risk  │
│analysis across all │
│    portfolios"      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│  User Message       │    │   Query Cache       │
│  Rewrite Agent      │◄───┤     Agent           │
│                     │    │                     │
│ • Clarify Intent    │    │ • Check Previous    │
│ • Optimize Question │    │ • Similar Queries   │
│ • Add Context       │    │ • Performance Boost │
└──────────┬──────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│  Schema Selection   │    │   Azure AI Search   │
│      Agent          │◄───┤  Multiple Indexes   │
│                     │    │                     │
│ • Identify Tables   │    │ • Schema Store      │
│ • Find Relationships│    │ • Column Values     │
│ • Select Columns    │    │ • Query Cache       │
└──────────┬──────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│ Parallel Query      │    │   Azure OpenAI      │
│ Solving Agent       │◄───┤   GPT-4o-mini       │
│                     │    │                     │
│ • Generate SQL      │    │ • Multiple Agents   │
│ • Validate Syntax   │    │ • Specialized Roles │
│ • Test Queries      │    │ • Smart Reasoning   │
└──────────┬──────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   Query Execution   │
│   & Validation      │
│                     │
│ • Run SQL Queries   │
│ • Verify Results    │
│ • Error Correction  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   Answer Agent      │    │   State Store       │
│                     │◄───┤   (Memory)          │
│ • Format Results    │    │                     │
│ • Add Explanations  │    │ • Conversation      │
│ • Generate Follow-ups│    │ • Context History   │
└──────────┬──────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   Rich Results      │
│                     │
│ • Comprehensive     │
│   Analysis          │
│ • Explanations      │
│ • Follow-up         │
│   Suggestions       │
│ ⚡ Response: 5-15s  │
│   (1-3s if cached)  │
└─────────────────────┘
```

### **Azure Services Used - AutoGen Multi-Agent (Full Stack)**
```
┌─────────────────────────────────────────────────────────────┐
│                 COMPLETE AZURE AI STACK                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧠 AZURE OPENAI SERVICE (Multi-Model)                     │
│     ├── Endpoint: fisopenaipoc.openai.azure.com           │
│     ├── Models: GPT-4o-mini (multiple deployments)        │
│     ├── Agents: 4+ specialized AI agents                   │
│     ├── Function: Advanced reasoning & SQL generation      │
│     └── Cost: ~$0.03-0.08 per query                       │
│                                                             │
│  🔍 AZURE AI SEARCH (Triple Index System)                  │
│     ├── Schema Store Index (Database Structure)            │
│     ├── Query Cache Index (Performance Optimization)       │
│     ├── Column Value Store (Sample Data Context)           │
│     ├── Semantic Search + Vector Search                    │
│     ├── Function: Intelligent data retrieval               │
│     └── Cost: ~$0.02-0.05 per query                       │
│                                                             │
│  💾 AZURE STORAGE (State Management)                       │
│     ├── Account: fisdstoolkit                              │
│     ├── Containers: Multiple for caching & state           │
│     ├── Function: Conversation memory & performance        │
│     └── Cost: ~$0.01-0.02 per query                       │
│                                                             │
│  🔄 ADVANCED FEATURES                                       │
│     ├── Query Cache (Learning System)                      │
│     ├── State Store (Conversation Context)                 │
│     ├── Multi-Agent Orchestration                          │
│     └── Intelligent Result Validation                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  💰 Total Cost: ~$0.06-0.15 per query                     │
│  ⚡ Performance: 5-15s (1-3s cached)                       │
│  🎯 Intelligence: Highest accuracy & context               │
│  🧠 Learning: Improves with usage                          │
└─────────────────────────────────────────────────────────────┘
```

---

## **Smart Auto Mode Decision Tree**

```
                    ┌─────────────────────┐
                    │   User Question     │
                    │     Analysis        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Question Pattern   │
                    │     Detection       │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Simple Pattern │  │ Complex Keywords│  │  Default Route  │
│     Match       │  │    Detected     │  │                 │
│                 │  │                 │  │                 │
│ "how many"      │  │ "analysis"      │  │ Standard        │
│ "total loan"    │  │ "compare"       │  │ Questions       │
│ "risk rating"   │  │ "correlation"   │  │                 │
│ "delinquent"    │  │ "trend"         │  │                 │
└─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ PATTERN MATCH   │  │ AUTOGEN MULTI-  │  │   AI-POWERED    │
│    APPROACH     │  │ AGENT APPROACH  │  │    APPROACH     │
│                 │  │                 │  │                 │
│ ⚡ <1 second    │  │ 🧠 5-15 seconds │  │ 🎯 2-5 seconds  │
│ 💰 $0          │  │ 💰 $0.06-0.15   │  │ 💰 $0.02-0.05   │
│ 🎯 100% accuracy│  │ 🔍 Comprehensive│  │ ⚖️ Balanced     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## **Overall Azure Architecture Map**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FIS BANKING TEXT2SQL ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  👤 BUSINESS USERS                                                          │
│     │                                                                       │
│     ▼                                                                       │
│  🌐 STREAMLIT WEB APPLICATION                                               │
│     │                                                                       │
│     ▼                                                                       │
│  🧠 SMART ROUTING LAYER                                                     │
│     ├── Pattern Match (Local Processing)                                    │
│     ├── AI-Powered (Azure OpenAI + AI Search)                             │
│     └── AutoGen Multi-Agent (Full Azure Stack)                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                            AZURE SERVICES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🧠 AZURE OPENAI SERVICE                                                   │
│     ├── fisopenaipoc.openai.azure.com                                     │
│     ├── GPT-4o-mini (SQL Generation)                                       │
│     ├── Text-embedding-ada-002 (Vector Search)                            │
│     └── Multi-Agent Deployments                                            │
│                                                                             │
│  🔍 AZURE AI SEARCH SERVICE                                                │
│     ├── fisaisearchpoc.search.windows.net                                 │
│     ├── Schema Store Index                                                 │
│     ├── Query Cache Index                                                  │
│     ├── Column Value Store Index                                           │
│     └── Semantic + Vector Search                                           │
│                                                                             │
│  💾 AZURE STORAGE ACCOUNT                                                  │
│     ├── fisdstoolkit.blob.core.windows.net                               │
│     ├── State Management                                                   │
│     ├── Query Caching                                                      │
│     └── Conversation History                                               │
│                                                                             │
│  🗄️ DATABASE LAYER                                                         │
│     ├── SQLite (Local Development)                                         │
│     ├── Azure SQL (Production Ready)                                       │
│     └── Managed Identity Authentication                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              SECURITY                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔐 AUTHENTICATION & AUTHORIZATION                                         │
│     ├── System-Assigned Managed Identity                                   │
│     ├── User-Assigned Managed Identity                                     │
│     ├── API Key Fallback                                                   │
│     └── Role-Based Access Control (RBAC)                                   │
│                                                                             │
│  🛡️ DATA PROTECTION                                                        │
│     ├── Data never leaves Azure tenant                                     │
│     ├── Encrypted in transit and at rest                                   │
│     ├── Audit trails for all queries                                       │
│     └── Compliance with banking regulations                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## **Performance & Cost Comparison**

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│    APPROACH     │  RESPONSE TIME  │   COST/QUERY    │   USE CASE      │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│                 │                 │                 │                 │
│ Pattern Match   │    < 1 sec      │      $0.00      │ Common Banking  │
│                 │      ⚡⚡⚡       │       💰        │ Questions       │
│                 │                 │                 │                 │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│                 │                 │                 │                 │
│ AI-Powered      │    2-5 sec      │  $0.02-$0.05   │ Flexible        │
│                 │      ⚡⚡        │      💰💰       │ Business        │
│                 │                 │                 │ Questions       │
│                 │                 │                 │                 │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│                 │                 │                 │                 │
│ AutoGen Multi-  │   5-15 sec      │  $0.06-$0.15   │ Complex         │
│ Agent           │  (1-3 cached)   │      💰💰💰     │ Analysis &      │
│                 │      ⚡         │                 │ Insights        │
│                 │                 │                 │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```
