# Client Browser Setup

Automated system to create custom Chrome browser profiles with desktop shortcuts for WeScope client systems.

## Quick Start (Admin)

1. **Run the generator** (admin machine only):
   ```bat
   1_ADMIN_Refresh_Systems.bat
   ```
   This runs the python script located in `WeScope_Browser_Installer_Package/client_browser_setup.py`.

2. **Distribute**: The script creates `Script_Output_For_Distribution/` which contains the installer.
   - This folder is automatically published to Google Drive if configured.

3. **Team Installation**: Team members run `WESCOPE_BROWSER_INSTALLER.bat` (Launcher v4.0).

## Folder Structure

- **WeScope_Browser_Installer_Package/**: Source code for the installer.
  - `client_browser_setup.py`: Main Python script.
  - `SETUP_TEAM.bat`: The core installer logic (Safe Installer with atomic extraction).
  - `WESCOPE_BROWSER_INSTALLER.bat`: The user-facing launcher.
  - `Script_Output_For_Distribution/`: **Generated Output** - The distributable package.
- **3_EMERGENCY_WIPE.bat**: Utility to wipe all WeScope profiles/shortcuts from a machine.
- **1_ADMIN_Refresh_Systems.bat**: Wrapper to run the generation script.

## Features

- **Safe Installer**: Uses atomic extraction (extract -> verify -> swap) to prevent empty folders.
- **Robust Desktop Detection**: Uses PowerShell to find the real Desktop path (OneDrive/Redirected safe).
- **Auto-Updates**: Scheduled task checks for updates every 15 minutes.
- **Fetches client data from BigQuery**: Generates sorted shortcuts (1-PRO, 2-KEY, 3-NEW, 4-LEG).
- **White-label URL fixes**: Handles NextGear, MICA, Verisk, etc.

## Requirements

- Python 3.8+
- Google Chrome
- BigQuery access (via `gcloud auth application-default login`)
