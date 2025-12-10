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
        c.client_name,
        l.login_url
    FROM
        `xano-fivetran-bq.staging_xano.ptl_client` c
    JOIN
        `xano-fivetran-bq.staging_xano.ptl_system_access_logins` l
    ON
        c.id = l.client_id
    WHERE
        c.subscription_id = 14
        AND l.login_url IS NOT NULL
"""

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be safe for use as a filename."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def fetch_client_data() -> Dict[str, List[str]]:
    """
    Fetches client systems from BigQuery.
    Mocks data if in Demo Mode and BQ lib is missing.
    """
    if DEMO_MODE and not HAS_BIGQUERY:
        print("Warning: 'google-cloud-bigquery' not found. Using MOCK data for demo.")
        return {
            "State Farm": ["https://login.statefarm.com", "https://claims.statefarm.com"],
            "Allstate": ["https://agent.allstate.com"],
            "Farmers": ["https://portal.farmers.com", "https://billing.farmers.com"]
        }

    print("Fetching data from BigQuery...")
    try:
        client = bigquery.Client()
        query_job = client.query(BQ_QUERY)
        results = query_job.result()
        
        data = defaultdict(list)
        for row in results:
            if row.login_url:
                data[row.client_name].append(row.login_url)
                
        print(f"Successfully fetched systems for {len(data)} clients.")
        return data
    except Exception as e:
        if DEMO_MODE:
            print(f"BQ Fetch Failed ({e}). Switching to MOCK data for demo.")
            return {
                "State Farm": ["https://login.statefarm.com"],
                "Allstate": ["https://agent.allstate.com"]
            }
        else:
            print(f"Error fetching data from BigQuery: {e}")
            sys.exit(1)

def create_desktop_shortcut(name: str, target: str, arguments: str, folder: str, description: str = ""):
    """Creates a Windows shortcut (.lnk) or a mock file in Demo Mode."""
    if not os.path.exists(folder):
        os.makedirs(folder)

    if IS_WINDOWS:
        try:
            path = os.path.join(folder, f"{name}.lnk")
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.TargetPath = target
            shortcut.Arguments = arguments
            shortcut.Description = description
            shortcut.IconLocation = target
            shortcut.save()
            print(f"Shortcut created: {path}")
        except Exception as e:
            print(f"Failed to create shortcut '{name}': {e}")
    else:
        # Mock Shortcut (Text File)
        path = os.path.join(folder, f"{name}.fake_lnk")
        with open(path, "w") as f:
            f.write(f"TARGET: {target}\nARGS: {arguments}\nDESC: {description}")
        print(f"[DEMO] Created mock shortcut: {path}")

def get_desktop_path() -> str:
    """Returns the path to the current user's Desktop or a Demo Dist folder."""
    if IS_WINDOWS:
        try:
            return winshell.desktop()
        except:
            return os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        d = os.path.abspath("./dist/Desktop")
        if not os.path.exists(d):
            os.makedirs(d)
        return d

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

def main():
    print("Starting Client Browser Setup Script...")
    
    # 1. Fetch Data
    clients_data = fetch_client_data()
    
    if not clients_data:
        print("No clients found.")
        return

    # Create local output folder for Ana's shortcuts
    if not os.path.exists(SHORTCUT_DIR_ANA):
        os.makedirs(SHORTCUT_DIR_ANA)

    # 2. Iterate and Process
    for client_name, urls in clients_data.items():
        clean_name = sanitize_filename(client_name)
        url_args = " ".join([f'"{url}"' for url in urls])
        
        # --- Scope: Self ---
        print(f"\n[Processing Scope: Self] - {clean_name}")
        initialize_browser_profile(client_name, urls, "Self", BASE_DIR_SELF)
        
        self_profile_path = os.path.join(BASE_DIR_SELF, clean_name)
        create_desktop_shortcut(
            name=clean_name,
            target=CHROME_EXE_PATH,
            arguments=f'--user-data-dir="{self_profile_path}" {url_args}',
            folder=get_desktop_path(),
            description=f"Launch {client_name} Systems"
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
            description=f"Launch {client_name} Systems for Ana"
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
    main()
