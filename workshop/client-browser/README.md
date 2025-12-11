# Client Browser Setup

Workshop folder for the Client Browser project that creates custom Chrome browser profiles and desktop shortcuts with unique icons for each client.

## Features

- Fetches client data from BigQuery or uses demo data
- Creates separate Chrome profiles for each client
- Generates custom colored icons with client initials
- Creates desktop shortcuts with custom icons
- Supports both personal use and shared profiles (for Ana)

## Prerequisites

1. **Python 3.7+** - Download from [python.org](https://python.org) or install via Microsoft Store
2. **Google Chrome** - Must be installed at the default location
3. **Required Python packages** - Install with: `pip install -r requirements.txt`

## Installation & Setup

1. **Install Python** (if not already installed):
   - Go to [python.org](https://python.org) and download Python 3.8 or later
   - During installation, make sure to check "Add Python to PATH"

2. **Install dependencies**:
   ```bash
   cd workshop/client-browser
   pip install -r requirements.txt
   ```

3. **Run the setup script**:
   ```bash
   python client_browser_setup.py
   ```

   Or use the provided batch file:
   ```bash
   run_setup.bat
   ```

## What It Does

1. **Fetches client data** from BigQuery (or uses demo data if BigQuery is unavailable)
2. **Creates Chrome profiles** for each client in:
   - `C:\Automation\My_Profiles\` (for personal use)
   - `C:\Automation\Ana_Profiles\` (for shared use)
3. **Generates custom icons** with:
   - Unique colors based on client name
   - Client initials as text
   - Multiple sizes (256x256, 128x128, 64x64, 32x32, 16x16)
4. **Creates desktop shortcuts** with custom icons for easy access

## Generated Files

- **Icons**: Stored in `client_icons/` folder as `.ico` files
- **Shortcuts**: Created on your Desktop and in `For_Ana_Desktop/` folder
- **Profiles**: Chrome user data directories for each client

## Troubleshooting

- **"Python not found"**: Install Python and add it to your PATH
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Chrome not found**: Ensure Chrome is installed in the default location
- **Permission errors**: Run as Administrator if needed

## Demo Mode

If BigQuery is not available or you're on a non-Windows system, the script runs in demo mode with mock data.
