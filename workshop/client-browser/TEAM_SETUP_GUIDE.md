# WeScope Client Browser Setup - Team Guide

## 🚀 First-Time Setup (New Team Members)

### Option A: Manual Setup (Traditional)

1. **Download** the latest `For_Team_Complete` folder from the shared location
2. **Run** `SETUP_TEAM.bat` as Administrator (right-click → "Run as Administrator")
3. **Done!** Find your shortcuts in `Desktop\Client Systems Shortcuts`

---

### Option B: Auto-Update Setup (Recommended)

This setup allows shortcuts to update automatically in the background—no manual downloads needed!

#### Step 1: One-Time Google Drive Setup
1. Install [Google Drive for Desktop](https://www.google.com/drive/download/) if not already installed
2. Sign in with your WeScope Google account
3. The admin will share a folder called **"WeScope Browser Updates"** with you
4. Ensure this folder is **synced** to your computer (check Google Drive settings)
5. Note the local path (e.g., `G:\My Drive\WeScope Browser Updates\For_Team_Complete`)

#### Step 2: Run Initial Setup
1. Download and extract the initial `For_Team_Complete` folder
2. Run `SETUP_TEAM.bat` as Administrator
3. ✅ Your shortcuts are now installed!

#### Step 3: Enable Auto-Updates
1. From the same folder, run `SETUP_AUTO_UPDATE.bat` as Administrator
2. When prompted, enter your Google Drive sync path:
   ```
   Example: G:\My Drive\WeScope Browser Updates\For_Team_Complete
   ```
3. ✅ Done! Updates will now check every 15 minutes automatically

---

## 🔄 How Auto-Updates Work

- **Automatic**: Checks for updates every 15 minutes in the background
- **Silent**: No popups or interruptions
- **Smart**: Only updates if a new version is available
- **Safe**: Existing profiles and data are preserved
- **Logged**: View update history at `C:\Automation\update.log`

---

## 🩹 Troubleshooting

### Chrome shows "Managed by your organization"

**Solution:**
1. Run `CLEANUP_POLICIES.bat` as Administrator
2. Close **all** Chrome windows (verify in Task Manager)
3. Restart Chrome

### Password Manager not saving passwords

This is usually caused by the "Managed by organization" issue above. Follow the same steps.

### Auto-updates not working

**Check:**
1. Is Google Drive for Desktop running?
2. Is the "WeScope Browser Updates" folder synced?
3. Check `C:\Automation\update.log` for error messages

**Manual update:**
```batch
C:\Automation\AUTO_UPDATE.bat
```

### Shortcuts not updating

**Force refresh:**
1. Delete `C:\Automation\.version`
2. Run `C:\Automation\AUTO_UPDATE.bat`
3. Restart any open client browser windows

---

## 📁 File Locations

| Location | Purpose |
|----------|---------|
| `Desktop\Client Systems Shortcuts\` | Your browser shortcuts (organized by tier) |
| `C:\Automation\Profiles\` | Chrome profile data (passwords, history, etc.) |
| `C:\Automation\Icons\` | Client icons |
| `C:\Automation\Extensions\` | Side-loaded Chrome extensions (Loom, ClickOnce) |
| `C:\Automation\AUTO_UPDATE.bat` | Auto-update script |
| `C:\Automation\.version` | Current installed version |
| `C:\Automation\update.log` | Update history log |

---

## ❓ FAQ

### Can I delete old shortcuts?

Yes! Simply delete shortcuts from the `Client Systems Shortcuts` folder. They'll be recreated if the admin adds them back.

### Will updates delete my saved passwords?

**No!** Your Chrome profile data in `C:\Automation\Profiles\` is never touched by updates. Only shortcuts and assets (icons, dashboards) are updated.

### Can I customize the update frequency?

Yes! Edit the scheduled task:
1. Open Task Scheduler
2. Find "WeScope Browser Auto-Update"
3. Change the interval (default: every 15 minutes)

### What if I don't want auto-updates?

Simply don't run `SETUP_AUTO_UPDATE.bat`. You can always update manually by:
1. Downloading the latest `For_Team_Complete`
2. Running `SETUP_TEAM.bat`

---

## 🆘 Need Help?

Contact Frank or check the update log: `C:\Automation\update.log`


