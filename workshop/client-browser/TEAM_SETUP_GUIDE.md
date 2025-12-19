# WeScope Client Browser Setup - Team Guide

## 🚀 One-Time Setup (New Team Members)

1.  **Open Google Drive** on your computer and go to:
    `G:\Shared drives\Client Shortcuts\For_Team_Complete`
2.  Right-click **`SETUP_TEAM.bat`** and select **Run as Administrator**.
3.  **When prompted**, type **`Y`** to enable automatic background updates.
4.  **Done!** Your shortcuts are installed in `Desktop\Client Systems Shortcuts` and will now update themselves automatically every 15 minutes.

---

## 🔄 How it Works

- **No more downloads**: You just run the script once from Google Drive.
- **Auto-Updates**: A hidden task checks for new client systems every 15 minutes.
- **Safe**: Your saved passwords and work profiles are never touched.
- **Silent**: Updates happen in the background without popups.

---

## 🩹 Troubleshooting

### Chrome shows "Managed by your organization"
1. Run **`CLEANUP_POLICIES.bat`** as Administrator.
2. Close all Chrome windows and restart.

### Password Manager not saving passwords
This is usually caused by the "Managed by organization" issue above. Follow the same steps.

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

## 🆘 Need Help?
Contact Frank or check the update log: `C:\Automation\update.log`
