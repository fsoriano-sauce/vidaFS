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

REM 1b. Detect User Desktop (Pass to Admin Process)
REM This ensures shortcuts go to the correct user's desktop, even when running as Admin
set "USER_DESKTOP="
for /f "usebackq delims=" %%I in (`powershell -Command "[Environment]::GetFolderPath('Desktop')"`) do set "USER_DESKTOP=%%I"
echo [INFO] Target Desktop: %USER_DESKTOP%

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
REM Using C:\WeScope_Install to avoid Temp folder restrictions
set "TEMP_INSTALL_DIR=C:\WeScope_Install"
if exist "%TEMP_INSTALL_DIR%" rmdir /s /q "%TEMP_INSTALL_DIR%" >nul 2>&1
mkdir "%TEMP_INSTALL_DIR%" >nul 2>&1
mkdir "%TEMP_INSTALL_DIR%\resources" >nul 2>&1

echo   Copying files to temporary local folder...
copy "%SOURCE_PATH%\SETUP_TEAM.bat" "%TEMP_INSTALL_DIR%\" >nul 2>&1
copy "%SOURCE_PATH%\resources\Automation.zip" "%TEMP_INSTALL_DIR%\resources\" >nul 2>&1
copy "%SOURCE_PATH%\resources\Shortcuts.zip" "%TEMP_INSTALL_DIR%\resources\" >nul 2>&1

if not exist "%TEMP_INSTALL_DIR%\resources\Shortcuts.zip" (
    echo [ERROR] Missing resources\Shortcuts.zip
    pause
    exit /b 1
)

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

REM We pass the SOURCE_PATH and USER_DESKTOP to SETUP_TEAM
echo [DEBUG] Launching SETUP_TEAM.bat...
echo [DEBUG] Source: "%SOURCE_PATH%"
echo [DEBUG] Desktop: "%USER_DESKTOP%"
echo [DEBUG] Temp Dir Contents:
dir "%TEMP_INSTALL_DIR%"

REM Using robust PowerShell invocation with try/catch
REM We construct a single argument string with explicit double quotes
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$src='%SOURCE_PATH%'; $desk='%USER_DESKTOP%'; $local='%TEMP_INSTALL_DIR%'; $argsList=@($src, $desk);" ^
  "$p = Start-Process -FilePath (Join-Path $local 'SETUP_TEAM.bat') -ArgumentList $argsList -WorkingDirectory $local -Verb RunAs -Wait -PassThru;" ^
  "exit $p.ExitCode"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Setup failed with exit code %errorlevel%.
    echo Check: C:\Automation\setup_debug.log
    pause
    exit /b %errorlevel%
)

REM 5. Cleanup
rmdir /s /q "%TEMP_INSTALL_DIR%" >nul 2>&1

echo.
echo ================================================================================
echo INSTALLATION COMPLETE
echo ================================================================================
echo You can close this window.
pause


