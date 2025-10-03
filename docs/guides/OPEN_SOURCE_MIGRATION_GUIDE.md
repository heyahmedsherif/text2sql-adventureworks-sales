# Open Source Migration Guide

## Overview

This system has been successfully migrated from Azure-specific services to open source alternatives. You can now run this Text2SQL system without any Azure dependencies!

## What Changed?

### 1. **Azure OpenAI → OpenAI API**
- **Before**: Azure OpenAI with managed identity authentication
- **After**: Standard OpenAI API with API key authentication
- **Alternative**: You can also use OpenAI-compatible APIs like:
  - OpenRouter (https://openrouter.ai)
  - LocalAI (for local LLMs)
  - Ollama with OpenAI compatibility layer
  - Any OpenAI-compatible endpoint

### 2. **Azure AI Search → ChromaDB**
- **Before**: Azure AI Search for vector storage and semantic search
- **After**: ChromaDB - open source vector database
- **Benefits**:
  - No cloud costs
  - Local-first storage
  - Easy to setup and use
  - Supports embeddings and metadata filtering

### 3. **Azure Document Intelligence → Optional OCR**
- **Before**: Azure Document Intelligence for PDF/image processing
- **After**: Optional pytesseract + pdf2image for OCR needs
- **Note**: Document processing is optional and only needed if you process PDFs

## Setup Instructions

### Step 1: Install Dependencies

```bash
# Activate your conda environment
conda activate text2sql

# Install updated requirements
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create or update `text_2_sql/.env` with the following:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: Override default models
OpenAI__CompletionDeployment=gpt-4o
OpenAI__MiniCompletionDeployment=gpt-4o-mini
OpenAI__EmbeddingModel=text-embedding-3-small

# Database Configuration
Text2Sql__DatabaseEngine=SQLITE
Text2Sql__Sqlite__Database=/full/path/to/your/database.db

# ChromaDB Configuration (optional - defaults work fine)
CHROMA_DB_PATH=./chroma_db
CHROMA_TEXT2SQL_SCHEMA_STORE=text2sql-schema-store
CHROMA_TEXT2SQL_QUERY_CACHE=text2sql-query-cache
CHROMA_TEXT2SQL_COLUMN_VALUE_STORE=text2sql-column-value-store

# AutoGen Configuration
SPIDER_DATA_DIR=/full/path/to/text_2_sql/data_dictionary_output
```

### Step 3: Update Code to Use ChromaDB (if using vector search)

If your code uses Azure AI Search, update imports:

```python
# Old (Azure)
from text_2_sql_core.connectors.ai_search import AISearchConnector

# New (ChromaDB)
from text_2_sql_core.connectors.chroma_search import ChromaSearchConnector
```

The API is nearly identical, so minimal code changes are needed.

### Step 4: Run the Application

```bash
# Start Streamlit app
streamlit run unified_text2sql_streamlit.py --server.port 8501

# Start MLflow (optional, in another terminal)
python mlflow_config.py ui
```

## Alternative LLM Providers

### Using OpenRouter (for access to multiple models)

```bash
# In .env file
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OpenAI__CompletionDeployment=anthropic/claude-3.5-sonnet
OpenAI__MiniCompletionDeployment=anthropic/claude-3-haiku
```

### Using Local LLMs with Ollama

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Enable OpenAI compatibility:

```bash
# In .env file
OPENAI_API_KEY=dummy-key  # Not used but required
OPENAI_BASE_URL=http://localhost:11434/v1
OpenAI__CompletionDeployment=llama3
OpenAI__MiniCompletionDeployment=llama3
```

### Using LocalAI (fully local, GPU-accelerated)

1. Setup LocalAI: https://localai.io
2. Configure:

```bash
# In .env file
OPENAI_API_KEY=dummy-key
OPENAI_BASE_URL=http://localhost:8080/v1
OpenAI__CompletionDeployment=gpt-4
```

## Cost Comparison

### Azure Setup (Before)
- Azure OpenAI: ~$0.03-0.06 per 1K tokens
- Azure AI Search: ~$250/month minimum
- Azure Document Intelligence: ~$1-10 per 1K pages
- **Total**: ~$300-500/month minimum

### Open Source Setup (After)
- OpenAI API: ~$0.15-0.60 per 1M tokens (gpt-4o-mini)
- ChromaDB: Free (local)
- OCR (if needed): Free (pytesseract)
- **Total**: Pay only for what you use, likely <$50/month for moderate usage

### Local LLM Setup (Fully Free)
- Ollama/LocalAI: $0 (one-time hardware cost only)
- ChromaDB: $0 (local)
- OCR: $0
- **Total**: $0/month (just electricity)

## Feature Compatibility

| Feature | Azure Version | Open Source Version | Status |
|---------|---------------|---------------------|--------|
| Text2SQL Generation | ✅ Azure OpenAI | ✅ OpenAI API | ✅ Full |
| Multi-Agent AutoGen | ✅ Azure OpenAI | ✅ OpenAI API | ✅ Full |
| Vector Search | ✅ Azure AI Search | ✅ ChromaDB | ✅ Full |
| Query Caching | ✅ Azure AI Search | ✅ ChromaDB | ✅ Full |
| Schema Storage | ✅ Azure AI Search | ✅ ChromaDB | ✅ Full |
| MLflow Tracking | ✅ Local | ✅ Local | ✅ Full |
| Document Processing | ✅ Azure DI | ⚠️ Optional pytesseract | ⚠️ Optional |

## Troubleshooting

### "OPENAI_API_KEY not found"
**Solution**: Make sure you've set the environment variable:
```bash
export OPENAI_API_KEY=sk-your-key-here
# Or add it to text_2_sql/.env file
```

### ChromaDB persistence issues
**Solution**: Ensure the CHROMA_DB_PATH directory exists and has write permissions:
```bash
mkdir -p ./chroma_db
chmod 755 ./chroma_db
```

### "Model not found" errors
**Solution**: Update model names in .env to match your provider:
```bash
# For OpenAI
OpenAI__CompletionDeployment=gpt-4o
OpenAI__MiniCompletionDeployment=gpt-4o-mini

# For Ollama
OpenAI__CompletionDeployment=llama3
OpenAI__MiniCompletionDeployment=llama3
```

## Benefits of Open Source Version

1. **No Vendor Lock-in**: Switch between OpenAI, local LLMs, or other providers easily
2. **Lower Costs**: Pay only for what you use, or run completely free with local LLMs
3. **Privacy**: Keep all data local with ChromaDB and local LLMs
4. **Flexibility**: Easy to customize and extend
5. **No Azure Account Needed**: No cloud setup, no managed identities, no resource groups

## Migration Checklist

- [ ] Install updated requirements.txt
- [ ] Set OPENAI_API_KEY in environment or .env file
- [ ] Update database paths in .env
- [ ] Remove old Azure-specific environment variables
- [ ] Test pattern matching queries
- [ ] Test AI-powered SQL generation
- [ ] Test AutoGen multi-agent system
- [ ] Verify MLflow tracking works
- [ ] (Optional) Setup local LLM if desired

## Support

For issues or questions:
1. Check this guide first
2. Review the main README.md
3. Open a GitHub issue
4. Check OpenAI/ChromaDB documentation

---

**Congratulations!** Your Text2SQL system is now fully open source and cloud-independent! 🎉
