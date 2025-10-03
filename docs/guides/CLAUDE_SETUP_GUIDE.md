# 🤖 Using Claude (Anthropic) Instead of OpenAI

## Quick Setup

Your Text2SQL system now supports **Claude (Anthropic)** as the LLM provider!

### Step 1: Get API Keys

You'll need **TWO** API keys:

1. **Anthropic API Key** (for Claude completions)
   - Get it from: https://console.anthropic.com/
   - Used for: Text2SQL generation, AI-powered queries

2. **OpenAI API Key** (for embeddings only)
   - Get it from: https://platform.openai.com/api-keys
   - Used for: Vector embeddings (Claude doesn't support embeddings yet)

### Step 2: Configure `.env` File

Edit `text_2_sql/.env`:

```bash
# Set provider to Claude
LLM_PROVIDER=claude

# Add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

# Add your OpenAI key (for embeddings only)
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Override Claude models (defaults are good)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MINI_MODEL=claude-3-5-haiku-20241022
```

### Step 3: Restart the App

```bash
# Kill current app
pkill -f "streamlit run"

# Restart
streamlit run unified_text2sql_streamlit.py --server.port 8501
```

## What Works with Claude

| Feature | Claude Support | Notes |
|---------|---------------|-------|
| **Pattern Matching** | ✅ Full | Works perfectly |
| **AI-Powered SQL** | ✅ Full | Uses Claude for generation |
| **AutoGen Multi-Agent** | ⚠️ Limited | Still uses OpenAI (AutoGen limitation) |
| **Embeddings** | ❌ Uses OpenAI | Claude has no embeddings API yet |

## Model Mapping

When you use Claude, the system automatically maps models:

| Internal Name | Claude Model | Use Case |
|---------------|--------------|----------|
| `4o-mini` | claude-3-5-haiku-20241022 | Fast, cheap queries |
| `4o` | claude-3-5-sonnet-20241022 | Complex, accurate queries |

## Cost Comparison

### Claude Pricing (as of 2024)
- **Claude 3.5 Haiku**: ~$0.80 per 1M input tokens, $4 per 1M output tokens
- **Claude 3.5 Sonnet**: ~$3 per 1M input tokens, $15 per 1M output tokens

### OpenAI Pricing (for comparison)
- **GPT-4o-mini**: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
- **GPT-4o**: ~$2.50 per 1M input tokens, $10 per 1M output tokens

**For embeddings** (still uses OpenAI):
- **text-embedding-3-small**: ~$0.02 per 1M tokens

## Why Claude?

1. **✅ Better reasoning** - Excellent for complex SQL generation
2. **✅ Longer context** - 200K tokens vs OpenAI's 128K
3. **✅ More accurate** - Often better at following instructions
4. **⚠️ More expensive** - Costs more per token than GPT-4o-mini

## Switching Between Providers

### Use Claude (Current Default)
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-openai-key  # For embeddings
```

### Use OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
# No ANTHROPIC_API_KEY needed
```

### Use Both (Advanced)
```bash
# Main queries use Claude
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your-claude-key

# AutoGen multi-agent uses OpenAI
OPENAI_API_KEY=your-openai-key
```

## Troubleshooting

### "ANTHROPIC_API_KEY required"
**Solution**: Add your Anthropic API key to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### "OPENAI_API_KEY required for embeddings"
**Solution**: Even with Claude, you need OpenAI for embeddings:
```bash
OPENAI_API_KEY=sk-xxxxx
```

### "AutoGen only supports OpenAI"
**Info**: This is expected. The AutoGen multi-agent system still uses OpenAI. Main Text2SQL queries will use Claude.

### API Key Format
- **Anthropic**: Starts with `sk-ant-api03-`
- **OpenAI**: Starts with `sk-proj-` or `sk-`

## Testing Your Setup

```bash
# Run validation
python test_open_source_setup.py

# Try a simple query
# 1. Start app
streamlit run unified_text2sql_streamlit.py

# 2. Select "Pattern Matching" or "AI-Powered" mode
# 3. Ask: "What is our total loan portfolio value?"
# 4. Should work with Claude!
```

## Claude Models Available

### Production Recommended
- **claude-3-5-sonnet-20241022** - Best balance of speed/quality
- **claude-3-5-haiku-20241022** - Fast and cheap

### Advanced (Optional)
- **claude-3-opus-20240229** - Highest quality, slowest, most expensive
- **claude-3-sonnet-20240229** - Previous gen Sonnet
- **claude-3-haiku-20240307** - Previous gen Haiku

## API Rate Limits

### Anthropic (Free Tier)
- **Requests**: 5 requests/minute
- **Tokens**: 25,000 tokens/day
- **Upgrade**: https://console.anthropic.com/settings/plans

### OpenAI (Free Tier)
- **Requests**: 3 requests/minute
- **Tokens**: Depends on model

💡 **Tip**: Get paid plans for production use!

## Example `.env` Configuration

```bash
# Database
Text2Sql__DatabaseEngine=SQLITE
Text2Sql__Sqlite__Database=/path/to/your/database.db

# LLM Provider
LLM_PROVIDER=claude

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# OpenAI API (for embeddings)
OPENAI_API_KEY=sk-xxxxx

# Claude Models (optional)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MINI_MODEL=claude-3-5-haiku-20241022

# Embeddings
OpenAI__EmbeddingModel=text-embedding-3-small
```

## Support

Need help?
1. Check error messages in terminal
2. Verify API keys are correct
3. Check API key formats
4. Review this guide
5. Check Anthropic documentation: https://docs.anthropic.com/

---

**You're all set to use Claude!** 🚀

Get your API keys and start using one of the best LLMs for Text2SQL!
