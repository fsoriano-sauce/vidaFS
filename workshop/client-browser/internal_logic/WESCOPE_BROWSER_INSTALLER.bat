@echo off
setlocal enabledelayedexpansion
title WeScope Browser Installer

echo ================================================================================
echo WESCOPE BROWSER INSTALLER (Launcher v4.0)
echo ================================================================================
echo.

REM 1. Detect Source Path (Where this script is running from)
set "SOURCE_PATH=%~dp0"
REM Remove trailing backslash
if "%SOURCE_PATH:~-1%"=="\" set "SOURCE_PATH=%SOURCE_PATH:~0,-1%"

echo [INFO] Running from: %SOURCE_PATH%

REM 2. Check for Installation Files
REM We expect 'resources' folder and 'SETUP_TEAM.bat' to be in the same folder as this script
REM (Because the user is running this from the Unzipped folder OR the G-Drive)

if not exist "%SOURCE_PATH%\SETUP_TEAM.bat" (
    echo [ERROR] SETUP_TEAM.bat not found in %SOURCE_PATH%.
    echo Please make sure you have extracted all files or are running from the Shared Drive.
    pause
    exit /b 1
)

REM 3. "Copy First" Strategy (Bypasses Admin Network Drive Restrictions)
echo.
echo [Step 1/2] Preparing installation files...
set "TEMP_INSTALL_DIR=%TEMP%\WeScope_Install_%RANDOM%"
mkdir "%TEMP_INSTALL_DIR%" >nul 2>&1
mkdir "%TEMP_INSTALL_DIR%\resources" >nul 2>&1

echo   Copying files to temporary local folder...
copy "%SOURCE_PATH%\SETUP_TEAM.bat" "%TEMP_INSTALL_DIR%\" >nul 2>&1
copy "%SOURCE_PATH%\resources\Automation.zip" "%TEMP_INSTALL_DIR%\resources\" >nul 2>&1
copy "%SOURCE_PATH%\resources\Shortcuts.zip" "%TEMP_INSTALL_DIR%\resources\" >nul 2>&1

if not exist "%TEMP_INSTALL_DIR%\resources\Automation.zip" (
    echo [ERROR] Failed to copy files to temp directory.
    pause
    exit /b 1
)

REM 4. Launch Setup as Administrator
echo.
echo [Step 2/2] Launching Setup as Administrator...
echo.
echo Please click "Yes" on the User Account Control (UAC) prompt.
echo.

REM We pass the SOURCE_PATH as the first argument so SETUP_TEAM knows where to look for future updates
REM This is critical for Auto-Update configuration
powershell -Command "Start-Process -FilePath '%TEMP_INSTALL_DIR%\SETUP_TEAM.bat' -ArgumentList '\"%SOURCE_PATH%\"' -Verb RunAs -Wait"

REM 5. Cleanup
rmdir /s /q "%TEMP_INSTALL_DIR%" >nul 2>&1

echo.
echo ================================================================================
echo INSTALLATION COMPLETE
echo ================================================================================
echo You can close this window.
pause
