# 🏦 FIS Banking Text2SQL System - Open Source Edition

[![Open Source](https://img.shields.io/badge/Open-Source-success)]()
[![No Azure Required](https://img.shields.io/badge/Azure-Not%20Required-blue)]()
[![LLM Flexible](https://img.shields.io/badge/LLM-Flexible-orange)]()

A comprehensive FIS Banking Text2SQL application that runs **completely without Azure dependencies**! Use OpenAI API, local LLMs, or any OpenAI-compatible service.

## 🚀 Quick Start (Open Source Version)

### Prerequisites
- Python 3.9+
- OpenAI API key (or use local LLMs - see below)
- SQLite database (or other supported databases)

### Super Quick Setup

```bash
# 1. Activate your conda environment
conda activate text2sql

# 2. Run the setup script
./setup_open_source.sh

# 3. Edit .env file and add your OpenAI API key
nano text_2_sql/.env
# Add: OPENAI_API_KEY=sk-your-actual-key-here

# 4. Run the app
streamlit run unified_text2sql_streamlit.py --server.port 8501
```

### Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp text_2_sql/.env.example text_2_sql/.env

# 3. Edit text_2_sql/.env and add:
OPENAI_API_KEY=sk-your-openai-key-here
Text2Sql__DatabaseEngine=SQLITE
Text2Sql__Sqlite__Database=/path/to/your/database.db

# 4. Run
streamlit run unified_text2sql_streamlit.py --server.port 8501
```

## 🌟 What's Different from Azure Version?

| Component | Azure Version | Open Source Version |
|-----------|---------------|---------------------|
| **LLM Provider** | Azure OpenAI only | OpenAI API, Local LLMs (Ollama, LocalAI), OpenRouter, etc. |
| **Vector Store** | Azure AI Search ($250+/month) | ChromaDB (free, local) |
| **Authentication** | Managed Identity, complex setup | Simple API key |
| **Cost** | ~$300-500/month minimum | Pay-per-use or $0 with local LLMs |
| **Setup Time** | Hours (Azure resources) | Minutes (just API key) |
| **Privacy** | Cloud-based | Can be 100% local |

## 💰 Cost Comparison

### Azure Setup
- Azure OpenAI: ~$0.03-0.06 per 1K tokens
- Azure AI Search: ~$250/month minimum
- Total: **~$300-500/month**

### OpenAI API Setup
- OpenAI API: ~$0.15-0.60 per 1M tokens
- ChromaDB: Free (local)
- Total: **~$10-50/month** for typical usage

### Local LLM Setup
- Ollama/LocalAI: Free (runs on your hardware)
- ChromaDB: Free (local)
- Total: **$0/month** (just electricity)

## 🔧 LLM Provider Options

### 1. OpenAI API (Recommended for Getting Started)

```bash
# In text_2_sql/.env
OPENAI_API_KEY=sk-your-openai-key
OpenAI__CompletionDeployment=gpt-4o
OpenAI__MiniCompletionDeployment=gpt-4o-mini
```

**Pros**: Reliable, fast, great quality
**Cons**: Pay per use (~$10-50/month)

### 2. Local LLMs with Ollama (Best for Privacy)

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3

# Configure .env
OPENAI_API_KEY=dummy-key
OPENAI_BASE_URL=http://localhost:11434/v1
OpenAI__CompletionDeployment=llama3
OpenAI__MiniCompletionDeployment=llama3
```

**Pros**: Free, private, no internet required
**Cons**: Requires GPU, slower than cloud

### 3. OpenRouter (Access to Many Models)

```bash
# In text_2_sql/.env
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OpenAI__CompletionDeployment=anthropic/claude-3.5-sonnet
```

**Pros**: Access to Claude, GPT-4, Llama, etc.
**Cons**: Requires internet, pay per use

### 4. LocalAI (Local + GPU Accelerated)

```bash
# Setup LocalAI (see https://localai.io)
# Configure .env
OPENAI_API_KEY=dummy-key
OPENAI_BASE_URL=http://localhost:8080/v1
OpenAI__CompletionDeployment=gpt-4
```

**Pros**: Fast, local, GPU accelerated
**Cons**: Complex setup, requires GPU

## 📦 Key Components

### Vector Store: ChromaDB
- **No cloud costs**: Runs locally
- **Persistent storage**: Data saved in `./chroma_db`
- **Fast retrieval**: Optimized for embeddings
- **Easy migration**: Drop-in replacement for Azure AI Search

### LLM Integration
- **Flexible**: Works with any OpenAI-compatible API
- **Configurable**: Change models via environment variables
- **Cached**: Supports query caching for speed

### Multi-Agent System
- **AutoGen powered**: Same 7-agent architecture
- **Works with all LLMs**: OpenAI, local, or cloud
- **Intelligent routing**: Auto-selects best approach

## 🎯 Features

All features from Azure version work identically:

- ✅ **Pattern Matching**: Instant responses for common queries
- ✅ **AI-Powered SQL**: Dynamic SQL generation
- ✅ **AutoGen Multi-Agent**: 7-agent collaborative system
- ✅ **MLflow Tracking**: Experiment tracking and analytics
- ✅ **User Feedback**: Rating and improvement system
- ✅ **Query Caching**: Fast repeated queries
- ✅ **Schema Search**: Intelligent schema selection

## 🔐 Security & Privacy

### With Local LLMs
- **100% Private**: All data stays on your machine
- **No API calls**: No external dependencies
- **HIPAA/SOC2 Ready**: Full data control

### With Cloud APIs
- **Encrypted**: All API calls use HTTPS
- **No training**: OpenAI doesn't train on API data
- **Key rotation**: Easy to rotate API keys

## 📊 Performance

| Operation | Azure OpenAI | OpenAI API | Ollama (Local) |
|-----------|--------------|------------|----------------|
| Pattern Match | <100ms | <100ms | <100ms |
| Simple SQL | ~1-2s | ~1-2s | ~3-5s |
| Complex (AutoGen) | ~5-10s | ~5-10s | ~15-30s |
| Embedding | ~500ms | ~500ms | ~2s |

## 🛠️ Troubleshooting

### "OPENAI_API_KEY not found"
```bash
# Make sure it's in text_2_sql/.env
echo "OPENAI_API_KEY=sk-your-key" >> text_2_sql/.env
```

### ChromaDB errors
```bash
# Create directory and set permissions
mkdir -p chroma_db
chmod 755 chroma_db
```

### Model not found
```bash
# Update model names in .env to match your provider
# For OpenAI:
OpenAI__CompletionDeployment=gpt-4o
OpenAI__MiniCompletionDeployment=gpt-4o-mini

# For Ollama:
OpenAI__CompletionDeployment=llama3
OpenAI__MiniCompletionDeployment=llama3
```

## 📚 Documentation

- **[Migration Guide](OPEN_SOURCE_MIGRATION_GUIDE.md)**: Complete migration from Azure
- **[Main README](README.md)**: Full system documentation
- **[MLOps Guide](MLFLOW_MLOPS_README.md)**: MLflow tracking
- **[Pattern Matching](PATTERN_MATCHING_GUIDE.md)**: Add custom patterns

## 🚢 Deployment Options

### Local Development
```bash
streamlit run unified_text2sql_streamlit.py
```

### Docker (Coming Soon)
```bash
docker-compose up
```

### Cloud Deployment
- Deploy to any cloud with Python support
- No Azure-specific dependencies
- Works on AWS, GCP, DigitalOcean, etc.

## 💡 Use Cases

### Perfect For:
- ✅ Cost-sensitive projects
- ✅ Privacy-critical applications
- ✅ On-premise deployments
- ✅ Development and testing
- ✅ No Azure account available

### Migration Path:
1. Start with OpenAI API (easy, cheap)
2. Test and validate
3. Move to local LLMs for production (free, private)

## 🤝 Contributing

This open source version is maintained alongside the Azure version. Contributions welcome!

## 📝 License

Same license as original project (MIT/Microsoft Open Source)

---

## ⭐ Why Open Source Version?

1. **No Vendor Lock-in**: Switch providers anytime
2. **Lower Costs**: 10x cheaper or completely free
3. **Privacy First**: 100% local option available
4. **Faster Setup**: Minutes instead of hours
5. **More Flexibility**: Use any LLM provider
6. **Community Driven**: Open source components

---

**Ready to get started?** Run `./setup_open_source.sh` and you'll be up in minutes! 🚀

For detailed migration instructions, see [OPEN_SOURCE_MIGRATION_GUIDE.md](OPEN_SOURCE_MIGRATION_GUIDE.md)
