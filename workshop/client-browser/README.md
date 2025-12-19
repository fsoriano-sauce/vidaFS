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

**First-Time Setup:**
1. Run `SETUP_TEAM.bat` as Administrator (installs shortcuts to Desktop)

**Optional - Enable Auto-Updates:**
2. Share `For_Team_Complete` via Google Drive (or similar sync service)
3. Team members run `SETUP_AUTO_UPDATE.bat` and enter their synced folder path
4. Updates check every 4 hours and install automatically in the background

See `TEAM_SETUP_GUIDE.md` for detailed instructions.

### Troubleshooting

If Chrome shows "managed by your organization" or password manager doesn't work:
1. Run `CLEANUP_POLICIES.bat` as Administrator
2. Close ALL Chrome windows (check Task Manager)
3. Restart Chrome

## Files

### Admin Files (Package Generation)
| File | Purpose |
|------|---------|
| `client_browser_setup.py` | Main Python script - fetches data from BigQuery, generates shortcuts |
| `REFRESH_PACKAGES.bat` | Quick helper to regenerate `For_Team_Complete/` folder |
| `download_extensions.py` | Helper to download Chrome extensions for side-loading |
| `requirements.txt` | Python dependencies |

### Team Files (Distribution)
| File | Purpose |
|------|---------|
| `SETUP_TEAM.bat` | Main installer (cleans policies, installs shortcuts) |
| `SETUP_AUTO_UPDATE.bat` | One-time setup for automatic background updates |
| `CLEANUP_POLICIES.bat` | Troubleshooting - removes "managed by organization" policies |
| `TEAM_SETUP_GUIDE.md` | Complete guide for team members |
| `version.txt` | Auto-generated version timestamp for update tracking |

### Generated Files
| File | Purpose |
|------|---------|
| `subscription_reference.md` | Auto-generated subscription ID reference |
| `Automation.zip` | Icons, Dashboards, Extensions (extracted to `C:\Automation\`) |
| `Shortcuts.zip` | Desktop shortcuts (extracted to `Desktop\Client Systems Shortcuts\`) |

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
