@echo off
REM =============================================================================
REM WeScope - SECURITY WIPE (Nuclear Option)
REM =============================================================================
echo.
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo WARNING: This will PERMANENTLY DELETE all WeScope browser data, including:
echo   1. All Client Browser Profiles (Saved Passwords, History, etc.)
echo   2. All Client Shortcuts on the Desktop
echo   3. The Automatic Update Task
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo.

REM Check Administrator Privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script must be run as Administrator!
    pause
    exit /b 1
)

set /p CONFIRM="Are you SURE you want to wipe all WeScope data? (TYPE 'WIPE' to confirm): "
if /i not "%CONFIRM%"=="WIPE" (
    echo [CANCELLED] No changes made.
    pause
    exit /b 0
)

echo.
echo [1/4] Stopping and removing Auto-Update task...
schtasks /delete /tn "WeScope Browser Auto-Update" /f >nul 2>&1
echo   [OK] Task removed.

echo [2/4] Deleting desktop shortcuts...
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\Client Systems Shortcuts"
if exist "%SHORTCUT_PATH%" (
    rmdir /s /q "%SHORTCUT_PATH%"
    echo   [OK] Shortcuts deleted.
)

echo [3/4] Wiping all profile data and assets (C:\Automation)...
REM We kill any running chrome instances first to release file locks
taskkill /f /im chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul
if exist "C:\Automation" (
    rmdir /s /q "C:\Automation"
    echo   [OK] C:\Automation wiped.
)

echo [4/4] Cleaning remaining policies...
reg delete "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallBlacklist" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallWhitelist" /f >nul 2>&1
echo   [OK] Policies cleaned.

echo.
echo ================================================================================
echo WIPE COMPLETE. All WeScope-related data has been removed.
echo ================================================================================
echo.
pause
exit /b 0
