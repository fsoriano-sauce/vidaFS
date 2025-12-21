@echo off
echo ================================================================================
echo ADMIN: REFRESH CLIENT SYSTEMS
echo ================================================================================
echo.
echo This script fetches the latest data from BigQuery and updates all shortcuts.
echo It will automatically publish updates to Google Drive for the team.
echo.

python "%~dp0internal_logic\client_browser_setup.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Refresh failed! Please check your internet and BigQuery access.
    pause
    exit /b %errorlevel%
)

echo.
echo ================================================================================
echo REFRESH COMPLETE!
echo Updates have been published to Google Drive.
echo ================================================================================
echo.
pause


