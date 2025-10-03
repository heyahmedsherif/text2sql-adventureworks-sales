# Text2SQL with Claude AI

Natural language to SQL query system powered by Anthropic's Claude. Ask questions in plain English and get executable SQL queries instantly.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Claude](https://img.shields.io/badge/Claude-3.0-orange.svg)

## Overview

This application transforms natural language questions into SQL queries using Claude AI. It features intelligent query processing, multi-database support, and an intuitive web interface.

**Key Capabilities:**
- Pattern matching for instant common queries
- AI-powered SQL generation for complex questions
- Multi-agent system for analytical workloads
- Support for SQLite, PostgreSQL, Snowflake, Databricks, and SQL Server

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/heyahmedsherif/text2sql-adventureworks-sales.git
cd text2sql-adventureworks-sales

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp text_2_sql/.env.example text_2_sql/.env
# Edit text_2_sql/.env and add your ANTHROPIC_API_KEY
```

### Run Locally

```bash
streamlit run unified_text2sql_streamlit.py
```

Open http://localhost:8501 in your browser.

### Deploy to Streamlit Cloud

See [deployment guide](docs/STREAMLIT_CLOUD_DEPLOYMENT.md) for step-by-step instructions.

## Example Usage

```
Q: "How many customers do we have?"
→ SELECT COUNT(*) FROM Customer

Q: "Show top 10 products by revenue"
→ SELECT ProductName, SUM(Revenue) FROM Products GROUP BY ProductName ORDER BY Revenue DESC LIMIT 10

Q: "What are our total sales this year?"
→ SELECT SUM(TotalDue) FROM SalesOrderHeader WHERE YEAR(OrderDate) = YEAR(GETDATE())
```

## Features

### Three Processing Modes

**Pattern Matching**
Instant responses for common queries using predefined templates.

**AI-Powered**
Claude generates SQL for complex questions with context awareness.

**Multi-Agent (AutoGen)**
Collaborative agents handle sophisticated analytical queries.

### Database Support

| Database | Status | Notes |
|----------|--------|-------|
| SQLite | ✅ Default | Ideal for development |
| PostgreSQL | ✅ Supported | Production ready |
| Snowflake | ✅ Supported | Data warehouse |
| Databricks | ✅ Supported | Lakehouse platform |
| SQL Server | ✅ Supported | Enterprise databases |

### Additional Features

- **Vector Search**: Semantic schema matching with ChromaDB
- **MLflow Integration**: Track query performance and metrics
- **Query Caching**: Reduce API calls and improve response times
- **Interactive UI**: Clean Streamlit interface with query history

## Configuration

### Basic Setup

Edit `text_2_sql/.env`:

```bash
# LLM Configuration
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your-api-key-here
CLAUDE_MODEL=claude-3-haiku-20240307

# Database
Text2Sql__DatabaseEngine=SQLITE
Text2Sql__Sqlite__Database=./data/AdventureWorks-sqlite.db
```

### Advanced Options

See [configuration guide](docs/guides/CLAUDE_SETUP_GUIDE.md) for:
- Custom model selection
- Database connection strings
- Performance tuning
- Vector store configuration

## Project Structure

```
text2sql-adventureworks-sales/
├── unified_text2sql_streamlit.py   # Main application
├── mlflow_tracking.py              # Experiment tracking
├── text_2_sql/                     # Core engine
│   ├── text_2_sql_core/           # Database connectors
│   └── autogen/                    # Multi-agent system
├── data/                           # Sample databases
├── docs/                           # Documentation
└── requirements.txt                # Dependencies
```

## Documentation

- [Quick Start Guide](docs/guides/QUICK_START_OPEN_SOURCE.md)
- [Streamlit Cloud Deployment](docs/STREAMLIT_CLOUD_DEPLOYMENT.md)
- [Pattern Matching](docs/guides/PATTERN_MATCHING_GUIDE.md)
- [MLflow Integration](docs/guides/MLFLOW_MLOPS_README.md)

## Why Claude?

Claude offers significant advantages for SQL generation:

- **Advanced reasoning** for complex query logic
- **200K token context** for large database schemas
- **Accurate instruction following** reduces errors
- **Cost-effective** with the Haiku model

## API Rate Limits

**Free Tier:**
- 5 requests/minute
- 25,000 tokens/day

**Paid Tier:**
- Higher limits available
- See [Anthropic pricing](https://www.anthropic.com/pricing)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/) - AI model
- [Streamlit](https://streamlit.io/) - Web framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [MLflow](https://mlflow.org/) - Experiment tracking

## Support

- 📖 [Documentation](docs/guides/)
- 🐛 [Report Issues](https://github.com/heyahmedsherif/text2sql-adventureworks-sales/issues)
- 💬 [Discussions](https://github.com/heyahmedsherif/text2sql-adventureworks-sales/discussions)

---

**Made with Claude AI**
