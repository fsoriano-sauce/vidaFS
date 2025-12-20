@echo off
REM =============================================================================
REM WeScope Browser - Unified Installer Launcher (DEBUG MODE)
REM =============================================================================
setlocal enabledelayedexpansion

echo [DEBUG] Launcher Started.
echo [DEBUG] User: %USERNAME%
echo [DEBUG] Working Dir: %CD%

REM 1. Define Master Path (G: Drive)
set "MASTER_DIR=G:\Shared drives\Client Shortcuts\For_Team_Complete"
set "MASTER_SETUP=%MASTER_DIR%\SETUP_TEAM.bat"

echo [DEBUG] Looking for: "%MASTER_SETUP%"

REM 2. Check for G: Drive Visibility
if not exist "%MASTER_SETUP%" (
    echo [ERROR] Cannot find SETUP_TEAM.bat on G: drive.
    REM Check if we are already Admin
    net session >nul 2>&1
    if !errorlevel! equ 0 (
        echo [ERROR] You are running as Administrator! Admin cannot see G: drive.
        echo FIX: Run as NORMAL user (Double-click only).
    ) else (
        echo [ERROR] G: drive not found. Is Google Drive running?
    )
    pause
    exit /b 1
)

REM 3. We can see G:. Prepare Temp Directory.
set "TEMP_DIR=%TEMP%\WeScopeSetup_%RANDOM%"
echo [DEBUG] Creating temp dir: "%TEMP_DIR%"
mkdir "%TEMP_DIR%" >nul 2>&1

echo [DEBUG] Copying files...
copy "%MASTER_DIR%\SETUP_TEAM.bat" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\Automation.zip" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\Shortcuts.zip" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\version.txt" "%TEMP_DIR%\" >nul
copy "%MASTER_DIR%\CLEANUP_POLICIES.bat" "%TEMP_DIR%\" >nul

if not exist "%TEMP_DIR%\SETUP_TEAM.bat" (
    echo [ERROR] Copy failed.
    pause
    exit /b 1
)

echo [DEBUG] Copy complete.
echo.
echo [INFO] Attempting to launch Admin Prompt...
echo [INFO] Watch for a flashing window or UAC prompt.
echo.

REM 4. Launch SETUP_TEAM.bat as Administrator from Temp
REM CHANGED: cmd /k to keep window open
REM CHANGED: Added quotes around cd path
powershell -Command "Start-Process cmd -ArgumentList '/k cd /d \"%TEMP_DIR%\" && echo [DEBUG] Elevated. && SETUP_TEAM.bat /interactive \"%MASTER_DIR%\"' -Verb RunAs"

echo [DEBUG] Launch command sent.
echo.
echo If no new window appears, the PowerShell command failed.
pause
exit /b 0
