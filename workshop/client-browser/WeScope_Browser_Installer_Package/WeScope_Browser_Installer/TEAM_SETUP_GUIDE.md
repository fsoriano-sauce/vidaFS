# WeScope Client Browser Setup - Team Guide

## 🚀 Setup Instructions

1.  **Navigate** to the shared folder on Google Drive:
    `G:\Shared drives\Client Shortcuts\WeScope_Browser_Installer`
    *(If you don't have the G: drive, ensure Google Drive for Desktop is running)*

2.  **Run the Installer**:
    *   Right-click on **`SETUP_TEAM.bat`**
    *   Select **Run as Administrator**

3.  **Follow Prompts**:
    *   If asked, type **`Y`** to enable automatic background updates.

4.  **Done!** Your shortcuts are installed in `Desktop\Client Systems Shortcuts` and will now update themselves automatically every 15 minutes.

---

## 🔄 How it Works

- **Direct Install**: The script runs directly from the shared drive to install shortcuts to your local desktop.
- **Auto-Updates**: A hidden task checks for new client systems every 15 minutes.
- **Safe**: Your saved passwords and work profiles are never touched.
- **Silent**: Updates happen in the background without popups.

---

## 🩹 Troubleshooting

### "Google Drive folder not found" error
1. Ensure **Google Drive for Desktop** is running and you are signed in.
2. Ensure the **'Client Shortcuts'** shared drive is visible in your Windows Explorer.
3. Ensure your Google Drive is mounted as the **G:** drive (this is the default).

### Chrome shows "Managed by your organization"
1. Browse to `G:\Shared drives\Client Shortcuts\WeScope_Browser_Installer`
2. Run **`CLEANUP_POLICIES.bat`** as Administrator.
3. Close all Chrome windows and restart.

### Emergency: Security Wipe (Remove everything)
If you need to completely remove all WeScope data (profiles, passwords, and shortcuts):
1. **Warning**: This will remove all data.
2. Run the **`3_EMERGENCY_WIPE.bat`** script provided by Admin (not included in standard distribution).

---

## 🆘 Need Help?
Contact Frank or check the update log: `C:\Automation\update.log`
