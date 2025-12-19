@echo off
REM =============================================================================
REM WeScope Team - Client Browser Setup Script (Silent/Auto-Update Mode)
REM =============================================================================
REM This version runs without admin prompts for automatic background updates
REM =============================================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM [Step 1/3] Check for required files (silent)
if not exist "Automation.zip" exit /b 1
if not exist "Shortcuts.zip" exit /b 1

REM [Step 2/3] Installing Automation Assets (Icons, Dashboards, Extensions)
REM Create Profiles directory if needed
if not exist "C:\Automation\Profiles" (
    if exist "C:\Automation\My_Profiles" (
        move "C:\Automation\My_Profiles" "C:\Automation\Profiles" >nul 2>&1
    ) else if exist "C:\Automation\Ana_Profiles" (
        move "C:\Automation\Ana_Profiles" "C:\Automation\Profiles" >nul 2>&1
    ) else (
        mkdir "C:\Automation\Profiles" 2>nul
    )
)

REM Extract Automation.zip
pushd C:\
tar -xf "%SCRIPT_DIR%Automation.zip" >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Expand-Archive -Path '%SCRIPT_DIR%Automation.zip' -DestinationPath 'C:\' -Force" >nul 2>&1
    if %errorlevel% neq 0 (
        popd
        exit /b 1
    )
)
popd

REM [Step 2.5] Policy Cleanup (silently skip if not admin)
reg delete "HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallBlacklist" /f >nul 2>&1
reg delete "HKCU\Software\Policies\Google\Chrome" /v "ExtensionInstallWhitelist" /f >nul 2>&1

REM [Step 3/3] Installing Shortcuts to Desktop
powershell -Command "$d = [Environment]::GetFolderPath('Desktop'); $p = Join-Path $d 'Client Systems Shortcuts'; if (Test-Path $p) { Remove-Item $p -Recurse -Force }; New-Item -ItemType Directory -Path $p -Force | Out-Null; Expand-Archive -Path 'Shortcuts.zip' -DestinationPath $p -Force" >nul 2>&1
if %errorlevel% neq 0 exit /b 1

REM Refresh Icon Cache (silently)
ie4uinit.exe -show >nul 2>&1

exit /b 0


