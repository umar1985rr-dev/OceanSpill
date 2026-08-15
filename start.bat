@echo off
chcp 65001 >nul 2>&1
setlocal

echo.
echo ================================================
echo        OceanSpill Quick Start
echo ================================================
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.10+ from:
    echo https://www.python.org/downloads/
    echo.
    echo During installation, CHECK "Add Python to PATH"
    pause
    exit /b 1
)

:: Check if venv exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --quiet --upgrade pip

:: Install/upgrade requirements
echo [INFO] Installing Python dependencies...
python -m pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install Python dependencies
    echo Check your internet connection and try again.
    pause
    exit /b 1
)

:: Check if frontend is built
if not exist "frontend\dist\index.html" (
    echo.
    echo [INFO] Building frontend...
    cd frontend
    if not exist "node_modules" (
        echo [INFO] Installing npm packages...
        call npm install
        if %errorlevel% neq 0 (
            echo.
            echo [ERROR] npm install failed!
            echo.
            echo Solutions:
            echo 1. Install Node.js from https://nodejs.org/
            echo 2. Delete frontend\node_modules folder
            echo 3. Delete frontend\package-lock.json file
            echo 4. Run start.bat again
            cd ..
            pause
            exit /b 1
        )
    )
    call npm run build
    if %errorlevel% neq 0 (
        echo [WARN] Frontend build had issues but continuing...
    )
    cd ..
)

:: Start the server
echo.
echo ================================================
echo        Starting OceanSpill Server...
echo ================================================
echo.
echo   URL: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Press Ctrl+C to stop
echo ================================================
echo.

:: Open browser after short delay
timeout /t 3 /nobreak >nul
start "" http://localhost:8000

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

:: If server exits, pause so user can see any errors
pause