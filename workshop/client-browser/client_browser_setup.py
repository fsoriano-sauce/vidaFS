import os
import sys
import time
import re
from typing import List, Dict, DefaultDict
from collections import defaultdict

# --- CROSS-PLATFORM COMPATIBILITY SETUP ---
IS_WINDOWS = os.name == 'nt'
DEMO_MODE = not IS_WINDOWS

# Third-party imports (Conditional)
try:
    from google.cloud import bigquery
    HAS_BIGQUERY = True
except ImportError:
    HAS_BIGQUERY = False

try:
    from PIL import Image, ImageDraw, ImageFont
    import colorsys
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

if IS_WINDOWS:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        import win32com.client
        import winshell
    except ImportError:
        pass # Handle in main
else:
    print("Non-Windows Environment detected. Running in DEMO MODE.")

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

if IS_WINDOWS:
    # Production Windows Paths
    BASE_DIR_SELF = r"C:\Automation\My_Profiles"
    BASE_DIR_ANA = r"C:\Automation\Ana_Profiles"
    SHORTCUT_DIR_ANA = os.path.join(os.getcwd(), "For_Ana_Desktop")
    CHROME_EXE_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
else:
    # Demo Linux Paths (Current Directory)
    BASE_DIR_SELF = os.path.abspath("./dist/Automation/My_Profiles")
    BASE_DIR_ANA = os.path.abspath("./dist/Automation/Ana_Profiles")
    SHORTCUT_DIR_ANA = os.path.abspath("./dist/For_Ana_Desktop")
    CHROME_EXE_PATH = "/usr/bin/google-chrome" # Mock
    print(f"DEMO PATHS:\n  Self Profiles: {BASE_DIR_SELF}\n  Ana Profiles: {BASE_DIR_ANA}\n")

# BigQuery Settings
BQ_PROJECT_ID = "xano-fivetran-bq"
BQ_QUERY = """
    SELECT
        c.full_name as client_name,
        sa.link as login_url
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l
    ON
        c.id = l.client_id
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access` sa
    ON
        l.system_access_id = sa.id
    WHERE
        c.subscription_id = 14
        AND sa.link IS NOT NULL
        AND sa.link != ''
        AND l.archived = false
"""

# Icon Settings
ICON_SIZE = (256, 256)
ICON_DIR = os.path.join(os.getcwd(), "client_icons")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def clean_target_url(url: str) -> str:
    """
    Removes specific login paths from the URL so the browser lands on the dashboard
    if the session is already active.
    """
    # Patterns to strip from the END of the URL
    patterns = [
        r"/login/?$",
        r"/signin/?$",
        r"/auth/login/?$",
        r"/users/sign_in/?$",
        r"\.aspx\?.*login.*"
    ]
    
    clean_url = url
    for p in patterns:
        clean_url = re.sub(p, "", clean_url, flags=re.IGNORECASE)
    
    # Specific fix for known problematic patterns if regex is too broad
    if "docusketch" in clean_url.lower():
         clean_url = clean_url.split("/login")[0]
         
    return clean_url.rstrip("/")

# ... (Existing funcs) ...

def initialize_browser_profile(client_name: str, urls: List[str], user_scope: str, base_dir: str):
    """
    Initializes the Chrome User Data profile.
    Mocks the interaction in Demo Mode.
    """
    clean_name = sanitize_filename(client_name)
    profile_path = os.path.join(base_dir, clean_name)
    
    print(f"\n--- Initializing Profile: {client_name} ({user_scope}) ---")
    print(f"Profile Path: {profile_path}")

    if not os.path.exists(profile_path):
        os.makedirs(profile_path)

    if IS_WINDOWS:
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--start-maximized")
        
        # Turn off automation flags so Chrome treats this as a normal user session
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Force a standard User-Agent. 
        # Crucial for session persistence: If Selenium uses a "Headless" or "WebDriver" UA,
        # the session cookies might be invalid when you open the shortcut (Native Chrome).
        standard_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        chrome_options.add_argument(f"user-agent={standard_ua}")
        
        driver = None
        try:
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )

            
            if urls:
                driver.get(urls[0])
                for url in urls[1:]:
                    driver.execute_script(f"window.open('{url}', '_blank');")
            else:
                 print("Warning: No URLs found.")

            print(f"\nACTION REQUIRED:")
            print(f"1. Log in to ALL opened tabs for '{client_name}'.")
            input(f"Press [ENTER] when done to save cookies...")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if driver:
                driver.quit()
    else:
        # Mock Browser Interaction
        print(f"[DEMO] Simulating Chrome launch for {len(urls)} URLs...")
        print(f"[DEMO] Creating dummy profile data in {profile_path}...")
        with open(os.path.join(profile_path, "Preferences"), "w") as f:
            f.write("DUMMY CHROME PREFS")
        print("[DEMO] Profile initialized.")

# ==============================================================================
# MAIN LOGIC
# ==============================================================================

def main(limit_clients: int = None):
    print("Starting Client Browser Setup Script...")
    if limit_clients:
        print(f"TEST MODE: Limited to {limit_clients} clients")

    # 1. Fetch Data
    clients_data = fetch_client_data(limit_clients=limit_clients)

    if not clients_data:
        print("No clients found.")
        return

    # Create local output folder for Ana's shortcuts
    if not os.path.exists(SHORTCUT_DIR_ANA):
        os.makedirs(SHORTCUT_DIR_ANA)

    # 2. Iterate and Process
    for client_name, urls in clients_data.items():
        clean_name = sanitize_filename(client_name)
        
        # Clean URLs for the shortcut arguments
        # We want the shortcut to open the dashboard, not the login page
        cleaned_urls = [clean_target_url(u) for u in urls]
        url_args = " ".join([f'"{url}"' for url in cleaned_urls])

        # Generate custom icon for this client
        icon_path = generate_client_icon(client_name)

        # --- Scope: Self ---
        print(f"\n[Processing Scope: Self] - {clean_name}")
        initialize_browser_profile(client_name, urls, "Self", BASE_DIR_SELF)

        self_profile_path = os.path.join(BASE_DIR_SELF, clean_name)
        create_desktop_shortcut(
            name=clean_name,
            target=CHROME_EXE_PATH,
            arguments=f'--user-data-dir="{self_profile_path}" {url_args}',
            folder=get_desktop_path(),
            description=f"Launch {client_name} Systems",
            icon_path=icon_path
        )

        # --- Scope: Ana ---
        print(f"\n[Processing Scope: Ana] - {clean_name}")
        initialize_browser_profile(client_name, urls, "Ana", BASE_DIR_ANA)

        ana_profile_path = os.path.join(BASE_DIR_ANA, clean_name)
        create_desktop_shortcut(
            name=f"Ana - {clean_name}",
            target=CHROME_EXE_PATH,
            arguments=f'--user-data-dir="{ana_profile_path}" {url_args}',
            folder=SHORTCUT_DIR_ANA,
            description=f"Launch {client_name} Systems for Ana",
            icon_path=icon_path
        )
    
    # 3. Handoff Instructions
    print("\n" + "="*80)
    print("PROCESS COMPLETE! HANDOFF INSTRUCTIONS:")
    print("="*80)
    if IS_WINDOWS:
        print(f"1. Locate the Profile Folder: {BASE_DIR_ANA}")
        print(f"2. LOCATE the SHORTCUT Folder: {SHORTCUT_DIR_ANA}")
    else:
        print(f"[DEMO] 1. Locate the Profile Folder: {BASE_DIR_ANA}")
        print(f"[DEMO] 2. LOCATE the SHORTCUT Folder: {SHORTCUT_DIR_ANA}")
    print("3. ZIP both of these folders.")
    print("4. SEND both zip files to Ana.")
    print("5. INSTRUCT Ana to:")
    print(f"   a. Unzip the profiles EXACTLY to: {BASE_DIR_ANA}")
    print("   b. Copy the shortcuts to her Desktop.")
    print("="*80 + "\n")

if __name__ == "__main__":
    import sys
    limit_clients = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit_clients = int(sys.argv[1])
        print(f"Running with client limit: {limit_clients}")
    main(limit_clients=limit_clients)
