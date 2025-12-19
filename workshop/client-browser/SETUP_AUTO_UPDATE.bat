@echo off
REM =============================================================================
REM Setup Auto-Update (One-time Team Member Setup)
REM =============================================================================
echo.
echo ================================================================================
echo WeScope Auto-Update Setup
echo ================================================================================
echo.
echo This script will configure automatic background updates for your browser
echo shortcuts. Updates will check every 4 hours and install silently.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

REM Prompt for Google Drive path
echo.
echo Enter the path to your synced Google Drive folder containing updates.
echo Example: G:\My Drive\WeScope\Browser Updates\For_Team_Complete
echo.
set /p DRIVE_PATH="Google Drive Path: "

REM Verify path exists
if not exist "%DRIVE_PATH%" (
    echo.
    echo [ERROR] Path not found: %DRIVE_PATH%
    echo Please check the path and try again.
    pause
    exit /b 1
)

REM Create AUTO_UPDATE.bat with the correct path
echo Creating auto-updater script...
set AUTO_UPDATE_SCRIPT=C:\Automation\AUTO_UPDATE.bat

(
echo @echo off
echo set UPDATE_SOURCE=%DRIVE_PATH%
echo set VERSION_FILE=%%UPDATE_SOURCE%%\version.txt
echo set LOCAL_VERSION_FILE=C:\Automation\.version
echo set LOG_FILE=C:\Automation\update.log
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
echo copy "%%UPDATE_SOURCE%%\Automation.zip" "%%TEMP_DIR%%\" ^>nul 2^>^&1
echo copy "%%UPDATE_SOURCE%%\Shortcuts.zip" "%%TEMP_DIR%%\" ^>nul 2^>^&1
echo copy "%%UPDATE_SOURCE%%\SETUP_TEAM.bat" "%%TEMP_DIR%%\" ^>nul 2^>^&1
echo if not exist "%%TEMP_DIR%%\Automation.zip" exit /b 1
echo cd /d "%%TEMP_DIR%%"
echo call SETUP_TEAM.bat ^>nul 2^>^&1
echo if %%errorlevel%% equ 0 echo %%SERVER_VERSION%% ^> "%%LOCAL_VERSION_FILE%%"
echo cd /d "%%USERPROFILE%%"
echo rmdir /s /q "%%TEMP_DIR%%" 2^>nul
) > "%AUTO_UPDATE_SCRIPT%"

echo   [OK] Auto-updater created

REM Create scheduled task
echo Creating scheduled task...
schtasks /create /tn "WeScope Browser Auto-Update" /tr "\"%AUTO_UPDATE_SCRIPT%\"" /sc hourly /mo 4 /rl highest /f >nul 2>&1

if %errorlevel% equ 0 (
    echo   [OK] Scheduled task created (runs every 4 hours)
) else (
    echo   [WARNING] Failed to create scheduled task
)

echo.
echo ================================================================================
echo SETUP COMPLETE!
echo ================================================================================
echo Your browser shortcuts will now update automatically in the background.
echo You can view the update log at: C:\Automation\update.log
echo.
pause
