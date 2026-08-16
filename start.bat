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

:: ================================================
:: Download AI Model (Git LFS)
:: ================================================
echo.
echo [INFO] Checking AI model file...
if exist "models\fine_tuned\best_model.pth" (
    :: Check if it's an LFS pointer (small file = pointer)
    for %%F in ("models\fine_tuned\best_model.pth") do set "MODEL_SIZE=%%~zF"
    if %MODEL_SIZE% LSS 1000000 (
        echo [WARN] Model file appears to be a Git LFS pointer (%MODEL_SIZE% bytes)
        echo [INFO] Downloading actual model from Git LFS...

        :: Try to install git-lfs if not present
        git lfs version >nul 2>&1
        if %errorlevel% neq 0 (
            echo [INFO] Git LFS not found, attempting to install...
            winget install --id GitHub.GitLFS --silent --accept-source-agreements --accept-package-agreements 2>nul
            if %errorlevel% neq 0 (
                choco install git-lfs -y 2>nul
                if %errorlevel% neq 0 (
                    scoop install git-lfs 2>nul
                )
            )
            :: Refresh PATH
            git lfs version >nul 2>&1
        )

        :: Pull LFS files
        git lfs pull
        if %errorlevel% neq 0 (
            echo [WARN] git lfs pull failed, trying explicit fetch+checkout...
            git lfs fetch --all
            git lfs checkout
        )

        :: Verify download
        if exist "models\fine_tuned\best_model.pth" (
            for %%F in ("models\fine_tuned\best_model.pth") do set "NEW_SIZE=%%~zF"
            if %NEW_SIZE% GTR 1000000 (
                echo [SUCCESS] Model downloaded (%NEW_SIZE% bytes)
            ) else (
                echo [ERROR] Model download failed - file still too small (%NEW_SIZE% bytes)
                echo.
                echo Manual fix: Run these commands in terminal:
                echo   git lfs install
                echo   git lfs pull
                pause
                exit /b 1
            )
        ) else (
            echo [ERROR] Model file not found after LFS pull
            pause
            exit /b 1
        )
    ) else (
        echo [OK] Model file exists (%MODEL_SIZE% bytes)
    )
) else (
    echo [WARN] Model file not found, attempting Git LFS pull...
    git lfs pull
    if %errorlevel% neq 0 (
        git lfs fetch --all
        git lfs checkout
    )
    if not exist "models\fine_tuned\best_model.pth" (
        echo [ERROR] Model file missing after LFS pull
        pause
        exit /b 1
    )
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