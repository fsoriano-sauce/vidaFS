Write-Host "Checking Windows Features for WSL..."
try {
    $vmp = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -ErrorAction Stop
    $wsl = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -ErrorAction Stop

    Write-Host "VirtualMachinePlatform: $($vmp.State)"
    Write-Host "Microsoft-Windows-Subsystem-Linux: $($wsl.State)"

    if ($vmp.State -ne 'Enabled' -or $wsl.State -ne 'Enabled') {
        Write-Host "Enabling features... (Check for UAC prompt)"
        Start-Process powershell -Verb RunAs -ArgumentList "-NoExit -Command Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform,Microsoft-Windows-Subsystem-Linux -All"
        Write-Host "Action required in the new window."
    } else {
        Write-Host "✅ Application features are correctly ENABLED."
        Write-Host "⚠️  ERROR PERSISTS: This confirms Virtualization is disabled in your BIOS/UEFI."
        Write-Host "   Action: Restart computer -> Enter BIOS -> Enable Intel VMX or AMD SVM."
    }
} catch {
    Write-Host "❌ Failed to check status (need Admin privileges)."
    Write-Host "Attempting to run as Admin..."
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit -File '$($MyInvocation.MyCommand.Path)'"
}
Read-Host "Press Enter to close..."
