================================================================================
CLIENT BROWSER SHORTCUTS - SETUP INSTRUCTIONS FOR FRANKIE
================================================================================

WHAT THIS IS:
-------------
This package creates desktop shortcuts for each client. When you click a 
shortcut, it opens Chrome with all of that client's systems in separate tabs
(in the correct order).

WHAT'S INCLUDED:
----------------
1. Frankie_Desktop_Shortcuts.zip  - Desktop shortcut icons for each client
2. Ana_Dashboards.zip             - Client dashboard HTML files (shared)
3. SETUP_FOR_FRANKIE.bat          - Automated setup script (THIS IS EASIEST!)
4. README_FOR_FRANKIE.txt         - This file


EASY SETUP (RECOMMENDED):
-------------------------
1. Extract the package to any folder
2. Right-click "SETUP_FOR_FRANKIE.bat" 
3. Select "Run as Administrator"
4. Follow the prompts!

The script will automatically:
- Update your shortcuts and dashboards
- Preserve your existing logins/profiles


MANUAL SETUP (IF YOU PREFER):
------------------------------
1. Create folder: C:\Automation\My_Profiles
   
2. Create folder: C:\Automation\Dashboards

3. Extract "Ana_Dashboards.zip" to C:\Automation\Dashboards

4. Extract "Frankie_Desktop_Shortcuts.zip" to your Desktop

5. Done! The shortcuts should now work.


NOTE: Profile folders start EMPTY. Chrome creates your profile data when you
first log in to each system.


HOW TO USE:
-----------
1. Double-click any client shortcut on your Desktop
   Example: "SM RSI - Ada"

2. Chrome will open with all systems for that client in tabs:
   - Dashboard (first tab - shows the client name)
   - CRM system
   - Documentation apps 
   - Estimating systems (XactAnalysis, Xactimate, ContentsTrack, Symbility)
   - MICA and others

3. Log in to each system ONCE
   - Chrome will remember your login for next time
   - You may need to manually enter Company Code for some systems

4. Close Chrome when done

5. Next time you click the shortcut, you should be automatically logged in!


TAB ORDER:
----------
Tabs open left to right in this order:
1. Client Dashboard (shows client name in window title)
2. CRM Systems (RESTORE365, Dash, etc.)
3. Documentation Apps (Encircle, CompanyCam, DocuSketch)
4. Estimating Systems (XactAnalysis → Xactimate → ContentsTrack → Symbility)
5. MICA
6. Others


TROUBLESHOOTING:
----------------
Q: Shortcuts don't work?
A: Make sure profiles are at: C:\Automation\My_Profiles

Q: Not staying logged in?
A: Some systems (like Symbility, MICA) log you out when you close the browser.
   This is normal. Just log in again.


================================================================================
Happy browsing!
================================================================================
