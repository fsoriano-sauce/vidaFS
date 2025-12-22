@echo off
echo ================================================================================
echo Testing Chrome Policy-Based Extension Installation
echo ================================================================================
echo.
echo This script will:
echo 1. Configure Chrome extension policies (same as SETUP_TEAM.bat)
echo 2. Launch Chrome to verify extensions load automatically
echo.
pause

echo Step 1: Configuring Extension Policies...
echo.

REM Create ExtensionInstallForcelist key
reg add "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /f >nul 2>&1

REM Xactware ClickOnce Extension - Install from Chrome Web Store
reg add "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "1" /t REG_SZ /d "ghonblphoimcehigdfdmomaochonfobc;https://clients2.google.com/service/update2/crx" /f >nul 2>&1

REM WeScope Autofill Extension - Install from Chrome Web Store
reg add "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "2" /t REG_SZ /d "hhoilbbpbbfbihpafjobnfffffoocoba;https://clients2.google.com/service/update2/crx" /f >nul 2>&1

echo [OK] Extension policies configured.
echo.
echo Step 2: Launching Chrome...
echo.
echo IMPORTANT: Close ALL Chrome windows first, then press any key.
pause

REM Launch Chrome to extensions page
"C:\Program Files\Google\Chrome\Application\chrome.exe" chrome://extensions/

echo.
echo ================================================================================
echo CHECK THE CHROME WINDOW:
echo ================================================================================
echo.
echo You should see 2 extensions installed:
echo   1. Xactware ClickOnce
echo   2. WeScope Autofill
echo.
echo Both should show "Installed by enterprise policy" or similar.
echo.
echo If extensions don't appear:
echo   - Make sure Chrome was fully closed before launching
echo   - Wait 5-10 seconds for Chrome to process the policy
echo   - Refresh the extensions page (F5)
echo.
echo ================================================================================
pause
