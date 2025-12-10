@echo off
REM Startup script for Drishti AI Full Stack

echo ============================================
echo   Drishti AI - Full Stack Startup
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "drishti-env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv drishti-env
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call drishti-env\Scripts\activate.bat

REM Check if backend dependencies installed
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
)

echo.
echo Starting services...
echo.

REM Start MongoDB (if not running)
echo Starting MongoDB...
sc query MongoDB | find "RUNNING" >nul
if errorlevel 1 (
    echo MongoDB not running, attempting to start...
    sc start MongoDB
    timeout /t 3 >nul
)

REM Start Ollama (if not running)
echo Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if errorlevel 1 (
    echo Ollama not running, please start it manually:
    echo   ollama serve
    echo.
)

echo.
echo ============================================
echo   Backend starting on http://localhost:8080
echo   API Docs: http://localhost:8080/docs
echo ============================================
echo.
echo To stop: Press Ctrl+C
echo.

REM Start backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
