@echo off
REM =============================================================================
REM Frankie's Client Browser Setup Script
REM =============================================================================

echo.
echo ================================================================================
echo Frankie's Client Browser Setup
echo ================================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [Step 1/4] Checking for required files...
if not exist "Frankie_Desktop_Shortcuts.zip" (
    echo ERROR: Frankie_Desktop_Shortcuts.zip not found!
    pause
    exit /b 1
)
if not exist "Ana_Dashboards.zip" (
    echo ERROR: Ana_Dashboards.zip not found! (We share the dashboard files)
    pause
    exit /b 1
)
echo   [OK] Files found

echo.
echo [Step 2/4] Creating folders...
if not exist "C:\Automation" mkdir "C:\Automation"
if not exist "C:\Automation\My_Profiles" mkdir "C:\Automation\My_Profiles"
if not exist "C:\Automation\Dashboards" mkdir "C:\Automation\Dashboards"
echo   [OK] Folders ready

echo.
echo [Step 3/4] Updating Dashboards...
REM Clean old dashboards
del "C:\Automation\Dashboards\*.html" /q 2>nul
REM Extract new ones
powershell -Command "Expand-Archive -Path '%SCRIPT_DIR%Ana_Dashboards.zip' -DestinationPath 'C:\Automation\Dashboards' -Force"
if %errorlevel% neq 0 (
    echo ERROR: Failed to extract dashboards!
    pause
    exit /b 1
)
echo   [OK] Dashboards updated

echo.
echo [Step 4/4] Installing Shortcuts...
REM Extract directly to Desktop (overwriting existing ones)
powershell -Command "Expand-Archive -Path '%SCRIPT_DIR%Frankie_Desktop_Shortcuts.zip' -DestinationPath '%USERPROFILE%\Desktop\' -Force"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install shortcuts!
    pause
    exit /b 1
)
echo   [OK] Shortcuts installed to Desktop

echo.
echo ================================================================================
echo SUCCESS! Setup Complete!
echo ================================================================================
echo.
pause

