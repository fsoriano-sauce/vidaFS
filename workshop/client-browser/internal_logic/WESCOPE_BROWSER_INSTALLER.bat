@echo off
REM =============================================================================
REM WeScope Browser - Unified Installer Launcher (Smart Elevation)
REM =============================================================================
setlocal enabledelayedexpansion

REM 1. Define Master Path (G: Drive)
set "MASTER_DIR=G:\Shared drives\Client Shortcuts\For_Team_Complete"
set "MASTER_SETUP=%MASTER_DIR%\SETUP_TEAM.bat"

REM 2. Check for G: Drive Visibility
if not exist "%MASTER_SETUP%" (
    REM Check if we are already Admin
    net session >nul 2>&1
    if !errorlevel! equ 0 (
        echo.
        echo ======================================================================
        echo  [ERROR] GOOGLE DRIVE NOT VISIBLE AS ADMIN
        echo ======================================================================
        echo.
        echo  You are running this script as Administrator.
        echo  Windows security prevents Administrator from seeing G: Drive.
        echo.
        echo  FIX: Please simply DOUBLE-CLICK this file (Run as Normal User).
        echo       The script will copy files first, THEN ask for Admin permissions.
        echo.
        echo ======================================================================
        pause
        exit /b 1
    ) else (
        echo.
        echo [ERROR] Google Drive (G:) is NOT MOUNTED or accessible.
        echo Please ensure Google Drive for Desktop is running and G: is visible.
        echo Checked path: "%MASTER_DIR%"
        echo.
        pause
        exit /b 1
    )
)

REM 3. We can see G:. Prepare Temp Directory.
set "TEMP_DIR=%TEMP%\WeScopeSetup_%RANDOM%"
echo.
echo  --------------------------------------------------
echo    WESCOPE CLIENT SYSTEMS - INSTALLER LOADER
echo  --------------------------------------------------
echo.
echo  [1/3] Found G: Drive. Preparing local setup...
mkdir "%TEMP_DIR%" >nul 2>&1

echo  [2/3] Copying installation files to temporary folder...
copy "%MASTER_DIR%\SETUP_TEAM.bat" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\Automation.zip" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\Shortcuts.zip" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\version.txt" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\CLEANUP_POLICIES.bat" "%TEMP_DIR%\" >nul

if not exist "%TEMP_DIR%\SETUP_TEAM.bat" (
    echo [ERROR] Failed to copy files from G:.
    pause
    exit /b 1
)

echo  [3/3] Launching Installer (You will see a UAC Prompt)...
echo.

REM 4. Launch SETUP_TEAM.bat as Administrator from Temp
REM We pass the MASTER_DIR as an argument so it knows where to look for updates later.
REM Argument order: [dummy] [path]. Our parser handles it.
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %TEMP_DIR% && SETUP_TEAM.bat /interactive \"%MASTER_DIR%\"' -Verb RunAs"

if %errorlevel% neq 0 (
    echo [ERROR] Failed to launch elevated installer.
    pause
)

exit /b 0
