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

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be safe for use as a filename."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def generate_client_icon(client_name: str) -> str:
    """
    Generates a custom icon for the client with their name and a colored background.
    Returns the path to the generated icon file.
    """
    if not HAS_PIL:
        print("Warning: PIL not available. Using default Chrome icon.")
        return CHROME_EXE_PATH

    # Ensure icon directory exists
    if not os.path.exists(ICON_DIR):
        os.makedirs(ICON_DIR)

    # Create a unique color based on client name
    hue = hash(client_name) % 360 / 360.0
    saturation = 0.7
    value = 0.9
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    bg_color = tuple(int(c * 255) for c in rgb)

    # Create image
    img = Image.new('RGBA', ICON_SIZE, bg_color + (255,))
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        # Use a larger font size for better visibility
        font_size = 48
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None

    # Get initials from client name
    words = client_name.split()
    if len(words) >= 2:
        initials = words[0][0].upper() + words[1][0].upper()
    else:
        initials = client_name[:2].upper()

    # Calculate text position (centered)
    if font:
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width, text_height = 40, 20

    x = (ICON_SIZE[0] - text_width) // 2
    y = (ICON_SIZE[1] - text_height) // 2

    # Draw white text with black outline
    text_color = (255, 255, 255, 255)
    outline_color = (0, 0, 0, 255)

    # Draw outline
    for dx, dy in [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]:
        draw.text((x + dx, y + dy), initials, fill=outline_color, font=font)

    # Draw main text
    draw.text((x, y), initials, fill=text_color, font=font)

    # Save as ICO file
    icon_path = os.path.join(ICON_DIR, f"{sanitize_filename(client_name)}.ico")
    img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

    print(f"Generated custom icon: {icon_path}")
    return icon_path

def fetch_client_data(limit_clients: int = None) -> Dict[str, List[str]]:
    """
    Fetches client systems from BigQuery.
    Mocks data if in Demo Mode and BQ lib is missing.
    limit_clients: If specified, limit to this many clients for testing
    """
    if DEMO_MODE and not HAS_BIGQUERY:
        print("Warning: 'google-cloud-bigquery' not found. Using MOCK data for demo.")
        mock_data = {
            "State Farm": ["https://login.statefarm.com", "https://claims.statefarm.com"],
            "Allstate": ["https://agent.allstate.com"],
            "Farmers": ["https://portal.farmers.com", "https://billing.farmers.com"]
        }
        if limit_clients:
            # Take first N clients for testing
            client_names = list(mock_data.keys())[:limit_clients]
            return {name: mock_data[name] for name in client_names}
        return mock_data

    print("Fetching data from BigQuery...")
    try:
        client = bigquery.Client(project=BQ_PROJECT_ID)
        query_job = client.query(BQ_QUERY)
        results = query_job.result()

        data = defaultdict(list)
        for row in results:
            if row.login_url:
                data[row.client_name].append(row.login_url)

        print(f"Successfully fetched systems for {len(data)} clients.")

        # Limit clients if specified (for testing)
        if limit_clients and len(data) > limit_clients:
            client_names = list(data.keys())[:limit_clients]
            limited_data = {name: data[name] for name in client_names}
            print(f"Limited to {limit_clients} clients for testing: {list(limited_data.keys())}")
            return limited_data

        return data
    except Exception as e:
        if DEMO_MODE:
            print(f"BQ Fetch Failed ({e}). Switching to MOCK data for demo.")
            mock_data = {
                "State Farm": ["https://login.statefarm.com"],
                "Allstate": ["https://agent.allstate.com"]
            }
            if limit_clients:
                client_names = list(mock_data.keys())[:limit_clients]
                return {name: mock_data[name] for name in client_names}
            return mock_data
        else:
            print(f"Error fetching data from BigQuery: {e}")
            sys.exit(1)

def create_desktop_shortcut(name: str, target: str, arguments: str, folder: str, description: str = "", icon_path: str = ""):
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
            # Use custom icon if provided, otherwise use Chrome icon
            shortcut.IconLocation = icon_path if icon_path else target
            shortcut.save()
            print(f"Shortcut created: {path}")
        except Exception as e:
            print(f"Failed to create shortcut '{name}': {e}")
    else:
        # Mock Shortcut (Text File)
        path = os.path.join(folder, f"{name}.fake_lnk")
        with open(path, "w") as f:
            f.write(f"TARGET: {target}\nARGS: {arguments}\nDESC: {description}\nICON: {icon_path}")
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
        url_args = " ".join([f'"{url}"' for url in urls])

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
