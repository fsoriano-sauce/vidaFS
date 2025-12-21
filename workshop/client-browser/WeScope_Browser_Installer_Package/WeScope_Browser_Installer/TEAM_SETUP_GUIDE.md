# WeScope Client Browser Setup - Team Guide

## 🚀 One-Time Setup (New Team Members)

1.  **Download** the **`WESCOPE_BROWSER_INSTALLER.bat`** file sent by Frank.
2.  Save it anywhere (Downloads or Desktop).
3.  Right-click the file and select **Run as Administrator**.
4.  **When prompted**, type **`Y`** to enable automatic background updates.
5.  **Done!** Your shortcuts are installed in `Desktop\Client Systems Shortcuts` and will now update themselves automatically every 15 minutes.

---

## 🔄 How it Works

- **Launcher Experience**: The file you download is a "launcher" that reaches out to the WeScope Google Drive to install the latest files.
- **No Manual Downloads**: You don't need to manage zip files or folders.
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
