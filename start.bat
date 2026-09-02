@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ================================================
:: OceanSpill Quick Start - Robust Version
:: ================================================
echo.
echo ================================================
echo        OceanSpill Quick Start
echo ================================================
echo.
echo [DEBUG] Script started
echo [DEBUG] Working directory: %~dp0
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
echo [DEBUG] Changed to: %CD%

:: ================================================
:: Check Python version (3.10-3.12 required)
:: ================================================
set "REQUIRED_MAJOR=3"
set "REQUIRED_MINOR_MIN=10"
set "REQUIRED_MINOR_MAX=12"
set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
set "PYTHON_INSTALLER_PATH=%TEMP%\python-3.12.7-amd64.exe"

:CHECK_PYTHON
set "PYTHON_OK=0"
set "PYTHON_CMD="
set "PY_FULL_VERSION="

where py >nul 2>&1
if not errorlevel 1 (
    for %%v in (3.12 3.11 3.10) do (
        py -%%v -c "import sys; print(sys.version.split()[0])" >nul 2>&1
        if !errorlevel! equ 0 (
            set "PYTHON_CMD=py -%%v"
            set "PY_FULL_VERSION=%%v"
            set "PYTHON_OK=1"
            goto :PYTHON_DETECTED
        )
    )
)

where python >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_FULL_VERSION=%%v"
    if not "!PY_FULL_VERSION!"=="" (
        for /f "tokens=1,2 delims=." %%a in ("!PY_FULL_VERSION!") do (
            set "PY_MAJOR=%%a"
            set "PY_MINOR=%%b"
        )
        if "!PY_MAJOR!"=="3" (
            if !PY_MINOR! geq 10 if !PY_MINOR! leq 12 (
                set "PYTHON_OK=1"
                set "PYTHON_CMD=python"
            )
        )
    )
)

:PYTHON_DETECTED
if !PYTHON_OK! equ 1 (
    echo [OK] Python detected: !PY_FULL_VERSION!
    goto :PYTHON_READY
)

echo.
echo [WARN] Required Python 3.10-3.12 was not found on this system.
echo.
choice /C YN /M "Do you want to download and install Python 3.12 now? (Y=Yes, N=No and exit)"
if errorlevel 2 (
    echo [DEBUG] User declined Python install.
    pause
    goto :EOF
)
call :INSTALL_PYTHON_312
if errorlevel 1 (
    echo [ERROR] Python installation failed.
    pause
    goto :EOF
)

goto :CHECK_PYTHON

:PYTHON_READY
if "!PYTHON_CMD!"=="" (
    echo [ERROR] Python is unavailable after installation.
    pause
    goto :EOF
)

if "!PY_FULL_VERSION!"=="" (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_FULL_VERSION=%%v"
)

for /f "tokens=1,2 delims=." %%a in ("!PY_FULL_VERSION!") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)

if not "!PY_MAJOR!"=="3" (
    echo [WARN] Unsupported Python version detected: !PY_FULL_VERSION!
    choice /C YN /M "Do you want to uninstall the current Python and install Python 3.12 required by OceanSpill? (Y=Yes, N=No and exit)"
    if errorlevel 2 (
        echo [DEBUG] User chose to keep unsupported Python and exit.
        pause
        goto :EOF
    )
    call :UNINSTALL_CURRENT_PYTHON
    call :INSTALL_PYTHON_312
    goto :CHECK_PYTHON
)

if !PY_MINOR! lss 10 (
    echo [WARN] Python !PY_FULL_VERSION! is older than the required version.
    choice /C YN /M "Do you want to replace it with Python 3.12? (Y=Yes, N=No and exit)"
    if errorlevel 2 (
        echo [DEBUG] User chose to exit.
        pause
        goto :EOF
    )
    call :UNINSTALL_CURRENT_PYTHON
    call :INSTALL_PYTHON_312
    goto :CHECK_PYTHON
)

if !PY_MINOR! gtr 12 (
    echo [WARN] Python !PY_FULL_VERSION! is newer than the supported version.
    choice /C YN /M "Do you want to replace it with Python 3.12? (Y=Yes, N=No and exit)"
    if errorlevel 2 (
        echo [DEBUG] User chose to exit.
        pause
        goto :EOF
    )
    call :UNINSTALL_CURRENT_PYTHON
    call :INSTALL_PYTHON_312
    goto :CHECK_PYTHON
)

echo [OK] Python !PY_FULL_VERSION! is supported.
GOTO :PYTHON_VALID

:PYTHON_VALID
:: ================================================
:: Check if venv exists
:: ================================================
echo [DEBUG] Checking for venv...
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [DEBUG] venv creation exit code: %errorlevel%
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        goto :EOF
    )
) else (
    echo [DEBUG] venv already exists
)

:: Activate venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    goto :EOF
)
echo [DEBUG] Venv activated

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --quiet --upgrade pip
echo [DEBUG] pip upgrade exit code: %errorlevel%

:: Install/upgrade requirements
echo [INFO] Installing Python dependencies...
python -m pip install -r backend\requirements.txt
echo [DEBUG] pip install exit code: %errorlevel%
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install Python dependencies
    echo Check your internet connection and try again.
    pause
    goto :EOF
)

:: ================================================
:: Download AI Model (GitHub Release - Primary, Git LFS - Fallback)
:: ================================================
echo.
echo [INFO] Checking AI model file...

:: GitHub Release download URL
set "MODEL_URL=https://github.com/umar1985rr-dev/OceanSpill/releases/download/v1.0.0-model/best_model.pth"
set "MODEL_PATH=models\fine_tuned\best_model.pth"
set "MODEL_DIR=models\fine_tuned"

:: Ensure model directory exists FIRST (before any file operations)
echo [DEBUG] Ensuring model directory exists: %MODEL_DIR%
if not exist "%MODEL_DIR%" (
    echo [INFO] Creating model directory: %MODEL_DIR%
    mkdir "%MODEL_DIR%" 2>nul
    echo [DEBUG] mkdir exit code: %errorlevel%
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create model directory. Check permissions.
        pause
        goto :EOF
    )
) else (
    echo [DEBUG] Model directory already exists
)

:: Check if model exists and is valid (get file size safely)
call :GET_FILE_SIZE "%MODEL_PATH%"
echo [DEBUG] Model file size: !FILE_SIZE!
if !FILE_SIZE! GTR 10000000 (
    echo [OK] Model file exists (!FILE_SIZE! bytes)
    goto :MODEL_DONE
)

if exist "%MODEL_PATH%" (
    echo [WARN] Model file exists but appears invalid/corrupt (!FILE_SIZE! bytes)
) else (
    echo [INFO] Model file not found. Downloading from GitHub Release...
)

:: Download with curl (built into Windows 10 1803+)
:DOWNLOAD_MODEL
echo [INFO] Downloading model (~98MB) from GitHub Release...
echo [INFO] URL: %MODEL_URL%

curl -L -o "%MODEL_PATH%" "%MODEL_URL%" --progress-bar --retry 3 --retry-delay 5 --connect-timeout 30
echo [DEBUG] curl exit code: %errorlevel%
if %errorlevel% neq 0 (
    echo [WARN] curl download failed (exit code: %errorlevel%).

    :: Check if git is available for LFS fallback
    git --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] Trying Git LFS as fallback...
        git lfs pull
        if %errorlevel% neq 0 (
            git lfs fetch --all
            git lfs checkout
        )
    ) else (
        echo [WARN] Git not found in PATH. Skipping Git LFS fallback.
        echo [INFO] To enable Git LFS fallback: Install Git from https://git-scm.com/
        echo [INFO] Make sure to check "Git from the command line and also from 3rd-party software" during install.
    )
)

:: Verify download
call :GET_FILE_SIZE "%MODEL_PATH%"
echo [DEBUG] Downloaded file size: !FILE_SIZE!
if !FILE_SIZE! GTR 10000000 (
    echo [SUCCESS] Model downloaded (!FILE_SIZE! bytes)
    goto :MODEL_DONE
) else (
    echo [ERROR] Model download failed - file too small or missing (!FILE_SIZE! bytes)
    echo.
    echo Manual fix: Download from %MODEL_URL%
    echo And place at: %MODEL_PATH%
    pause
    goto :EOF
)

:MODEL_DONE
echo [DEBUG] Reached MODEL_DONE, continuing to frontend check...

:: ================================================
:: Check if frontend is built
:: ================================================
echo [DEBUG] Checking frontend build...
if not exist "frontend\dist\index.html" (
    echo.
    echo [INFO] Building frontend...
    cd frontend
    if not exist "node_modules" (
        echo [INFO] Installing npm packages...
        call npm install
        echo [DEBUG] npm install exit code: %errorlevel%
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
            goto :EOF
        )
    )
    call npm run build
    echo [DEBUG] npm run build exit code: %errorlevel%
    if %errorlevel% neq 0 (
        echo [WARN] Frontend build had issues but continuing...
    )
    cd ..
) else (
    echo [DEBUG] Frontend already built
)

:: ================================================
:: Start the server
:: ================================================
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

:: If the port is already in use, don't start a second server — it's the
:: #1 source of "Backend offline" flapping and duplicate incidents (same
:: port, two monitoring loops, SQLite conflicts).
netstat -ano | findstr /C:":8000" | findstr /C:"LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Backend already running on port 8000. Opening the browser...
    echo [INFO] Close the running backend first if you want to restart it.
    timeout /t 2 /nobreak >nul
    start "" http://localhost:8000
    goto :EOF
)

:: Start uvicorn in background, wait for port, then open browser — single window
echo [DEBUG] Starting uvicorn in background...
set PYTHONUNBUFFERED=1
start /B python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

:: Wait for port 8000 to be listening (up to 30 seconds)
echo [DEBUG] Waiting for server to be ready...
set /a _wait=0
:WAIT_LOOP
timeout /t 1 /nobreak >nul
set /a _wait+=1
netstat -ano | findstr /C:":8000" | findstr /C:"LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    if %_wait% lss 30 goto :WAIT_LOOP
    echo [WARN] Server did not start within 30 seconds.
)
echo [DEBUG] Server ready after %_wait%s — opening browser...
start "" http://localhost:8000

:: Keep window open while server runs
:KEEP_ALIVE
timeout /t 10 /nobreak >nul
tasklist /FI "IMAGENAME eq python.exe" 2>nul | findstr /I "python.exe" >nul 2>&1
if %errorlevel% equ 0 goto :KEEP_ALIVE
echo [DEBUG] Server process ended.
pause
goto :EOF

:: ================================================
:: Subroutines (must be at END to prevent fall-through)
:: ================================================

:INSTALL_PYTHON_312
echo [INFO] Downloading Python 3.12 installer...
where powershell >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell is required to install Python automatically.
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe', '%PYTHON_INSTALLER_PATH%')"
if not exist "%PYTHON_INSTALLER_PATH%" (
    echo [ERROR] Failed to download Python 3.12 installer.
    exit /b 1
)

echo [INFO] Installing Python 3.12 for all users and adding to PATH...
start /wait "" "%PYTHON_INSTALLER_PATH%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if errorlevel 1 (
    echo [ERROR] Python 3.12 installation failed.
    exit /b 1
)

echo [OK] Python 3.12 installation complete.
exit /b 0

:UNINSTALL_CURRENT_PYTHON
echo [INFO] Attempting to remove the unsupported Python installation...
where winget >nul 2>&1
if not errorlevel 1 (
    for /f "usebackq delims=" %%i in (`winget list --id Python.Python --exact --source winget 2^>nul`) do (
        echo %%i | findstr /I "Python.Python" >nul 2>&1
        if not errorlevel 1 (
            echo [INFO] Uninstalling Python via winget...
            winget uninstall --id Python.Python --exact --silent --accept-source-agreements --accept-package-agreements
            exit /b 0
        )
    )
)

for /f "skip=2 tokens=1,2,*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" 2^>nul ^| findstr /I "Python"') do (
    echo [INFO] Found Python registry entry: %%c
    for /f "tokens=1 delims=" %%d in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /v "DisplayName" 2^>nul ^| findstr /I "Python"') do (
        echo %%d
    )
)

for %%p in ("%LOCALAPPDATA%\Programs\Python" "C:\Python" "C:\Python312" "C:\Python311" "C:\Python310") do (
    if exist "%%~p" (
        echo [INFO] Removing Python directory: %%~p
        rmdir /s /q "%%~p" 2>nul
    )
)

where python >nul 2>&1
if errorlevel 1 (
    echo [OK] Unsupported Python removed or no longer active.
)
exit /b 0

:GET_FILE_SIZE
set "FILE_SIZE=0"
if exist "%~1" (
    for %%F in ("%~1") do set "FILE_SIZE=%%~zF"
)
goto :eof