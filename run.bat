@echo off
REM Image Management & SEO Enhancement System - Launcher Script (Windows)

echo.
echo 🖼️  Image Management ^& SEO Enhancement System
echo ==============================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Virtual environment not found. Creating one...
    python -m venv venv
    echo ✅ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
    echo ✅ Dependencies installed
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  No .env file found. Creating from template...
    copy .env.example .env
    echo ✅ Created .env file. Please configure your AWS credentials in Settings.
    echo.
)

REM Start the application
echo 🚀 Starting Web UI...
echo 📍 Opening at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py
