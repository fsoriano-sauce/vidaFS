@echo off
echo ================================================================================
echo WeScope Browser Policy Cleanup
echo ================================================================================
echo.
echo This script removes the "Installed by administrator" extension policies
echo that were accidentally applied to your personal Chrome profile.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

echo Removing legacy extension policies...

REM Remove entire ExtensionInstallForcelist key
reg delete "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Removed ExtensionInstallForcelist key
) else (
    echo   [INFO] ExtensionInstallForcelist key not found or already removed.
)

REM Also try removing individual policies (legacy cleanup)
reg delete "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "901" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "902" /f >nul 2>&1

REM Remove any other Chrome policies that might cause "managed" state
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallBlacklist" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallWhitelist" /f >nul 2>&1

echo   [OK] Policy cleanup complete

REM Refresh Group Policy (force update)
gpupdate /force >nul 2>&1

echo.
echo ================================================================================
echo CLEANUP COMPLETE!
echo Please restart all Chrome windows for changes to take effect.
echo ================================================================================
echo.
pause








