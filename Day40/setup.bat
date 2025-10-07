@echo off
echo ========================================
echo Google Drive Viewer - Setup Script
echo ========================================
echo.

REM Check if Python is installed
echo [1/4] Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python --version
echo Python is installed successfully!
echo.

REM Upgrade pip
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install required packages
echo [3/4] Installing required packages...
echo This may take a few minutes...
echo.

python -m pip install google-auth-oauthlib google-api-python-client openpyxl pandas

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install required packages!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying installation...
python -c "import google_auth_oauthlib, googleapiclient, openpyxl, pandas" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Package verification failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo IMPORTANT: Before running the program, you need to:
echo 1. Go to Google Cloud Console (console.cloud.google.com)
echo 2. Create a project and enable Google Drive API
echo 3. Create OAuth 2.0 Desktop credentials
echo 4. Download the credentials JSON file
echo 5. Rename it to "credentials.json"
echo 6. Place it in this folder: %~dp0
echo.
echo After completing these steps, run "run.bat" to start the program.
echo.
pause