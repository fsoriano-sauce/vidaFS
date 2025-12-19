@echo off
REM launcher for the team installer
echo [DEBUG] Launching WeScope Browser Installer...
call "%~dp0internal_logic\WESCOPE_BROWSER_INSTALLER.bat"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Launcher failed with code %errorlevel%
    pause
)
