@echo off
REM =============================================================================
REM WeScope Auto-Updater (Silent Background Updates)
REM =============================================================================
REM This script checks for updates and installs them automatically.
REM Designed to run via Task Scheduler without user interaction.
REM =============================================================================

REM === CONFIGURATION ===
REM Set this to your Google Drive sync folder or any shared location
set UPDATE_SOURCE=G:\My Drive\WeScope\Browser Updates\For_Team_Complete
set VERSION_FILE=%UPDATE_SOURCE%\version.txt
set LOCAL_VERSION_FILE=C:\Automation\.version
set LOG_FILE=C:\Automation\update.log

REM Create log entry
echo [%date% %time%] Auto-update check started >> "%LOG_FILE%"

REM Check if source folder exists
if not exist "%UPDATE_SOURCE%" (
    echo [%date% %time%] Source folder not found: %UPDATE_SOURCE% >> "%LOG_FILE%"
    exit /b 0
)

REM Check if version file exists on server
if not exist "%VERSION_FILE%" (
    echo [%date% %time%] Version file not found on server >> "%LOG_FILE%"
    exit /b 0
)

REM Create local version file if it doesn't exist
if not exist "%LOCAL_VERSION_FILE%" (
    echo 0 > "%LOCAL_VERSION_FILE%"
)

REM Read versions
set /p SERVER_VERSION=<"%VERSION_FILE%"
set /p LOCAL_VERSION=<"%LOCAL_VERSION_FILE%"

REM Compare versions
if "%SERVER_VERSION%"=="%LOCAL_VERSION%" (
    echo [%date% %time%] Already up to date (v%LOCAL_VERSION%) >> "%LOG_FILE%"
    exit /b 0
)

echo [%date% %time%] Update available: v%LOCAL_VERSION% -^> v%SERVER_VERSION% >> "%LOG_FILE%"

REM Create temp directory
set TEMP_DIR=%TEMP%\WeScope_Update_%RANDOM%
mkdir "%TEMP_DIR%" 2>nul

REM Copy files
copy "%UPDATE_SOURCE%\Automation.zip" "%TEMP_DIR%\" >nul 2>&1
copy "%UPDATE_SOURCE%\Shortcuts.zip" "%TEMP_DIR%\" >nul 2>&1
copy "%UPDATE_SOURCE%\SETUP_TEAM.bat" "%TEMP_DIR%\" >nul 2>&1

if not exist "%TEMP_DIR%\Automation.zip" (
    echo [%date% %time%] Failed to copy files >> "%LOG_FILE%"
    rmdir /s /q "%TEMP_DIR%" 2>nul
    exit /b 1
)

REM Run silent update
cd /d "%TEMP_DIR%"
call SETUP_TEAM.bat /silent >nul 2>&1

if %errorlevel% equ 0 (
    echo [%date% %time%] Update successful! Now running v%SERVER_VERSION% >> "%LOG_FILE%"
    echo %SERVER_VERSION% > "%LOCAL_VERSION_FILE%"
) else (
    echo [%date% %time%] Update failed with error code %errorlevel% >> "%LOG_FILE%"
)

REM Cleanup
cd /d "%USERPROFILE%"
rmdir /s /q "%TEMP_DIR%" 2>nul

exit /b 0


