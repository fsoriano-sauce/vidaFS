@echo off
REM =============================================================================
REM WeScope Team - Client Browser Setup Script (Universal)
REM =============================================================================

echo.
echo ================================================================================
echo WeScope Team Browser Setup
echo ================================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [Step 1/3] Checking for required files...
echo NOTE: Do NOT unzip the archives manually. This script processes them.

if not exist "Automation.zip" (
    echo [ERROR] Automation.zip not found!
    pause
    exit /b 1
)
if not exist "Shortcuts.zip" (
    echo [ERROR] Shortcuts.zip not found!
    pause
    exit /b 1
)
echo   [OK] Files found

echo.
echo [Step 2/3] Installing Automation Assets (Icons, Dashboards)...
REM Ensure Chrome is closed to release file locks (Gentle warning)
echo NOTE: If you see "Access Denied" errors below, please close Chrome and retry.

REM --------------------------------------------------------------------------
REM MIGRATION LOGIC: Unify Profiles into C:\Automation\Profiles
REM --------------------------------------------------------------------------
if not exist "C:\Automation\Profiles" (
    REM Check for legacy folders and rename them
    if exist "C:\Automation\My_Profiles" (
        echo [MIGRATION] Migrating 'My_Profiles' to 'Profiles'...
        move "C:\Automation\My_Profiles" "C:\Automation\Profiles" >nul
    ) else if exist "C:\Automation\Ana_Profiles" (
        echo [MIGRATION] Migrating 'Ana_Profiles' to 'Profiles'...
        move "C:\Automation\Ana_Profiles" "C:\Automation\Profiles" >nul
    ) else (
        REM Create fresh if nothing exists
        mkdir "C:\Automation\Profiles"
    )
) else (
    REM Destination already exists.
    REM If legacy folders ALSO exist, we should probably warn or remove them?
    REM For safety, we just leave them alone or hide them.
    if exist "C:\Automation\My_Profiles" (
        echo [INFO] Found unused 'My_Profiles'. 'Profiles' is already active.
    )
)

REM --------------------------------------------------------------------------

REM Try 'tar' by changing directory to C:\ (avoids flag parsing issues)
pushd C:\
tar -xf "%SCRIPT_DIR%Automation.zip"
if %errorlevel% neq 0 (
    echo [WARNING] 'tar' failed. Trying PowerShell fallback...
    powershell -Command "Expand-Archive -Path '%SCRIPT_DIR%Automation.zip' -DestinationPath 'C:\' -Force"
    if %errorlevel% neq 0 (
        popd
        echo [ERROR] Failed to extract Automation.zip!
        pause
        exit /b 1
    )
)
popd
echo   [OK] Automation folder installed to C:\Automation

echo.
echo [Step 2.5] Configuring Chrome Extensions...
REM NOTE: Registry policies are disabled to prevent impacting personal Chrome profiles.
REM If extensions (Loom, ClickOnce, etc.) are required, they must be installed manually or 
REM enabled via a different mechanism that does not affect global HKCU policies.
REM reg add "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "901" /t REG_SZ /d "hhoilbbpbbfbihpafjobnfffffoocoba;https://clients2.google.com/service/update2/crx" /f >nul 2>&1
REM reg add "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /v "902" /t REG_SZ /d "ghonblphoimcehigdfdmomaochonfobc;https://clients2.google.com/service/update2/crx" /f >nul 2>&1
echo   [SKIPPED] Global Extension Policy (User Request)

echo.
echo [Step 3/3] Installing Shortcuts to Desktop...
REM Extract to 'Client Systems Shortcuts' folder on Desktop (Clean Install)
powershell -Command "$d = [Environment]::GetFolderPath('Desktop'); $p = Join-Path $d 'Client Systems Shortcuts'; if (Test-Path $p) { Remove-Item $p -Recurse -Force }; New-Item -ItemType Directory -Path $p -Force | Out-Null; Expand-Archive -Path 'Shortcuts.zip' -DestinationPath $p -Force"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install shortcuts!
    pause
    exit /b 1
)
echo   [OK] Shortcuts installed to Desktop\Client Systems Shortcuts

REM Refresh Icon Cache
ie4uinit.exe -show >nul 2>&1

echo.
echo ================================================================================
echo SUCCESS! Setup Complete!
echo You can now use the shortcuts in the "Client Systems Shortcuts" folder.
echo ================================================================================
echo.
pause
