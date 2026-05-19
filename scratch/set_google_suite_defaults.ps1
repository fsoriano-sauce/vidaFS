#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Updates Windows file associations to use the Google Suite auto-convert handler.
.DESCRIPTION
    Points all Office file types to the open_in_google.ps1 handler script, which 
    uploads to Google Drive with auto-conversion and opens the native Google editor.
#>

$ErrorActionPreference = 'Continue'

$handlerScript = "C:\Automation\GoogleSuiteHandler\open_in_google.ps1"
if (-not (Test-Path $handlerScript)) {
    Write-Error "Handler script not found at $handlerScript"
    exit 1
}

# The command that Windows will run when opening these file types.
# We use a hidden PowerShell window so no console flashes on double-click.
$pwshPath = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
$openCommand = "`"$pwshPath`" -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$handlerScript`" `"%1`""

Write-Host "Handler command: $openCommand" -ForegroundColor Cyan

# --- Define ProgIDs ---
$handlers = @(
    @{
        ProgId      = 'GoogleDocs.Document'
        Description = 'Google Docs (auto-convert)'
        Extensions  = @('.docx', '.doc', '.rtf')
    },
    @{
        ProgId      = 'GoogleSheets.Spreadsheet'
        Description = 'Google Sheets (auto-convert)'
        Extensions  = @('.xlsx', '.xls', '.csv')
    },
    @{
        ProgId      = 'GoogleSlides.Presentation'
        Description = 'Google Slides (auto-convert)'
        Extensions  = @('.pptx', '.ppt')
    }
)

# --- Register ProgIDs ---
foreach ($handler in $handlers) {
    $progId = $handler.ProgId
    $desc   = $handler.Description
    $regBase = "HKLM:\Software\Classes\$progId"
    
    New-Item -Path "$regBase\shell\open\command" -Force | Out-Null
    Set-ItemProperty -Path $regBase -Name '(Default)' -Value $desc
    Set-ItemProperty -Path "$regBase\shell\open\command" -Name '(Default)' -Value $openCommand
    
    # Friendly name for "Open With" dialog
    New-Item -Path "$regBase\Application" -Force | Out-Null
    Set-ItemProperty -Path "$regBase\Application" -Name 'ApplicationName' -Value $desc
    
    Write-Host "  Registered: $progId" -ForegroundColor Green
    
    foreach ($ext in $handler.Extensions) {
        # Machine-level association
        $null = cmd /c "assoc $ext=$progId" 2>&1
        $null = cmd /c "ftype $progId=$openCommand" 2>&1
        
        # Add to OpenWithProgids
        $openWithPath = "HKCU:\Software\Classes\$ext\OpenWithProgids"
        New-Item -Path $openWithPath -Force | Out-Null
        New-ItemProperty -Path $openWithPath -Name $progId `
            -Value ([byte[]]@()) -PropertyType Binary -Force | Out-Null
        
        # Clear UserChoice
        $userChoicePath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$ext\UserChoice"
        if (Test-Path $userChoicePath) {
            try {
                $regKey = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey(
                    "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$ext\UserChoice",
                    [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree,
                    [System.Security.AccessControl.RegistryRights]::TakeOwnership
                )
                if ($regKey) {
                    $acl = $regKey.GetAccessControl()
                    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
                    $acl.SetOwner([System.Security.Principal.NTAccount]$currentUser)
                    $regKey.SetAccessControl($acl)
                    $acl = $regKey.GetAccessControl()
                    $rule = New-Object System.Security.AccessControl.RegistryAccessRule(
                        $currentUser,
                        [System.Security.AccessControl.RegistryRights]::FullControl,
                        [System.Security.AccessControl.AccessControlType]::Allow
                    )
                    $acl.AddAccessRule($rule)
                    $regKey.SetAccessControl($acl)
                    $regKey.Close()
                    Remove-Item -Path $userChoicePath -Force -ErrorAction Stop
                    Write-Host "    $ext : Cleared old default" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "    $ext : Could not clear UserChoice" -ForegroundColor DarkYellow
            }
        }
        
        Write-Host "    $ext -> $($handler.Description)" -ForegroundColor White
    }
}

# Restart Explorer
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
if (-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) {
    Start-Process explorer.exe
}

Write-Host "`n=== DONE ===" -ForegroundColor Green
Write-Host "Double-clicking Office files will now auto-convert to Google Suite." -ForegroundColor White
