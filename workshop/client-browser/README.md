# Client Browser Setup

Automated system to create custom Chrome browser profiles with desktop shortcuts for WeScope client systems.

## Quick Start

1. **Run the generator** (admin machine only):
   ```bash
   python client_browser_setup.py
   ```

2. **Distribute**: Zip `For_Team_Complete/` and send to team members.

3. **Team installs**: Run `SETUP_TEAM.bat` as Administrator.

## Files

| File | Purpose |
|------|---------|
| `client_browser_setup.py` | Main Python script - fetches data, generates shortcuts |
| `SETUP_TEAM.bat` | Universal installer for team members |
| `subscription_reference.md` | Auto-generated subscription ID reference |
| `requirements.txt` | Python dependencies |

## Generated Output

| Folder | Purpose |
|--------|---------|
| `For_Team_Complete/` | **Distribution package** - zip and send this |
| `For_Team_Desktop/` | Staging folder (intermediate, gitignored) |

## Features

- Fetches client data from BigQuery
- Generates sorted shortcuts (1-PRO, 2-KEY, 3-NEW, 4-LEG)
- Creates unified `C:\Automation\Profiles` directory
- Installs Chrome extensions via policy (Loom, Translate)
- Opens WeScope portal as last tab
- Handles white-label URL fixes (NextGear, MICA, etc.)

## Requirements

- Python 3.8+
- Google Chrome
- BigQuery access (via `gcloud auth application-default login`)
