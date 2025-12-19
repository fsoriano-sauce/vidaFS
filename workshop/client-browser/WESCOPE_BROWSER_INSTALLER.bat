@echo off
REM =============================================================================
REM WeScope Browser - Remote Launcher / Installer
REM =============================================================================
setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo WeScope Browser Installer
echo ================================================================================
echo.

REM 1. Define the Master Path on Google Drive
set "MASTER_PATH=G:\Shared drives\Client Shortcuts\For_Team_Complete\SETUP_TEAM.bat"

REM 2. Check if Google Drive is mounted and accessible
if not exist "%MASTER_PATH%" (
    echo [ERROR] Google Drive folder not found!
    echo.
    echo Please ensure:
    echo   1. Google Drive for Desktop is running.
    echo   2. The 'Client Shortcuts' folder is shared with you.
    echo   3. Your Google Drive is mounted as the G: drive.
    echo.
    echo If your Drive uses a different letter (not G:), please contact Frank.
    echo.
    pause
    exit /b 1
)

echo [INFO] Found master setup on Google Drive.
echo [INFO] Launching installer...
echo.

REM 3. Call the master setup script from Google Drive
REM We use 'call' so it stays in this window and 'pushd' to ensure it runs in its own directory
pushd "G:\Shared drives\Client Shortcuts\For_Team_Complete"
call SETUP_TEAM.bat
popd

exit /b 0
