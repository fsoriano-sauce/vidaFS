@echo off
REM =============================================================================
REM Extension Policy Verification Script
REM Verifies that Chrome extension policies are correctly configured
REM =============================================================================
setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo WeScope Extension Policy Verification
echo ================================================================================
echo.

set PASS_COUNT=0
set FAIL_COUNT=0
set EXPECTED_URL=https://clients2.google.com/service/update2/crx

echo [Step 1] Checking Registry Configuration...
echo.

REM Check Xactware ClickOnce Extension
echo Checking: Xactware ClickOnce Extension...
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "1" 2^>nul ^| findstr "1"') do set "EXT1_VALUE=%%b"

if defined EXT1_VALUE (
    echo !EXT1_VALUE! | findstr /i "ghonblphoimcehigdfdmomaochonfobc" >nul
    if !errorlevel! equ 0 (
        echo !EXT1_VALUE! | findstr /i "%EXPECTED_URL%" >nul
        if !errorlevel! equ 0 (
            echo   [PASS] Xactware ClickOnce: Configured with Web Store URL
            set /a PASS_COUNT+=1
        ) else (
            echo   [WARN] Xactware ClickOnce: Found but NOT using Web Store URL
            echo         Value: !EXT1_VALUE!
            set /a FAIL_COUNT+=1
        )
    ) else (
        echo   [FAIL] Xactware ClickOnce: Wrong extension ID in policy
        set /a FAIL_COUNT+=1
    )
) else (
    echo   [FAIL] Xactware ClickOnce: NOT configured in registry
    set /a FAIL_COUNT+=1
)

echo.

REM Check WeScope Autofill Extension
echo Checking: WeScope Autofill Extension...
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "2" 2^>nul ^| findstr "2"') do set "EXT2_VALUE=%%b"

if defined EXT2_VALUE (
    echo !EXT2_VALUE! | findstr /i "hhoilbbpbbfbihpafjobnfffffoocoba" >nul
    if !errorlevel! equ 0 (
        echo !EXT2_VALUE! | findstr /i "%EXPECTED_URL%" >nul
        if !errorlevel! equ 0 (
            echo   [PASS] WeScope Autofill: Configured with Web Store URL
            set /a PASS_COUNT+=1
        ) else (
            echo   [WARN] WeScope Autofill: Found but NOT using Web Store URL
            echo         Value: !EXT2_VALUE!
            set /a FAIL_COUNT+=1
        )
    ) else (
        echo   [FAIL] WeScope Autofill: Wrong extension ID in policy
        set /a FAIL_COUNT+=1
    )
) else (
    echo   [FAIL] WeScope Autofill: NOT configured in registry
    set /a FAIL_COUNT+=1
)

echo.
echo ================================================================================
echo RESULTS: %PASS_COUNT% passed, %FAIL_COUNT% failed
echo ================================================================================
echo.

if %FAIL_COUNT% gtr 0 (
    echo [ACTION REQUIRED] Run SETUP_TEAM.bat as Administrator to fix policy configuration.
    echo.
) else (
    echo [SUCCESS] All extension policies are correctly configured.
    echo.
    echo Next Steps:
    echo   1. Close ALL Chrome windows completely
    echo   2. Reopen Chrome
    echo   3. Navigate to chrome://extensions/
    echo   4. Wait 10-30 seconds for extensions to download
    echo   5. Both extensions should appear with "Installed by enterprise policy"
    echo.
)

echo Would you like to launch Chrome to verify extensions? (Y/N)
set /p LAUNCH="Choice: "
if /i "%LAUNCH%"=="Y" (
    echo.
    echo Launching Chrome to extensions page...
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" chrome://extensions/
)

echo.
pause
exit /b %FAIL_COUNT%
