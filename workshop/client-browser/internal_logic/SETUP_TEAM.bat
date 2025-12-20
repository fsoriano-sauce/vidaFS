@echo off
REM =============================================================================
REM WeScope Team - Unified Client Browser Setup & Auto-Updater
REM =============================================================================
setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo WeScope Team Browser Setup (Unified Installer)
echo ================================================================================
echo.

REM 1. Check Administrator Privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script must be run as Administrator!
    echo.
    echo Right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

REM 2. Environment Setup
set SCRIPT_DIR=%~dp0
set AUTO_DIR=C:\Automation
set PROFILE_DIR=%AUTO_DIR%\Profiles
set SHORTCUT_TARGET_NAME=Client Systems Shortcuts
set SHORTCUT_PATH=%USERPROFILE%\Desktop\%SHORTCUT_TARGET_NAME%

REM Detect OneDrive Desktop (Fix for missing icons)
if exist "%USERPROFILE%\OneDrive\Desktop" (
    set "SHORTCUT_PATH=%USERPROFILE%\OneDrive\Desktop\%SHORTCUT_TARGET_NAME%"
) else (
    set "SHORTCUT_PATH=%USERPROFILE%\Desktop\%SHORTCUT_TARGET_NAME%"
)

cd /d "%SCRIPT_DIR%"

REM 3. File Verification
echo [Step 1/4] Verifying installation files...
echo   Working Dir: %CD%

REM Check for resources folder
set "RES_DIR=%SCRIPT_DIR%resources"
if not exist "%RES_DIR%" (
    REM Fallback for legacy flat structure (just in case)
    if exist "Automation.zip" set "RES_DIR=%SCRIPT_DIR%"
)

if not exist "%RES_DIR%\Automation.zip" ( echo [ERROR] Automation.zip missing in %RES_DIR%! & pause & exit /b 1 )
if not exist "%RES_DIR%\Shortcuts.zip" ( echo [ERROR] Shortcuts.zip missing in %RES_DIR%! & pause & exit /b 1 )
echo   [OK] Found assets in %RES_DIR%

REM 4. Chrome Policy Cleanup (Proactive Fix)
echo [Step 2/4] Cleaning Chrome Policies...
reg delete "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallBlacklist" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallWhitelist" /f >nul 2>&1
echo   [OK] Policy Cleanup Complete.

REM 5. Install Assets & Shortcuts
echo [Step 3/4] Installing Assets and Shortcuts...
REM Ensure Automation folder exists
if not exist "%AUTO_DIR%" mkdir "%AUTO_DIR%"

REM Extract Automation.zip to C:\ (Contains Icons, Dashboards, Extensions)
echo   [Step 3/4] Unpacking assets...
pushd C:\
tar -xf "%RES_DIR%\Automation.zip" >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Expand-Archive -Path '%RES_DIR%\Automation.zip' -DestinationPath 'C:\' -Force"
)
popd

REM Extract Shortcuts to Desktop
echo   [Step 3/4] Unpacking shortcuts...
powershell -Command "$p = '%SHORTCUT_PATH%'; if (Test-Path $p) { Remove-Item $p -Recurse -Force }; New-Item -ItemType Directory -Path $p -Force | Out-Null; Expand-Archive -Path '%RES_DIR%\Shortcuts.zip' -DestinationPath $p -Force"
echo   [OK] Assets installed to %AUTO_DIR%
echo   [OK] Shortcuts installed to Desktop\%SHORTCUT_TARGET_NAME%

REM 6. Optional Auto-Update Setup
echo.
echo [Step 4/4] Configuring Auto-Updates...

REM Check if we are running from a sync folder (Google Drive, etc.)
set IS_SYNC_FOLDER=0
echo %SCRIPT_DIR% | findstr /i "Google" >nul && set IS_SYNC_FOLDER=1
echo %SCRIPT_DIR% | findstr /i "OneDrive" >nul && set IS_SYNC_FOLDER=1
echo %SCRIPT_DIR% | findstr /i "Shared drives" >nul && set IS_SYNC_FOLDER=1

if "%1"=="/silent" (
    set SETUP_AUTO=Y
) else (
    echo.
    echo Would you like to enable automatic background updates?
    echo (Shortcuts will update every 15 mins when the admin pushes changes)
    set /p SETUP_AUTO="Enable Auto-Updates? (Y/N): "
)

if /i "%SETUP_AUTO%"=="Y" (
    REM Use detected path or prompt if not found
    set UPDATE_PATH=%SCRIPT_DIR%
    if "%IS_SYNC_FOLDER%"=="0" (
        if not "%1"=="/silent" (
            echo.
            echo [WARNING] Could not automatically detect Google Drive path.
            echo Please paste the path to the 'For_Team_Complete' folder on your Drive:
            set /p UPDATE_PATH="Path: "
        )
    )
    
    REM Remove trailing backslash if present
    if "!UPDATE_PATH:~-1!"=="\" set UPDATE_PATH=!UPDATE_PATH:~0,-1!

    REM Create the local AUTO_UPDATE.bat
    (
    echo @echo off
    echo set UPDATE_SOURCE=!UPDATE_PATH!
    echo set RES_DIR=%%UPDATE_SOURCE%%\resources
    echo set VERSION_FILE=%%RES_DIR%%\version.txt
    echo set LOCAL_VERSION_FILE=%AUTO_DIR%\.version
    echo set LOG_FILE=%AUTO_DIR%\update.log
    echo.
    echo if not exist "%%UPDATE_SOURCE%%" exit /b 0
    echo if not exist "%%VERSION_FILE%%" exit /b 0
    echo if not exist "%%LOCAL_VERSION_FILE%%" echo 0 ^> "%%LOCAL_VERSION_FILE%%"
    echo.
    echo set /p SERVER_VERSION=^<"%%VERSION_FILE%%"
    echo set /p LOCAL_VERSION=^<"%%LOCAL_VERSION_FILE%%"
    echo.
    echo if "%%SERVER_VERSION%%"=="%%LOCAL_VERSION%%" exit /b 0
    echo.
    echo set TEMP_DIR=%%TEMP%%\WeScope_Update_%%RANDOM%%
    echo mkdir "%%TEMP_DIR%%" 2^>nul
    echo mkdir "%%TEMP_DIR%%\resources" 2^>nul
    echo copy "%%RES_DIR%%\Automation.zip" "%%TEMP_DIR%%\resources\" ^>nul 2^>^&1
    echo copy "%%RES_DIR%%\Shortcuts.zip" "%%TEMP_DIR%%\resources\" ^>nul 2^>^&1
    echo copy "%%UPDATE_SOURCE%%\SETUP_TEAM.bat" "%%TEMP_DIR%%\" ^>nul 2^>^&1
    echo if not exist "%%TEMP_DIR%%\resources\Automation.zip" exit /b 1
    echo cd /d "%%TEMP_DIR%%"
    echo call SETUP_TEAM.bat /silent "!UPDATE_PATH!" ^>nul 2^>^&1
    echo if %%errorlevel%% equ 0 echo %%SERVER_VERSION%% ^> "%%LOCAL_VERSION_FILE%%"
    echo cd /d "%%USERPROFILE%%"
    echo rmdir /s /q "%%TEMP_DIR%%" 2^>nul
    ) > "%AUTO_DIR%\AUTO_UPDATE.bat"

    REM Create the silent runner VBScript (to hide the popup)
    (
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.Run chr^(34^) ^& "%AUTO_DIR%\AUTO_UPDATE.bat" ^& Chr^(34^), 0
    echo Set WshShell = Nothing
    ) > "%AUTO_DIR%\silent_run.vbs"

    REM Create Scheduled Task (using wscript to hide the window)
    schtasks /create /tn "WeScope Browser Auto-Update" /tr "wscript.exe //B \"%AUTO_DIR%\silent_run.vbs\"" /sc minute /mo 15 /rl highest /f >nul 2>&1
    
    if !errorlevel! equ 0 (
        echo   [OK] Auto-update scheduled (every 15 mins - SILENT)
        REM Initialize version file
        if exist "version.txt" copy /y "version.txt" "%AUTO_DIR%\.version" >nul
    ) else (
        echo   [ERROR] Failed to create scheduled task.
    )
) else (
    echo   [SKIP] Auto-update setup skipped.
)

echo.
echo ================================================================================
echo SUCCESS! Setup Complete.
echo ================================================================================
if not "%1"=="/silent" pause
exit /b 0
