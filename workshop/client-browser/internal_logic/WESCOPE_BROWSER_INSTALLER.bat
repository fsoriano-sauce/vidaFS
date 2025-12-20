@echo off
REM =============================================================================
REM WeScope Browser - Unified Installer Launcher (v3.8 Stable)
REM =============================================================================
setlocal enabledelayedexpansion

REM 1. Define Master Path (G: Drive)
set "MASTER_DIR=G:\Shared drives\Client Shortcuts\For_Team_Complete"
set "MASTER_SETUP=%MASTER_DIR%\SETUP_TEAM.bat"

echo.
echo  --------------------------------------------------
echo    WESCOPE CLIENT SYSTEMS - INSTALLER LOADER
echo  --------------------------------------------------
echo.
echo  [1/3] Checking connection to WeScope Drive...

REM 2. Check for G: Drive Visibility
if not exist "%MASTER_SETUP%" (
    echo.
    echo  [ERROR] Cannot access G: Drive.
    echo  Please ensure Google Drive for Desktop is running.
    echo.
    REM Check if running as Admin (which hides G: drive)
    net session >nul 2>&1
    if !errorlevel! equ 0 (
        echo  [TIP] You are running as Administrator.
        echo        Please CLOSE this window and simply DOUBLE-CLICK the file.
        echo        (Do NOT Right-Click - Run as Admin).
    )
    pause
    exit /b 1
)

REM 3. Prepare Temp Directory
set "TEMP_DIR=%TEMP%\WeScopeSetup_%RANDOM%"
mkdir "%TEMP_DIR%" >nul 2>&1

echo  [2/3] Downloading installer files...
copy "%MASTER_DIR%\SETUP_TEAM.bat" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\Automation.zip" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\Shortcuts.zip" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\version.txt" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\CLEANUP_POLICIES.bat" "%TEMP_DIR%\" >nul

if not exist "%TEMP_DIR%\SETUP_TEAM.bat" (
    echo.
    echo  [ERROR] Failed to download files.
    echo  Please check your internet connection.
    pause
    exit /b 1
)

echo  [3/3] Starting Installer...
echo.
echo  [ACTION REQUIRED]
echo  A new window will appear requesting Administrator permissions.
echo  Please click [YES] to continue.
echo.

REM 4. Launch SETUP_TEAM.bat as Administrator from Temp
REM We use /k to KEEP the window open if it crashes, so you can see the error.
powershell -Command "Start-Process cmd -ArgumentList '/k cd /d %TEMP_DIR% && SETUP_TEAM.bat /interactive \"%MASTER_DIR%\"' -Verb RunAs"

echo  Done. You can close this window.
pause
exit /b 0
