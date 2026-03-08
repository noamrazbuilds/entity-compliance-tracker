@echo off
echo ==========================================
echo   Entity Compliance Tracker
echo ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed.
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

:: Create virtual environment if needed
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies if needed
if not exist ".venv\.installed" (
    echo Installing dependencies (first run only)...
    pip install -q --upgrade pip
    pip install -q .
    echo. > .venv\.installed
    echo Dependencies installed.
)

:: Create data directory
if not exist "data" mkdir data

echo.
echo Starting services...
echo   API:      http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:8501
echo.
echo Press Ctrl+C or use the Shutdown button in the UI to stop.
echo.

:: Start API in background
start /B uvicorn ect_app.main:app --host 0.0.0.0 --port 8000

:: Wait for API
timeout /t 3 /nobreak >nul

:: Start Streamlit
start /B streamlit run ect_frontend/app.py --server.port 8501 --server.headless true

:: Wait a moment then open browser
timeout /t 3 /nobreak >nul
start http://localhost:8501

:: Keep window open — Ctrl+C or UI shutdown will terminate
echo Services are running. Close this window or use the UI Shutdown button to stop.
pause
