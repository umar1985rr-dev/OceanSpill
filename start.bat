@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

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

:: ================================================
:: Download AI Model (GitHub Release - Primary, Git LFS - Fallback)
:: ================================================
echo.
echo [INFO] Checking AI model file...

:: GitHub Release download URL
set "MODEL_URL=https://github.com/umar1985rr-dev/OceanSpill/releases/download/v1.0.0-model/best_model.pth"
set "MODEL_PATH=models\fine_tuned\best_model.pth"

if exist "%MODEL_PATH%" (
    :: Check if it's valid (not LFS pointer, >10MB)
    for %%F in ("%MODEL_PATH%") do set "MODEL_SIZE=%%~zF"
    if !MODEL_SIZE! GTR 10000000 (
        echo [OK] Model file exists (!MODEL_SIZE! bytes)
        goto :MODEL_DONE
    ) else (
        echo [WARN] Model file appears invalid/corrupt (!MODEL_SIZE! bytes)
        echo [INFO] Re-downloading from GitHub Release...
        goto :DOWNLOAD_MODEL
    )
) else (
    echo [INFO] Model file not found. Downloading from GitHub Release...
    goto :DOWNLOAD_MODEL
)

goto :MODEL_DONE

:DOWNLOAD_MODEL
:: Create directory if not exist
if not exist "models\fine_tuned" mkdir "models\fine_tuned"

echo [INFO] Downloading model (~98MB) from GitHub Release...
echo [INFO] URL: %MODEL_URL%

:: Download with curl (built into Windows 10 1803+)
curl -L -o "%MODEL_PATH%" "%MODEL_URL%" --progress-bar --retry 3 --retry-delay 5
if %errorlevel% neq 0 (
    echo [WARN] curl download failed. Trying Git LFS as fallback...
    git lfs pull
    if %errorlevel% neq 0 (
        git lfs fetch --all
        git lfs checkout
    )
)

:: Verify download
if exist "%MODEL_PATH%" (
    for %%F in ("%MODEL_PATH%") do set "NEW_SIZE=%%~zF"
    if !NEW_SIZE! GTR 10000000 (
        echo [SUCCESS] Model downloaded (!NEW_SIZE! bytes)
        goto :MODEL_DONE
    ) else (
        echo [ERROR] Model download failed - file too small (!NEW_SIZE! bytes)
        echo.
        echo Manual fix: Download from %MODEL_URL%
        pause
        exit /b 1
    )
) else (
    echo [ERROR] Model file not found after download
    pause
    exit /b 1
)

:MODEL_DONE
echo [DEBUG] Reached MODEL_DONE, continuing to frontend check...

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