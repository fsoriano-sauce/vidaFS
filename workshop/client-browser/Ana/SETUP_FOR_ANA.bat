@echo off
REM =============================================================================
REM Ana's Client Browser Setup Script
REM =============================================================================

echo.
echo ================================================================================
echo Ana's Client Browser Setup
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

echo [Step 1/5] Checking for required files...
if not exist "Ana_Desktop_Shortcuts.zip" (
    echo ERROR: Ana_Desktop_Shortcuts.zip not found!
    pause
    exit /b 1
)
if not exist "Ana_Dashboards.zip" (
    echo ERROR: Ana_Dashboards.zip not found!
    pause
    exit /b 1
)
echo   [OK] Files found

echo.
echo [Step 2/5] Cleaning up old files...
del "%USERPROFILE%\Desktop\Ana - *.lnk" /q 2>nul
if exist "C:\Automation\Dashboards" (
    del "C:\Automation\Dashboards\*.html" /q 2>nul
)
echo   [OK] Cleanup complete

echo.
echo [Step 3/5] Creating folders...
if not exist "C:\Automation" mkdir "C:\Automation"
if not exist "C:\Automation\Ana_Profiles" mkdir "C:\Automation\Ana_Profiles"
if not exist "C:\Automation\Dashboards" mkdir "C:\Automation\Dashboards"
echo   [OK] Folders ready

echo.
echo [Step 4/5] Extracting dashboards...
powershell -Command "Expand-Archive -Path '%SCRIPT_DIR%Ana_Dashboards.zip' -DestinationPath 'C:\Automation\Dashboards' -Force"
if %errorlevel% neq 0 (
    echo ERROR: Failed to extract dashboards!
    pause
    exit /b 1
)
echo   [OK] Dashboards extracted

echo.
echo [Step 5/5] Installing shortcuts...
powershell -Command "Expand-Archive -Path '%SCRIPT_DIR%Ana_Desktop_Shortcuts.zip' -DestinationPath '%USERPROFILE%\Desktop\' -Force"
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
echo Your client shortcuts are now on your Desktop.
echo Each shortcut will open all systems for that client in separate tabs.
echo.
echo IMPORTANT: Log in to each system ONCE, and Chrome will remember your login.
echo.
echo ================================================================================
echo.
pause
