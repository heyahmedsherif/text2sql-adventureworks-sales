# 🚀 Streamlit Cloud Deployment Guide

This guide will help you deploy your Text2SQL app to Streamlit Cloud.

---

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Anthropic API Key** - Get it from [console.anthropic.com](https://console.anthropic.com/)

---

## 🔧 Step 1: Push to GitHub

```bash
# Make sure .env is not tracked
git rm --cached text_2_sql/.env 2>/dev/null || true

# Stage all files
git add .

# Commit
git commit -m "Initial commit: Text2SQL with Claude AI

- Migrated from Azure OpenAI to Claude (Anthropic)
- Added Streamlit Cloud secrets support
- Updated for AdventureWorks sample database
- Reorganized project structure

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Deploy to Streamlit Cloud

### A. Create New App

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository
4. Set **Main file path**: `unified_text2sql_streamlit.py`
5. Click **"Advanced settings"** (optional: choose Python version)

### B. Configure Secrets

1. In your app dashboard, click **"Settings"** (⚙️)
2. Select **"Secrets"** from the left menu
3. Copy the content from `.streamlit/secrets.toml.example`
4. Paste into the secrets editor
5. **Replace placeholder values** with your actual API keys:

```toml
# ============================================
# LLM PROVIDER CONFIGURATION
# ============================================
LLM_PROVIDER = "claude"

# ============================================
# CLAUDE (ANTHROPIC) API CONFIGURATION
# ============================================
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR-ACTUAL-KEY-HERE"

CLAUDE_MODEL = "claude-3-haiku-20240307"
CLAUDE_MINI_MODEL = "claude-3-haiku-20240307"

# ============================================
# OPENAI API (Optional)
# ============================================
OPENAI_API_KEY = "sk-placeholder"

OpenAI__CompletionDeployment = "gpt-4o"
OpenAI__MiniCompletionDeployment = "gpt-4o-mini"
OpenAI__EmbeddingModel = "text-embedding-3-small"

# ============================================
# DATABASE CONFIGURATION
# ============================================
Text2Sql__DatabaseEngine = "SQLITE"
Text2Sql__UseQueryCache = true
Text2Sql__PreRunQueryCache = true
Text2Sql__UseColumnValueStore = true
Text2Sql__GenerateFollowUpSuggestions = true
Text2Sql__RowLimit = 100

Text2Sql__Sqlite__Database = "./data/AdventureWorks-sqlite.db"

# ============================================
# CHROMADB VECTOR STORE
# ============================================
CHROMA_DB_PATH = "./chroma_db"
CHROMA_TEXT2SQL_SCHEMA_STORE = "text2sql-schema-store"
CHROMA_TEXT2SQL_QUERY_CACHE = "text2sql-query-cache"
CHROMA_TEXT2SQL_COLUMN_VALUE_STORE = "text2sql-column-value-store"
```

6. Click **"Save"**

### C. Deploy

1. Click **"Deploy!"**
2. Wait for the app to build (2-5 minutes)
3. Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## 🔍 Verification Checklist

After deployment, verify:

- ✅ App loads without errors
- ✅ Claude API connection works (check sidebar status)
- ✅ Database queries execute successfully
- ✅ Pattern matching works for common queries
- ✅ AI-Powered processing generates SQL correctly

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure all dependencies are in `requirements.txt`

```bash
# Regenerate requirements.txt if needed
pip freeze > requirements.txt
```

### Issue: Database file not found

**Solution**: Make sure `data/AdventureWorks-sqlite.db` is committed to your repo

```bash
# Check if database file exists
ls -lh data/AdventureWorks-sqlite.db

# If missing, download it
# (Add download instructions or provide download link)
```

### Issue: Claude API key not working

**Solution**:
1. Verify your API key at [console.anthropic.com](https://console.anthropic.com/)
2. Check Streamlit Cloud secrets are saved correctly
3. Restart the app from Streamlit Cloud dashboard

### Issue: "Secrets not found" error

**Solution**: The app code automatically loads secrets. If you see this error:
1. Go to app Settings > Secrets
2. Make sure all required keys are present
3. Click "Save" and restart the app

---

## 📊 Database Options

### Option 1: SQLite (Default)
- ✅ Simple and included in repo
- ✅ Works out-of-the-box
- ⚠️ Limited to small datasets (<100MB recommended)

### Option 2: PostgreSQL
Add to Streamlit secrets:
```toml
Text2Sql__DatabaseEngine = "POSTGRES"
Text2Sql__Postgres__ConnectionString = "postgresql://user:password@host:5432/db"
```

### Option 3: Snowflake
Add to Streamlit secrets:
```toml
Text2Sql__DatabaseEngine = "SNOWFLAKE"
Text2Sql__Snowflake__User = "username"
Text2Sql__Snowflake__Password = "password"
Text2Sql__Snowflake__Account = "account"
Text2Sql__Snowflake__Warehouse = "warehouse"
Text2Sql__Snowflake__Database = "database"
```

---

## 🔐 Security Best Practices

1. **Never commit secrets to GitHub**
   - ✅ `.env` is gitignored
   - ✅ `.streamlit/secrets.toml` is gitignored
   - ✅ Use Streamlit Cloud secrets manager only

2. **Use separate API keys for production**
   - Different key for development vs. production
   - Monitor usage at [console.anthropic.com](https://console.anthropic.com/)

3. **Set appropriate rate limits**
   - Claude free tier: 5 requests/min, 25K tokens/day
   - Consider upgrading for production use

4. **Database security**
   - Use read-only credentials when possible
   - Limit query row results (already set to 100)

---

## 🎯 Post-Deployment Steps

1. **Test all features:**
   - Pattern Matching queries
   - AI-Powered SQL generation
   - Different question types

2. **Share your app:**
   - Copy the Streamlit Cloud URL
   - Share with your team
   - Add to your documentation

3. **Monitor usage:**
   - Check Streamlit Cloud analytics
   - Monitor Claude API usage
   - Track query performance in MLflow (if configured)

---

## 🔄 Updating Your App

To deploy updates:

```bash
# Make your changes
git add .
git commit -m "Update: description of changes"
git push

# Streamlit Cloud will auto-deploy the changes
```

---

## 📞 Support

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Claude API Docs**: [docs.anthropic.com](https://docs.anthropic.com)

---

## ✅ Deployment Checklist

Before going live:

- [ ] GitHub repository is public or accessible to Streamlit Cloud
- [ ] All dependencies are in `requirements.txt`
- [ ] Database file is committed (if using SQLite)
- [ ] Anthropic API key is added to Streamlit secrets
- [ ] All secrets are configured correctly
- [ ] App deploys without errors
- [ ] All features tested and working
- [ ] Security best practices followed
- [ ] Documentation updated with app URL

---

**Your Text2SQL app is now live on Streamlit Cloud! 🎉**
