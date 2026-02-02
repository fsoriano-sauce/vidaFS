# Client Browser Setup

Automated system to create custom Chrome browser profiles with desktop shortcuts for WeScope client systems.

## Quick Start (Admin)

1. **Run the generator** (admin machine only):
   ```bat
   1_ADMIN_Refresh_Systems.bat
   ```
   This runs the python script located in `WeScope_Browser_Installer_Package/client_browser_setup.py`.

2. **Distribute**: The script creates `WeScope_Browser_Installer/` which contains the installer.
   - This folder is automatically published to Google Drive if configured.

3. **Team Installation**: Team members navigate to the G-Drive folder and run `SETUP_TEAM.bat` as Administrator.

## Folder Structure

- **WeScope_Browser_Installer_Package/**: Source code for the installer.
  - `client_browser_setup.py`: Main Python script.
  - `SETUP_TEAM.bat`: The core installer logic (Safe Installer with atomic extraction).
  - `WeScope_Browser_Installer/`: **Generated Output** - The distributable package.
- **3_EMERGENCY_WIPE.bat**: Utility to wipe all WeScope profiles/shortcuts from a machine.
- **1_ADMIN_Refresh_Systems.bat**: Wrapper to run the generation script.

## Historical Note: Launcher Strategy
*Previously, we used a `WESCOPE_BROWSER_INSTALLER.bat` launcher to copy files locally before running. This was removed in v4.1 in favor of a simpler direct-run approach from the G-Drive to reduce complexity and avoid execution policy errors.*

## Features

- **Safe Installer**: Uses atomic extraction (extract -> verify -> swap) to prevent empty folders.
- **Robust Desktop Detection**: Uses PowerShell to find the real Desktop path (OneDrive/Redirected safe).
- **Auto-Updates**: Scheduled task checks for updates every 15 minutes.
- **Fetches client data from BigQuery**: Generates sorted shortcuts (1-PRO, 2-KEY, 3-NEW, 4-LEG).
- **White-label URL fixes**: Handles NextGear, MICA, Verisk, etc.

## Troubleshooting

### Missing "Run as Administrator"
If you do not see the **"Run as Administrator"** option when right-clicking `SETUP_TEAM`, it is likely because the file is marked as **online-only** by Google Drive. Windows cannot run administrative tasks on files that are not physically on your computer.

**Fix:**
1. Right-click the `SETUP_TEAM` file in your Google Drive folder.
2. Select **Offline access** > **Available offline**.
3. Wait for the cloud icon next to the file to turn into a **green checkmark**.
4. Right-click the file again; the **"Run as Administrator"** option will now be available.
