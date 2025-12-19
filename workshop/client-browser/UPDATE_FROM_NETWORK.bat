@echo off
REM =============================================================================
REM WeScope Team - Update from Network Share
REM =============================================================================
echo.
echo ================================================================================
echo WeScope Team Browser Update
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

REM Network share path (update this to your actual share location)
set NETWORK_PATH=\\SERVER\Share\WeScope\client-browser\For_Team_Complete

REM Check if network path exists
if not exist "%NETWORK_PATH%" (
    echo [ERROR] Network path not found: %NETWORK_PATH%
    echo Please update the NETWORK_PATH variable in this script.
    pause
    exit /b 1
)

echo [INFO] Copying latest packages from network share...
echo Source: %NETWORK_PATH%
echo.

REM Create temp directory
set TEMP_DIR=%TEMP%\WeScope_Update
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

REM Copy files
copy "%NETWORK_PATH%\Automation.zip" "%TEMP_DIR%\" >nul
copy "%NETWORK_PATH%\Shortcuts.zip" "%TEMP_DIR%\" >nul
copy "%NETWORK_PATH%\SETUP_TEAM.bat" "%TEMP_DIR%\" >nul

if not exist "%TEMP_DIR%\Automation.zip" (
    echo [ERROR] Failed to copy Automation.zip from network share!
    pause
    exit /b 1
)

echo [OK] Files copied to temp directory.
echo.
echo Running setup...

REM Run the setup script from temp directory
cd /d "%TEMP_DIR%"
call SETUP_TEAM.bat

echo.
echo [Cleanup] Removing temp files...
cd /d "%USERPROFILE%"
rmdir /s /q "%TEMP_DIR%" >nul 2>&1

echo.
echo ================================================================================
echo UPDATE COMPLETE!
echo ================================================================================
echo.
pause


