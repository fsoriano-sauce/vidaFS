@echo off
REM =============================================================================
REM WeScope Browser - Unified Installer Launcher (v3.5)
REM =============================================================================
setlocal enabledelayedexpansion

:: 1. Auto-Elevate to Administrator (Using FULL path %~f0)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Requesting Administrator privileges...
    :: We use %~f0 to pass the ABSOLUTE path to the elevated process
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: 2. Fix Working Directory (Force it to the folder where THIS script lives)
cd /d "%~dp0"

echo.
echo  --------------------------------------------------
echo    WESCOPE CLIENT SYSTEMS - INSTALLER LOADER
echo  --------------------------------------------------
echo.
echo  [1/2] Reaching out to WeScope Google Drive...

:: 3. Define Master Path (The brains on G:)
set "MASTER_PATH=G:\Shared drives\Client Shortcuts\For_Team_Complete\SETUP_TEAM.bat"

:: 4. Check for G: Drive
if not exist "G:\" (
    echo.
    echo  [ERROR] Google Drive (G:) is NOT MOUNTED.
    echo  Please ensure Google Drive for Desktop is running.
    echo.
    pause
    exit /b 1
)

:: 5. Check for Master Setup
if not exist "%MASTER_PATH%" (
    echo.
    echo  [ERROR] Master Installer not found on G: Drive.
    echo  Checked: "%MASTER_PATH%"
    echo.
    pause
    exit /b 1
)

echo  [2/2] Launching Master Setup...
echo.
echo  --------------------------------------------------
echo.

:: 6. Run the actual installer from G:
pushd "G:\Shared drives\Client Shortcuts\For_Team_Complete"
call SETUP_TEAM.bat
set INSTALLER_EXIT_CODE=%errorlevel%
popd

:: 7. Final Success/Error Handling
if %INSTALLER_EXIT_CODE% equ 0 (
    cls
    echo.
    echo ================================================================================
    echo                    WESCOPE SETUP SUCCESSFUL!
    echo ================================================================================
    echo.
    echo   - Client shortcuts are now on your Desktop.
    echo   - Updates will happen automatically every 15 minutes (Invisible).
    echo   - You can close this window now.
    echo.
    echo ================================================================================
    pause
) else (
    echo.
    echo [ERROR] The installer failed (Code: %INSTALLER_EXIT_CODE%)
    pause
)

exit /b 0
