@echo off
title OceanSpill - Marine Decision Support System
color 0B
echo.
echo  ============================================
echo   OceanSpill - AI-Powered Oil Spill Detection
echo   Marine Decision Support System
echo  ============================================
echo.

cd /d "%~dp0"

REM ── Create virtual environment if missing ────────────────
if not exist "venv\Scripts\activate.bat" (
    echo  [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo  [ERROR] Failed to create virtual environment.
        echo  Make sure Python 3.10+ is installed and in your PATH.
        pause
        exit /b 1
    )
    echo  [SETUP] Virtual environment created.
    echo.
)

REM ── Install dependencies if needed ──────────────────────
if not exist "venv\Lib\site-packages\fastapi" (
    echo.
    echo  [SETUP] Installing Python dependencies...
    echo  This may take a few minutes on first run.
    echo  ------------------------------------------------
    call venv\Scripts\activate.bat
    echo.
    echo  Downloading: web framework, data tools, AI/ML,
    echo  computer vision, reporting, and alert modules...
    echo.
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo.
        echo  [ERROR] Failed to install dependencies.
        echo  Check your internet connection and try again.
        pause
        exit /b 1
    )
    echo.
    echo  ------------------------------------------------
    echo  [SETUP] All dependencies installed successfully.
    echo.
)

REM ── Activate virtual environment ──────────────────────────
call venv\Scripts\activate.bat

REM ── Build frontend if not built ───────────────────────────
if not exist "frontend\dist\index.html" (
    echo [SETUP] Building frontend...
    cd frontend
    if exist "node_modules" (
        call npm run build
    ) else (
        call npm ci
        call npm run build
    )
    cd ..
    echo [SETUP] Frontend built.
    echo.
) else (
    echo [OK] Frontend already built.
)

REM ── Start the server ─────────────────────────────────────
echo.
echo  Starting server on http://localhost:8000 ...
echo  (Close this window or press Ctrl+C to stop the server)
echo.
start "OceanSpill Server" cmd /k python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

REM ── Wait for the server to actually be ready ─────────────
echo.
echo  Waiting for the server to start...
echo  (First launch loads the AI model - this can take 30-60 seconds)
echo.
set /a tries=0

:check_server
timeout /t 2 /nobreak >nul
set /a tries+=1

curl -s -o nul http://localhost:8000/
if not errorlevel 1 goto server_ready

if %tries% geq 45 (
    echo.
    echo  [ERROR] Server did not start within 90 seconds.
    echo  Look at the "OceanSpill Server" window for the error message.
    echo  Common causes:
    echo    - Port 8000 is already in use by another program.
    echo    - A previous server is still running. Close it first.
    echo    - The model file is missing from the repository.
    echo.
    pause
    exit /b 1
)

goto check_server

:server_ready
echo.
echo  Server is ready. Opening your browser...
start http://localhost:8000
echo.
echo  Server is running. You can close this window.
echo.
pause
