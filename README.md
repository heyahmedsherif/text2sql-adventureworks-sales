# 🤖 Text2SQL with Claude AI

A powerful Natural Language to SQL query system powered by **Claude (Anthropic)** AI models. Convert plain English questions into precise SQL queries with support for SQLite, PostgreSQL, Snowflake, Databricks, and more.

## ✨ Features

- **🎯 Smart Query Processing**: Three processing modes
  - Pattern Matching (instant responses for common queries)
  - AI-Powered SQL Generation (Claude-powered intelligent query creation)
  - AutoGen Multi-Agent System (complex analytical queries)

- **🤖 Claude AI Integration**: Primary LLM provider using Anthropic's Claude models
  - Claude 3 Haiku for fast, cost-effective queries
  - Claude 3 Sonnet/Opus for complex analytical tasks
  - Supports fallback to OpenAI if needed

- **📊 Multi-Database Support**:
  - SQLite (default, perfect for testing)
  - PostgreSQL
  - Snowflake
  - Databricks
  - T-SQL/SQL Server

- **🔍 Vector Search**: ChromaDB integration for semantic schema search

- **📈 MLflow Integration**: Track query performance and model usage

- **🎨 Beautiful Streamlit UI**: Interactive web interface

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Claude API key from [Anthropic Console](https://console.anthropic.com/)
- (Optional) OpenAI API key for embeddings

### Installation

\`\`\`bash
# Clone the repository
git clone <your-repo-url>
cd dstoolkit-text2sql-and-imageprocessing

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp text_2_sql/.env.example text_2_sql/.env
\`\`\`

### Configuration

Edit \`text_2_sql/.env\`:

\`\`\`bash
# === LLM Provider ===
LLM_PROVIDER=claude  # Use Claude as primary LLM

# === CLAUDE (ANTHROPIC) API CONFIGURATION ===
ANTHROPIC_API_KEY=your-claude-api-key-here

# Claude Models
CLAUDE_MODEL=claude-3-haiku-20240307  # Main model
CLAUDE_MINI_MODEL=claude-3-haiku-20240307  # Fast model

# === OPENAI API (Optional - for embeddings only) ===
OPENAI_API_KEY=sk-placeholder  # Only needed for vector embeddings

# === Database Configuration ===
Text2Sql__DatabaseEngine=SQLITE
Text2Sql__Sqlite__Database=./data/your-database.db
\`\`\`

### Run the Application

\`\`\`bash
streamlit run unified_text2sql_streamlit.py --server.port 8501
\`\`\`

Visit http://localhost:8501 in your browser!

## 📖 Documentation

- [Claude Setup Guide](docs/guides/CLAUDE_SETUP_GUIDE.md) - Detailed Claude configuration
- [Quick Start Guide](docs/guides/QUICK_START_OPEN_SOURCE.md) - Get started in 5 minutes
- [Streamlit Cloud Deployment](docs/STREAMLIT_CLOUD_DEPLOYMENT.md) - Deploy to Streamlit Cloud
- [Pattern Matching Guide](docs/guides/PATTERN_MATCHING_GUIDE.md) - Fast query patterns
- [MLflow MLOps Guide](docs/guides/MLFLOW_MLOPS_README.md) - Track and optimize queries

## 🎯 Example Queries

Try these with the AdventureWorks sample database:

\`\`\`
"How many customers do we have?"
"Show me the top 10 products by revenue"
"What are our total sales this year?"
"List customers who haven't ordered in 30 days"
\`\`\`

## 🏗️ Project Structure

\`\`\`
dstoolkit-text2sql-and-imageprocessing/
├── unified_text2sql_streamlit.py    # Main Streamlit app
├── text_2_sql/                      # Core Text2SQL engine
│   ├── text_2_sql_core/            # Database connectors & logic
│   └── autogen/                     # Multi-agent system
├── data/                            # Sample databases
├── docs/                            # Documentation
│   ├── guides/                      # Setup & usage guides
│   └── legacy/                      # Azure deployment docs (legacy)
├── tests/                           # Test files
└── requirements.txt                 # Python dependencies
\`\`\`

## 🔧 Configuration Options

### LLM Providers

**Claude (Recommended)**:
\`\`\`bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
CLAUDE_MODEL=claude-3-haiku-20240307
\`\`\`

**OpenAI (Alternative)**:
\`\`\`bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
\`\`\`

### Database Engines

Set \`Text2Sql__DatabaseEngine\` to one of:
- \`SQLITE\` - Local SQLite database (default)
- \`POSTGRES\` - PostgreSQL
- \`SNOWFLAKE\` - Snowflake Data Warehouse
- \`DATABRICKS\` - Databricks SQL
- \`TSQL\` - Microsoft SQL Server

## 💡 Why Claude?

- **✅ Superior reasoning** - Excellent for complex SQL generation
- **✅ Longer context** - 200K tokens vs OpenAI's 128K
- **✅ Better instruction following** - More accurate query generation
- **✅ Cost-effective** - Haiku model is fast and affordable

## 🔐 API Keys

### Get Your Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and paste into \`.env\` file

### Rate Limits

**Claude Free Tier**:
- 5 requests/minute
- 25,000 tokens/day

**Paid Tier**: Significantly higher limits

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI models
- **Microsoft** for the original Text2SQL framework
- **Streamlit** for the amazing UI framework

## 📞 Support

- 📖 [Documentation](docs/guides/)
- 🐛 Report Issues
- 💬 Discussions

---

**Built with ❤️ using Claude AI**
