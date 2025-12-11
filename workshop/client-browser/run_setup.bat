@echo off
echo ========================================
echo Client Browser Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install requirements
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages.
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully.
echo Starting Client Browser Setup...
echo.

REM Run the main script
python client_browser_setup.py

echo.
echo Setup complete! Check your Desktop for the new shortcuts with custom icons.
echo.
pause


