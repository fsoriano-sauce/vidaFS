# Client Browser Setup

Automated system to create custom Chrome browser profiles with desktop shortcuts for WeScope client systems.

## Quick Start

### For Admins (Generating Packages)

1. **Run the generator**:
   - Option A: Double-click `REFRESH_PACKAGES.bat`
   - Option B: Run `python client_browser_setup.py` manually

2. **Distribute**:
   - **Method 1 (Manual)**: Zip `For_Team_Complete/` and send to team members
   - **Method 2 (Network Share)**: Copy `For_Team_Complete/` to a shared network location

### For Team Members (Installing)

1. **From manual download**: Run `SETUP_TEAM.bat` as Administrator
2. **From network share**: Run `UPDATE_FROM_NETWORK.bat` as Administrator (edit script to set network path)

### Troubleshooting

If Chrome shows "managed by your organization" or password manager doesn't work:
1. Run `CLEANUP_POLICIES.bat` as Administrator
2. Close ALL Chrome windows (check Task Manager)
3. Restart Chrome

## Files

| File | Purpose |
|------|---------|
| `client_browser_setup.py` | Main Python script - fetches data, generates shortcuts |
| `SETUP_TEAM.bat` | Universal installer for team members (cleans policies, installs shortcuts) |
| `REFRESH_PACKAGES.bat` | Quick helper to regenerate `For_Team_Complete/` folder |
| `CLEANUP_POLICIES.bat` | Removes Chrome "managed by organization" policies |
| `UPDATE_FROM_NETWORK.bat` | Auto-pulls updates from network share (requires network path setup) |
| `download_extensions.py` | Helper to download Chrome extensions for side-loading |
| `subscription_reference.md` | Auto-generated subscription ID reference |
| `requirements.txt` | Python dependencies |

## Generated Output

| Folder | Purpose |
|--------|---------|
| `For_Team_Complete/` | **Distribution package** - zip and send this |
| `For_Team_Desktop/` | Staging folder (intermediate, gitignored) |

## Features

- **Data-Driven**: Fetches client systems from BigQuery (no hardcoding)
- **Smart Sorting**: Shortcuts prefixed by tier (1-PRO, 2-KEY, 3-NEW, 4-LEG)
- **Profile Management**: Creates isolated Chrome profiles in `C:\Automation\Profiles`
- **Safe Extensions**: Side-loads extensions per profile (Loom, ClickOnce) - does NOT impact personal browsers
- **URL Optimization**: Fixes known SSO issues (Xactimate, PSA, Westhill, etc.)
- **Deduplication**: Prevents duplicate tabs for the same system
- **Policy Protection**: Actively cleans registry policies to protect personal Chrome profiles
- **WeScope Portal**: Always opens as the last tab

## Requirements

- Python 3.8+
- Google Chrome
- BigQuery access (via `gcloud auth application-default login`)
