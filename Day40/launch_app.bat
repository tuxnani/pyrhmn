@echo off
echo ========================================
echo Google Drive Viewer - Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please run setup.bat first to install Python and required packages.
    echo.
    pause
    exit /b 1
)

REM Check if credentials.json exists
echo Checking for credentials.json...
if not exist "%~dp0credentials.json" (
    echo.
    echo ========================================
    echo ERROR: credentials.json not found!
    echo ========================================
    echo.
    echo The program requires Google OAuth credentials to run.
    echo.
    echo Please follow these steps:
    echo.
    echo 1. Go to: https://console.cloud.google.com/
    echo 2. Create a new project or select existing one
    echo 3. Enable the Google Drive API
    echo 4. Go to "Credentials" and create "OAuth 2.0 Client ID"
    echo 5. Select "Desktop app" as application type
    echo 6. Download the JSON file
    echo 7. Rename it to "credentials.json"
    echo 8. Place it in: %~dp0
    echo.
    echo Current directory: %~dp0
    echo.
    pause
    exit /b 1
)

echo credentials.json found!
echo.

REM Check if the main Python script exists
if not exist "%~dp0google_drive_viewer.py" (
    echo ERROR: google_drive_viewer.py not found!
    echo Please ensure the Python script is in the same folder as this batch file.
    echo.
    pause
    exit /b 1
)

REM Run the program
echo Starting Google Drive Viewer...
echo.
python "%~dp0google_drive_viewer.py"

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo The program encountered an error!
    echo ========================================
    echo.
    pause
    exit /b 1
)

echo.
echo Program closed.
pause