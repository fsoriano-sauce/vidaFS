@echo off
echo ================================================================================
echo REFRESH PACKAGES
echo ================================================================================
echo.
echo This script will regenerate the client browser deployment packages based on
echo the latest data from BigQuery.
echo.
echo Running client_browser_setup.py...
echo.

python "%~dp0client_browser_setup.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python script failed!
    pause
    exit /b %errorlevel%
)

echo.
echo ================================================================================
echo REFRESH COMPLETE!
echo Packages are ready in: %~dp0For_Team_Complete
echo ================================================================================
echo.
pause




