# 🎯 PowerPoint-Ready Diagrams for FIS Text2SQL Presentation

## **Slide 1: Pattern Matching Approach**

### Simple Flowchart (Use Shapes + Arrows):
```
[User Question] → [Pattern Engine] → [Pre-built SQL] → [Database] → [Results]
   "How many        ↓                    ↓               ↓           ↓
   customers?"   8 Patterns         SELECT COUNT(*)   SQLite     <1 second
```

### Azure Services Box:
```
┌─────────────────────────────┐
│     NO AZURE SERVICES       │
│                             │
│  ✓ Local Processing Only    │
│  ✓ Zero Cloud Costs         │
│  ✓ Instant Results          │
└─────────────────────────────┘
```

---

## **Slide 2: AI-Powered Approach**

### Flowchart with Azure Icons:
```
[User Question] → [Azure OpenAI] ← [Azure AI Search]
      ↓               ↓                    ↓
"Show trends"    GPT-4o-mini         Schema Store
      ↓               ↓                    ↓
[Generated SQL] → [Database] → [Formatted Results]
```

### Azure Services Used:
```
🧠 Azure OpenAI
   • GPT-4o-mini model
   • SQL generation
   • $0.01-0.03/query

🔍 Azure AI Search  
   • Schema retrieval
   • Semantic search
   • $0.01-0.02/query
```

---

## **Slide 3: AutoGen Multi-Agent**

### Agent Workflow:
```
[User Question]
      ↓
[Message Rewrite Agent] ← [Query Cache]
      ↓
[Schema Selection Agent] ← [Azure AI Search]
      ↓
[Query Generation Agent] ← [Azure OpenAI]
      ↓
[Answer Agent] ← [State Store]
      ↓
[Rich Results + Follow-ups]
```

### Full Azure Stack:
```
🧠 Azure OpenAI (4+ Agents)
🔍 Azure AI Search (3 Indexes)
💾 Azure Storage (State)
🔄 Query Cache (Learning)
```

---

## **Slide 4: Smart Auto Decision Tree**

### Simple Decision Logic:
```
                [User Question]
                      ↓
             [Smart Detection]
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   [Simple]      [Analysis]    [Standard]
   Patterns      Keywords      Questions
        ↓             ↓             ↓
   [Pattern]     [AutoGen]    [AI-Powered]
    Match        Multi-Agent    
```

---

## **Slide 5: Azure Architecture Overview**

### High-Level Architecture:
```
👥 Business Users
        ↓
🌐 Streamlit App
        ↓
🧠 Smart Router
   ├── Pattern Match (Local)
   ├── AI-Powered (OpenAI + Search)  
   └── AutoGen (Full Stack)
        ↓
🏦 Banking Database
```

### Azure Services Stack:
```
🧠 Azure OpenAI Service
   └── fisopenaipoc.openai.azure.com

🔍 Azure AI Search
   └── fisaisearchpoc.search.windows.net

💾 Azure Storage
   └── fisdstoolkit.blob.core.windows.net

🔐 Managed Identity Security
```

---

## **Slide 6: Performance Comparison Table**

| Approach | Speed | Cost/Query | Best For |
|----------|-------|------------|----------|
| Pattern Match | <1 sec ⚡⚡⚡ | $0.00 💰 | Common questions |
| AI-Powered | 2-5 sec ⚡⚡ | $0.02-0.05 💰💰 | Flexible queries |
| AutoGen | 5-15 sec ⚡ | $0.06-0.15 💰💰💰 | Complex analysis |

---

## **PowerPoint Creation Tips:**

### **For Flowcharts:**
1. Use PowerPoint's SmartArt "Process" layouts
2. Replace text with our labels
3. Add Azure service icons from Microsoft's icon library
4. Use consistent colors (Azure blue theme)

### **For Azure Services:**
1. Download official Azure icons from Microsoft
2. Create boxes with service icons + descriptions
3. Use arrows to show data flow
4. Add cost/performance callouts

### **Color Scheme Suggestions:**
- **Primary**: Azure Blue (#0078D4)
- **Secondary**: Light Blue (#40E0D0)  
- **Accent**: Orange (#FF8C00) for highlights
- **Text**: Dark Gray (#333333)
- **Success**: Green (#107C10)

### **Icon Sources:**
- Microsoft Azure Architecture Icons
- Azure Service Icons (official Microsoft download)
- PowerPoint built-in icons (Insert > Icons > "Cloud")

### **Animation Suggestions:**
- Entrance: Fade in each step sequentially
- Emphasis: Pulse or glow for key services
- Path: Arrows flowing from step to step
- Exit: Fade out previous slides when advancing

---

## **Speaker Notes for Each Slide:**

### **Pattern Matching:**
"This is our fastest approach - when someone asks a common question like 'how many customers,' we instantly recognize the pattern and execute a pre-written, optimized SQL query. No Azure services needed, zero cost, sub-second response."

### **AI-Powered:**
"For more flexible questions, we use Azure OpenAI's GPT-4o-mini to generate custom SQL. The AI Search service provides database context, ensuring accurate queries. This handles novel questions while maintaining good performance."

### **AutoGen Multi-Agent:**
"Our most sophisticated approach uses multiple AI agents working together. Each agent has a specialized role - one rewrites questions, another selects schemas, another generates SQL, and a final agent formats results with explanations."

### **Smart Auto:**
"The system automatically chooses the best approach based on question complexity. Simple patterns go to pattern matching, analysis requests go to AutoGen, everything else uses AI-powered generation."

### **Architecture:**
"All Azure services stay within your tenant for security. We use managed identity for authentication, and the system scales automatically based on demand."

This structure gives you everything needed to create professional presentation slides that effectively communicate the technical sophistication while remaining business-friendly.