# ⚡ Quick Start - Open Source Text2SQL

## 🚀 Get Running in 5 Minutes

### Step 1: Setup (2 minutes)
```bash
# Activate conda environment
conda activate text2sql

# Run automated setup
./setup_open_source.sh
```

### Step 2: Configure (1 minute)
```bash
# Edit .env file
nano text_2_sql/.env

# Add your OpenAI API key (required):
OPENAI_API_KEY=sk-your-actual-api-key-here

# Set database path (if using SQLite):
Text2Sql__DatabaseEngine=SQLITE
Text2Sql__Sqlite__Database=/path/to/your/database.db
```

### Step 3: Run (1 minute)
```bash
# Start the app
streamlit run unified_text2sql_streamlit.py --server.port 8501

# Open browser to http://localhost:8501
```

### Step 4: Test (1 minute)
1. Select a demo question from dropdown
2. Click "🔍 Process Query"
3. View results and provide feedback
4. Done! ✅

---

## 🔑 Environment Variables Quick Reference

### Required
```bash
OPENAI_API_KEY=sk-xxxxx          # Your OpenAI API key
Text2Sql__DatabaseEngine=SQLITE  # Or TSQL, Postgres, etc.
```

### Database (choose one)
```bash
# SQLite
Text2Sql__Sqlite__Database=/path/to/db.db

# PostgreSQL
Text2Sql__Postgres__ConnectionString=postgresql://...

# SQL Server
Text2Sql__Tsql__ConnectionString=Server=...;Database=...
```

### Optional (has good defaults)
```bash
OpenAI__CompletionDeployment=gpt-4o           # Default: gpt-4o
OpenAI__MiniCompletionDeployment=gpt-4o-mini  # Default: gpt-4o-mini
OpenAI__EmbeddingModel=text-embedding-3-small # Default
CHROMA_DB_PATH=./chroma_db                    # Default
```

---

## 🎯 LLM Provider Options

### Option 1: OpenAI (Recommended)
```bash
OPENAI_API_KEY=sk-xxxxx
# Done! Uses gpt-4o and gpt-4o-mini by default
```

### Option 2: Local LLM (Ollama)
```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3

# Then configure:
OPENAI_API_KEY=dummy-key  # Required but not used
OPENAI_BASE_URL=http://localhost:11434/v1
OpenAI__CompletionDeployment=llama3
OpenAI__MiniCompletionDeployment=llama3
```

### Option 3: OpenRouter (Multiple Models)
```bash
OPENAI_API_KEY=sk-or-v1-xxxxx
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OpenAI__CompletionDeployment=anthropic/claude-3.5-sonnet
OpenAI__MiniCompletionDeployment=anthropic/claude-3-haiku
```

---

## 🧪 Testing Your Setup

### Quick Test
```bash
python test_open_source_setup.py
```

**Expected Output:**
```
✅ ChromaDB imported successfully
✅ OpenAI client imported successfully
✅ OpenAI connector imported successfully
✅ ChromaDB search connector imported successfully
✅ MLflow imported successfully
✅ Streamlit imported successfully
✅ OpenAI API key configured
✅ ChromaDB working correctly
✅ All tests passed!
```

### Manual Test
1. Start app: `streamlit run unified_text2sql_streamlit.py`
2. Try pattern match: "How many customers do we have?"
3. Try AI-powered: "Show customers with high risk ratings"
4. Try AutoGen: "Analyze risk distribution in our portfolio"

---

## 💰 Cost Estimate

### OpenAI API
- **gpt-4o-mini**: $0.15 per 1M input tokens, $0.60 per 1M output tokens
- **Typical usage**: ~1-5M tokens/month
- **Estimated cost**: $10-50/month

### Local LLM (Ollama/LocalAI)
- **Cost**: $0/month (just electricity)
- **Requirement**: GPU recommended (8GB+ VRAM)

---

## 🐛 Common Issues

### "OPENAI_API_KEY not found"
```bash
# Check .env file exists
ls text_2_sql/.env

# Check key is set
grep OPENAI_API_KEY text_2_sql/.env

# Should see: OPENAI_API_KEY=sk-xxxxx
```

### "Module not found: chromadb"
```bash
pip install -r requirements.txt
```

### "Database connection failed"
```bash
# Check path in .env
grep Database text_2_sql/.env

# Verify file exists
ls /path/to/your/database.db
```

### App won't start
```bash
# Check conda environment
echo $CONDA_DEFAULT_ENV  # Should show: text2sql

# Reinstall if needed
pip install --force-reinstall streamlit openai chromadb
```

---

## 📚 Documentation

- **Full Guide**: [OPEN_SOURCE_MIGRATION_GUIDE.md](OPEN_SOURCE_MIGRATION_GUIDE.md)
- **Detailed README**: [README_OPEN_SOURCE.md](README_OPEN_SOURCE.md)
- **All Changes**: [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)
- **Original README**: [README.md](README.md)

---

## 🎉 Success Checklist

- [ ] Conda environment activated
- [ ] Dependencies installed (`./setup_open_source.sh`)
- [ ] OpenAI API key in `.env`
- [ ] Database path configured
- [ ] Tests passing (`python test_open_source_setup.py`)
- [ ] App running (`streamlit run unified_text2sql_streamlit.py`)
- [ ] Queries working (try demo questions)

---

## 📞 Need Help?

1. **Run test script**: `python test_open_source_setup.py`
2. **Check logs**: Look at terminal output
3. **Review docs**: See guides above
4. **Open issue**: GitHub with test results

---

**Remember**: No Azure account needed! Just OpenAI API key (or use local LLMs for $0/month) 🚀
