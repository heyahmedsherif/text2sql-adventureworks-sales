@echo off
REM 🚀 FIS Banking Text2SQL Quick Start Script for Windows
REM This script helps novice users get the system running quickly

echo 🏦 FIS Banking Text2SQL System - Quick Start
echo ==============================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if we're in the right directory
if not exist "unified_text2sql_streamlit.py" (
    echo ❌ Please run this script from the dstoolkit-text2sql-and-imageprocessing directory
    echo    Current directory: %cd%
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check if .env file exists
if not exist "text_2_sql\.env" (
    echo ⚙️ Creating environment configuration file...
    if not exist "text_2_sql" mkdir text_2_sql
    (
        echo # Azure OpenAI Configuration
        echo OpenAI__Endpoint=https://your-openai-resource.openai.azure.com/
        echo OpenAI__ApiKey=your-api-key-here
        echo.
        echo # Database Configuration  
        echo Text2Sql__DatabaseEngine=SQLITE
        echo Text2Sql__Sqlite__Database=C:\path\to\your\fis_database.db
        echo.
        echo # Spider Data Directory ^(for AutoGen^)
        echo SPIDER_DATA_DIR=%cd%\text_2_sql\data_dictionary_output
    ) > text_2_sql\.env
    echo 📝 Created text_2_sql\.env file
    echo ⚠️  IMPORTANT: Edit text_2_sql\.env with your Azure OpenAI credentials and database path
    echo    - Update OpenAI__Endpoint with your Azure OpenAI resource URL
    echo    - Update OpenAI__ApiKey with your API key
    echo    - Update Text2Sql__Sqlite__Database with full path to your SQLite database
) else (
    echo ✅ Environment file already exists
)

echo.
echo 🎉 Setup Complete!
echo.
echo 📋 Next Steps:
echo 1. Edit text_2_sql\.env with your Azure OpenAI credentials
echo 2. Place your FIS database file and update the database path in .env
echo 3. Start the application:
echo.
echo    🖥️  Streamlit App:
echo    streamlit run unified_text2sql_streamlit.py --server.port 8501
echo.
echo    📊 MLflow Dashboard ^(optional^):
echo    python mlflow_config.py ui
echo.
echo 4. Open http://localhost:8501 in your browser
echo 5. Try demo questions and provide feedback!
echo.
echo 📚 Need help? Check out:
echo    - DEMO_QUESTIONS_FOR_STAKEHOLDERS.md
echo    - MLFLOW_MLOPS_README.md
echo.
echo 🚀 Happy querying!
echo.
pause