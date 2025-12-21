import os
import sys
import re
from typing import List, Dict
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
    BASE_DIR_PROFILES = r"C:\Automation\Profiles"
    BASE_DIR_SELF = BASE_DIR_PROFILES # Legacy/Universal
    BASE_DIR_ANA = BASE_DIR_PROFILES  # Legacy/Universal
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    SHORTCUT_DIR_TEAM = os.path.join(SCRIPT_DIR, "For_Team_Desktop")
    SHORTCUT_DIR_ANA = SHORTCUT_DIR_TEAM
    
    CHROME_EXE_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ICON_DIR = r"C:\Automation\Icons"
    DASHBOARD_DIR = r"C:\Automation\Dashboards"
else:
    # Demo Linux Paths (Current Directory)
    BASE_DIR_SELF = os.path.abspath("./dist/Automation/My_Profiles")
    BASE_DIR_ANA = os.path.abspath("./dist/Automation/Ana_Profiles")
    SHORTCUT_DIR_ANA = os.path.abspath("./dist/For_Ana_Desktop")
    CHROME_EXE_PATH = "/usr/bin/google-chrome" # Mock
    ICON_DIR = os.path.abspath("./dist/Automation/Icons")
    DASHBOARD_DIR = os.path.abspath("./dist/Automation/Dashboards")
    print(f"DEMO PATHS:\n  Self Profiles: {BASE_DIR_SELF}\n  Ana Profiles: {BASE_DIR_ANA}\n")

# BigQuery Settings
BQ_PROJECT_ID = "xano-fivetran-bq"
BQ_QUERY = """
    SELECT
        c.full_name as client_name,
        COALESCE(NULLIF(l.custom_link, ''), sa.link) as login_url,
        sa.name as system_name,
        c.key_and_pro_account as is_key_account,
        c.subscription_id,
        s.subscription_name,
        l.api_key
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
    LEFT JOIN
        `xano-fivetran-bq.staging_xano.ptl_subscription` s
    ON
        c.subscription_id = s.id
    WHERE
        c.suspended = false
        AND c._fivetran_deleted = false
        AND l._fivetran_deleted = false
        AND sa._fivetran_deleted = false
        AND c.subscription_id IN (2, 3, 4, 5, 8, 9, 12, 13, 14, 15, 16) -- Updated validation list
        AND sa.link IS NOT NULL
        AND sa.link != ''
        # AND (sa.client_id IS NULL OR sa.client_id = '')  -- Exclude API-connected systems (commented out to rely on api_key check)
"""

# Icon Settings
ICON_SIZE = (256, 256)
# ICON_DIR is now defined above with paths

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be safe for use as a filename."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def create_client_dashboard(clean_name: str, client_name: str, urls: List[str]) -> str:
    """
    Creates a local HTML dashboard file for the client.
    Returns the absolute path to the file.
    """
    # Dashboard directory - fixed path for portability
    dash_dir = DASHBOARD_DIR
    if not os.path.exists(dash_dir):
        os.makedirs(dash_dir)
        
    filename = os.path.join(dash_dir, f"{clean_name}.html")
    
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{client_name} - WeScope</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 40px; }}
            .container {{ max_width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: #2ecc71; margin-top: 0; font-size: 32px; border-bottom: 2px solid #f0f0f0; padding-bottom: 20px; }}
            .system-list {{ list-style: none; padding: 0; margin-top: 30px; }}
            .system-item {{ margin-bottom: 15px; }}
            .system-link {{ display: block; padding: 15px 20px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; text-decoration: none; color: #333; font-weight: 500; transition: all 0.2s; }}
            .system-link:hover {{ background: #e8f5e9; border-color: #2ecc71; color: #2ecc71; transform: translateX(5px); }}
            .footer {{ margin-top: 40px; color: #888; font-size: 14px; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{client_name}</h1>
            <p>WeScope Client Workspace</p>
            
            <ul class="system-list">
    """
    
    for url in urls:
        # Extract domain for display
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            name = domain.split('.')[0].title()
            # specific naming overrides
            if 'restore365' in url: name = "RESTORE365"
            if 'xactanalysis' in url: name = "XactAnalysis"
            if 'xactimate' in url: name = "Xactimate"
            if 'contentstrack' in url: name = "ContentsTrack"
            if 'symbility' in url: name = "Symbility"
            if 'dash-ngs' in url: name = "DASH"
        except:
            name = url
            
        html += f'<li class="system-item"><a href="{url}" target="_blank" class="system-link">{name}<br><span style="font-size:12px;color:#999">{url}</span></a></li>'
        
    html += """
            </ul>
            <div class="footer">
                <p>This tab identifies your active client session.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
        
    return filename

def get_category_metadata(subscription_id: int, is_key_account: bool):
    """
    Returns (category_name, color_tuple, text_label) based on priority rules.
    """
    # Priority 1: PRO (Sub 14)
    if subscription_id == 14:
        return "PRO", (46, 204, 113), "PRO" # Green
    
    # Priority 2: KEY
    if is_key_account:
        return "KEY", (41, 128, 185), "KEY" # Blue
    
    # Priority 3: NEW (Sub 12, 13)
    if subscription_id in [12, 13]:
        return "NEW", (127, 140, 141), "NEW" # Dark Grey
    
    # Priority 4: LEGACY (Sub 2,3,4,5,8,9)
    if subscription_id in [2, 3, 4, 5, 8, 9]:
        return "LEGACY", (189, 195, 199), "LEG" # Light Grey
    
    # Fallback (shouldn't happen with strict query)
    return "UNKNOWN", (149, 165, 166), "?"

def generate_labeled_icon(subscription_id: int, is_key_account: bool) -> str:
    """
    Generates an icon with the appropriate background color and text label.
    """
    if not HAS_PIL:
        print("Warning: PIL not available. Using default Chrome icon.")
        return CHROME_EXE_PATH

    # Ensure icon directory exists
    if not os.path.exists(ICON_DIR):
        os.makedirs(ICON_DIR)

    category, color_hex, label_text = get_category_metadata(subscription_id, is_key_account)
    filename = f"WeScope_{category}.ico"
    icon_path = os.path.join(ICON_DIR, filename)
    
    # Create if doesn't exist
    if not os.path.exists(icon_path):
        print(f"Creating {category} icon ({label_text})...")
        
        # Create base image
        img = Image.new('RGB', ICON_SIZE, color_hex)
        draw = ImageDraw.Draw(img)
        
        # Add text
        try:
            # Try to load a nice font, or fallback to default
            font_size = 100
            try:
                # Arial is commonly available
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                # Linux/Other might not have arial, try generic sans
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()
        except:
             font = ImageFont.load_default()

        # Center text (approximate if using default font)
        # Using simple centering logic
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (ICON_SIZE[0] - text_width) // 2
        y = (ICON_SIZE[1] - text_height) // 2
        
        # Draw text in White
        draw.text((x, y), label_text, fill=(255, 255, 255), font=font)

        img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"  Created: {icon_path}")
    
    return icon_path

def categorize_system(url: str) -> int:
    """
    Categorizes systems by type for tab ordering.
    Returns a priority number (lower = opens first/left-most tab).
    
    Priority Order:
    1. CRM Systems (dash, restore365, fusion, solitaire, psa, etc.)
    2. Documentation Apps (matterport, encircle, companycam)
    3. Estimating Systems (xactanalysis, xactimate, contents, symbility)
    4. MICA
    5. Others
    """
    url_lower = url.lower()
    
    # Priority 1: CRM Systems
    crm_keywords = ['dash', 'restore365', 'fusion', 'solitaire', 'psa', 'restoration-manager', 
                    'restorationmanager', 'buildertrend', 'jobnimbus']
    if any(keyword in url_lower for keyword in crm_keywords):
        return 1
    
    # Priority 2: Documentation Apps
    doc_keywords = ['matterport', 'encircle', 'companycam', 'docusketch', 'magicplan']
    if any(keyword in url_lower for keyword in doc_keywords):
        return 2
    
    # Priority 3: Estimating Systems
    estimating_keywords = ['xactanalysis', 'xactimate', 'contentstrack', 'contents', 'symbility']
    if any(keyword in url_lower for keyword in estimating_keywords):
        # Sub-ordering within estimating: XactAnalysis, Xactimate, ContentsTrack, Symbility
        if 'xactanalysis' in url_lower:
            return 30
        elif 'xactimate' in url_lower:
            return 31
        elif 'contentstrack' in url_lower or 'contents' in url_lower:
            return 32
        elif 'symbility' in url_lower:
            return 33
        else:
            return 3
    
    # Priority 4: MICA
    if 'mica' in url_lower:
        return 4
    
    # Priority 5: Everything else
    return 5

def clean_target_url(url: str, system_name: str = "") -> str:
    """
    Removes specific login paths from the URL so the browser lands on the dashboard
    if the session is already active. Also applies known URL fixes/overrides.
    """
    # =========================================================================
    # SYSTEM-BASED OVERRIDES (Highest Priority - Check Name First)
    # =========================================================================
    
    # Xactimate (Online) - Force optimized App URL
    # Catches generic "identity.verisk.com" links if the system is Xactimate
    if "Xactimate" in system_name:
        print(f"  [URL Replacement] Xactimate (System Name Match): -> xactimate.com/xor/app/")
        return "https://xactimate.com/xor/app/"

    # XactAnalysis - Force optimized Start URL
    if "XactAnalysis" in system_name:
        print(f"  [URL Replacement] XactAnalysis (System Name Match): -> start.jsp")
        return "https://www.xactanalysis.com/apps/cxa/start.jsp"
    if "micaexchange.com" in url.lower():
        # Keep custom MICA URLs (they usually have specific paths like /pdr/ or /rainbow/)
        # But ensure they are clean
        pass
    
    URL_OVERRIDES = {
        # Docusketch: portal_2 doesn't exist, should be portal
        "app.docusketch.com/portal_2": "app.docusketch.com/portal",
    }
    
    # =========================================================================
    # FULL URL REPLACEMENTS - Replace entire URL with a better destination
    # These take priority and return immediately
    # =========================================================================
    
    # Xactimate/XactAnalysis - Verisk login URLs should go directly to the app
    if "identity.verisk.com" in url.lower():
        if "xactimate" in url.lower() or "xor.xactimate" in url.lower():
            # Use the app root, which handles SSO redirection better than deep links
            print(f"  [URL Replacement] Xactimate: -> xactimate.com/xor/app/")
            return "https://xactimate.com/xor/app/"
        elif "xactanalysis" in url.lower():
            # User confirmed this specific URL handles re-launching best
            print(f"  [URL Replacement] XactAnalysis: -> start.jsp")
            return "https://www.xactanalysis.com/apps/cxa/start.jsp"
        else:
            # Generic Verisk - just go to settings (or the base)
            print(f"  [URL Replacement] Verisk: stripping login params")
            return "https://identity.verisk.com"
    
    # Symbility/Claims Workspace - go directly to claims page, not login
    # NOTE: Symbility expires sessions on browser close (like MICA)
    if "symbility.net" in url.lower() and "symbility.net/ux/site/#/login" not in url.lower():
        # Only override if it's NOT already a specific login URL (some custom links might be specific)
        # But generally we want #/claims
        print(f"  [URL Replacement] Symbility: -> #/claims")
        return "https://www.symbility.net/ux/site/#/claims"
    
    # PSA (Canam Systems) - Fix error page to login page
    if "psarcweb.com" in url.lower():
        # User reported Error page: https://psarcweb.com/PSAWeb/Error?aspxerrorpath=/PSAWeb/Account
        # Correct Login page: https://psarcweb.com/PSAWeb/Account/Login
        print(f"  [URL Replacement] PSA: -> Account/Login")
        return "https://psarcweb.com/PSAWeb/Account/Login"

    # RESTORE365 - go to the post-login page, not the login page
    # The /User/ path shows "Hello World" which is broken
    # RESTORE365 - go to the post-login page
    if "restore365.net" in url.lower():
        print(f"  [URL Replacement] RESTORE365: -> uPostLogin.aspx")
        return "https://restore365.net/Enterprise/Module/User/uPostLogin.aspx"
        
    # DASH (NextGear) - Fix "Hello World" on /User/ path
    if "dash-ngs.net" in url.lower():
         print(f"  [URL Replacement] DASH: -> uPostLogin.aspx")
         return "https://www.dash-ngs.net/NextGear/Enterprise/Module/User/uPostLogin.aspx"
         
    # RMS (NextGear)
    if "rms-ngs.net" in url.lower():
         print(f"  [URL Replacement] RMS: -> uPostLogin.aspx")
         return "https://rms-ngs.net/RMS/Module/User/uPostLogin.aspx"

    # Fusion (NextGear)
    if "fusion-ngs.net" in url.lower():
         print(f"  [URL Replacement] Fusion: -> uPostLogin.aspx")
         return "https://fusion-ngs.net/Enterprise/Module/User/uPostLogin.aspx"

    # Solitaire (NextGear)
    if "solitaire-ngs.net" in url.lower():
         print(f"  [URL Replacement] Solitaire: -> uPostLogin.aspx")
         return "https://solitaire-ngs.net/DKI/Module/User/uPostLogin.aspx"

    # Westhill Global - Fix incorrect "app.westhillglobal.com" to "login.westhillglobal.com"
    if "app.westhillglobal.com" in url.lower():
        print(f"  [URL Replacement] Westhill: app. -> login.")
        return url.lower().replace("app.westhillglobal.com", "login.westhillglobal.com")
    
    # Apply URL overrides first
    clean_url = url
    for bad_pattern, good_pattern in URL_OVERRIDES.items():
        if bad_pattern in clean_url:
            clean_url = clean_url.replace(bad_pattern, good_pattern)
            print(f"  [URL Override] {bad_pattern} -> {good_pattern}")
    
    # Patterns to strip from the END of the URL
    patterns = [
        r"/login(\?.*)?$",
        r"/sign-in(\?.*)?$",
        r"/signin(\?.*)?$",
        r"/auth/login(\?.*)?$",
        r"/users/sign_in(\?.*)?$",
        r"/Login\.aspx(\?.*)?$",
        r"/logon\.event(\?.*)?$",
        r"/Logon\.event(\?.*)?$",
    ]
    
    for p in patterns:
        clean_url = re.sub(p, "", clean_url, flags=re.IGNORECASE)
    
    # Strip query parameters for cleaner URLs (sessions don't need them)
    if "?" in clean_url:
        clean_url = clean_url.split("?")[0]
    
    # Strip hash fragments that are login-related
    if "#/login" in clean_url.lower():
        clean_url = clean_url.split("#")[0]
         
    return clean_url.rstrip("/")


def fetch_client_data(limit_clients: int = None) -> Dict[str, Dict]:
    """
    Fetches client systems from BigQuery.
    Returns: { "Client Name": { "urls": [...], "is_key_account": bool } }
    """
    if DEMO_MODE and not HAS_BIGQUERY:
        print("Warning: 'google-cloud-bigquery' not found. Using MOCK data for demo.")
        mock_data = {
            "State Farm": {"systems": [{"url": "https://login.statefarm.com", "name": "State Farm"}, {"url": "https://claims.statefarm.com/login", "name": "Claims"}], "is_key_account": True},
            "Allstate": {"systems": [{"url": "https://agent.allstate.com/signin", "name": "Allstate"}], "is_key_account": False},
        }
        if limit_clients:
            client_names = list(mock_data.keys())[:limit_clients]
            return {name: mock_data[name] for name in client_names}
        return mock_data

    print("Fetching data from BigQuery...")
    try:
        client = bigquery.Client(project=BQ_PROJECT_ID)
        query_job = client.query(BQ_QUERY)
        results = query_job.result()

        data = defaultdict(lambda: {"systems": [], "is_key_account": False, "subscription_id": None, "subscription_name": "Unknown"})
        for row in results:
            # Exclude if API Key is present, UNLESS it is Symbility
            if row.api_key:
                is_symbility = "symbility" in str(row.login_url).lower()
                if not is_symbility:
                    continue

            if row.login_url:
                data[row.client_name]["systems"].append({"url": row.login_url, "name": row.system_name})
                # If 'true' string or boolean True in BQ, handle appropriately
                # keys in BQ are often strings 'true' or 'false'
                is_key = str(row.is_key_account).lower() == 'true'
                data[row.client_name]["is_key_account"] = is_key
                data[row.client_name]["subscription_id"] = row.subscription_id
                data[row.client_name]["subscription_name"] = row.subscription_name

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
                "State Farm": {"systems": [{"url": "https://login.statefarm.com", "name": "State Farm"}], "is_key_account": True},
            }
            if limit_clients:
                client_names = list(mock_data.keys())[:limit_clients]
                return {name: mock_data[name] for name in client_names}
            return mock_data
        else:
            print(f"Error fetching data from BigQuery: {e}")
            # Do not exit, try to continue or raise
            raise e



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

# ... (Existing funcs) ...


def create_subset_zip(base_path, subfolders, output_zip_path):
    """
    Creates a zip file containing only specific subfolders from base_path.
    Structure in zip: /Automation/[subfolder]
    """
    import shutil
    import tempfile
    
    print(f"[-] Creating filtered zip: {os.path.basename(output_zip_path)}")
    try:
        # Create temp dir for staging
        with tempfile.TemporaryDirectory() as temp_dir:
            # We want the zip to contain a root folder "Automation"
            staging_root = os.path.join(temp_dir, "Automation")
            os.makedirs(staging_root)
            
            for sub in subfolders:
                src = os.path.join(base_path, sub)
                dst = os.path.join(staging_root, sub)
                if os.path.exists(src):
                    # copytree needs destination to NOT exist
                    shutil.copytree(src, dst)
                    print(f"    Including: {sub}")
                else:
                    print(f"    [WARNING] Missing: {sub}")
            
            # Zip the staging dir (contains "Automation" folder)
            shutil.make_archive(output_zip_path.replace('.zip', ''), 'zip', temp_dir)
            print(f"[OK] Created {os.path.basename(output_zip_path)}")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to create zip: {e}")
        return False

# ==============================================================================
# MAIN LOGIC
# ==============================================================================

def generate_subscription_reference(clients_data: Dict):
    """Generates a markdown reference for Subscription IDs (Queries BQ for full list)."""
    if not HAS_BIGQUERY: return

    print("Generating Subscription Reference (Fetching full list)...")
    try:
        client = bigquery.Client(project=BQ_PROJECT_ID)
        query = "SELECT id, subscription_name FROM `xano-fivetran-bq.staging_xano.ptl_subscription` ORDER BY id"
        results = client.query(query).result()
        
        lines = ["# Subscription ID Reference\n", 
                 "| ID | Name | Default Category | Notes |", 
                 "|---|---|---|---|"]
        
        for row in results:
            sid = row.id
            sname = row.subscription_name
            # Provide default category (assuming Not Key Account)
            cat, _, _ = get_category_metadata(sid, False)
            
            note = ""
            if sid == 14: 
                note = "Pro Tier (Always PRO)"
            elif sid in [12, 13]:
                note = "New Structure (Essential/Plus)"
            elif sid in [2,3,4,5,8,9]:
                note = "Legacy Tiers"
                
            lines.append(f"| {sid} | {sname} | {cat} | {note} |")
            
        # Add Key Account Note
        lines.append("\n## Logic Mapping")
        lines.append("1. **PRO (Green)**: Subscription ID = 14")
        lines.append("2. **KEY (Blue)**: If Client is 'Key Account' (Verified) AND not PRO.")
        lines.append("3. **NEW (Dark Grey)**: Subscription ID = 12 or 13")
        lines.append("4. **LEG (Light Grey)**: All other legacy IDs (2-9)")
        
        with open("subscription_reference.md", "w") as f:
            f.write("\n".join(lines))
        print(f"[INFO] Created subscription_reference.md")
        
    except Exception as e:
        print(f"[WARNING] Failed to generate reference: {e}")

def main(limit_clients: int = None):
    print("Starting Client Browser Setup Script...")
# ... (standard main logic up to packaging) ...
# I will use replace_file_content carefully to preserve the middle of main
# Wait, I cannot use replace_file_content to insert helper AND update main if they are far apart in one chunk.
# I will insert helper first right before main.

# Wait, replace_file_content does supports standard edit.
# I will insert the helper function before main() definition.

    if limit_clients:
        print(f"TEST MODE: Limited to {limit_clients} clients")

    # 1. Fetch Data
    clients_data = fetch_client_data(limit_clients=limit_clients)
    generate_subscription_reference(clients_data)

    if not clients_data:
        print("No clients found.")
        return

    # Ensure fresh build by cleaning old dashboards
    import shutil
    if os.path.exists(DASHBOARD_DIR):
        print("Cleaning old dashboards...")
        try:
            shutil.rmtree(DASHBOARD_DIR)
        except Exception as e:
            print(f"[WARNING] Could not clean dashboards: {e}")
    if not os.path.exists(DASHBOARD_DIR):
        os.makedirs(DASHBOARD_DIR)

    # Create local output folder for Ana's shortcuts
    if not os.path.exists(SHORTCUT_DIR_ANA):
        os.makedirs(SHORTCUT_DIR_ANA)

    # 2. Iterate and Process
    for client_name, data in clients_data.items():
        systems = data["systems"]
        is_key_account = data["is_key_account"]
        subscription_id = data.get("subscription_id")
        
        clean_name = sanitize_filename(client_name)
        
        # Generate Colored Icon
        icon_path = generate_labeled_icon(subscription_id, is_key_account)
        
        # Clean URLs for the shortcut arguments
        # We want the shortcut to open the dashboard, not the login page
        cleaned_urls = []
        seen_urls = set()
        for sys_obj in systems:
            raw_url = sys_obj["url"]
            sys_name = sys_obj["name"]
            cleaned_url = clean_target_url(raw_url, sys_name)
            
            # Deduplication: Prevent multiple tabs for the exact same URL
            if cleaned_url not in seen_urls:
                cleaned_urls.append(cleaned_url)
                seen_urls.add(cleaned_url)
        
        # Sort URLs by category (CRM first, then docs, then estimating, etc.)
        cleaned_urls_sorted = sorted(cleaned_urls, key=lambda url: categorize_system(url))
        
        # EXCLUSIONS: Remove API-integrated systems even if they have credentials
        # These systems are typically accessed via API and don't need browser tabs
        # (Legacy keyword check - now mostly handled by BQ API Key check)
        excluded_keywords = ['jobnimbus']
        final_urls = []
        for url in cleaned_urls_sorted:
            is_excluded = False
            for keyword in excluded_keywords:
                if keyword in url.lower():
                    print(f"  [Excluding] {keyword} system: {url}")
                    is_excluded = True
                    break
            if not is_excluded:
                final_urls.append(url)
        
        # Create a local Dashboard HTML file for this client
        dashboard_path = create_client_dashboard(clean_name, client_name, final_urls)
        
        # Add dashboard as the FIRST tab
        # Note: We use file:/// URI for the dashboard
        dashboard_url = f"file:///{dashboard_path.replace(os.sep, '/')}"
        
        # Combine all URLs (Dashboard + Systems + WeScope)
        all_urls = [dashboard_url] + final_urls + ["https://portal.wescope.com/"]
        url_args = " ".join([f'"{url}"' for url in all_urls])

        # --- Scope: Team (Unified) ---
        # Determine Sort Prefix (1=PRO, 2=KEY, 3=NEW, 4=LEG)
        cat_sort, _, _ = get_category_metadata(subscription_id, is_key_account)
        prefix = "9"
        if cat_sort == "PRO": prefix = "1"
        elif cat_sort == "KEY": prefix = "2"
        elif cat_sort == "NEW": prefix = "3"
        elif cat_sort == "LEGACY": prefix = "4"
        
        shortcut_label = f"{prefix} - {clean_name}"
        print(f"\n[Creating Shortcut] {shortcut_label} (Team)")

        # Profile Path: Must use ORIGINAL clean_name to preserve data migration
        profile_path = os.path.join(BASE_DIR_PROFILES, clean_name)
        if not os.path.exists(profile_path):
             os.makedirs(profile_path)
             
        # Add Extensions if they exist
        extensions_path = r"C:\Automation\Extensions"
        load_extensions = []
        if os.path.exists(extensions_path):
            # Check for specific extensions
            ext_list = ["Loom", "Xactware_ClickOnce"]
            for ext in ext_list:
                ep = os.path.join(extensions_path, ext)
                if os.path.exists(ep):
                    load_extensions.append(ep)
        
        ext_args = ""
        if load_extensions:
            ext_str = ",".join(load_extensions)
            ext_args = f'--load-extension="{ext_str}"'

        chrome_args = f'--user-data-dir="{profile_path}" --profile-directory="Default" {ext_args} {url_args}'
        
        if not os.path.exists(SHORTCUT_DIR_TEAM):
            os.makedirs(SHORTCUT_DIR_TEAM)

        create_desktop_shortcut(
            name=shortcut_label,
            target=CHROME_EXE_PATH,
            arguments=chrome_args,
            folder=SHORTCUT_DIR_TEAM,
            description=f"Launch {client_name}",
            icon_path=icon_path
        )
    
    # 3. Packaging for Team (Unified)
    print("\n" + "="*80)
    print("PACKAGING FOR TEAM (UNIVERSAL)...")
    print("="*80)
    
    # Destination folder (inside script directory)
    dist_dir = os.path.join(SCRIPT_DIR, "WeScope_Browser_Installer")
    resources_dir = os.path.join(dist_dir, "resources")
    
            # Clean output directories to ensure no deprecated files persist
    if os.path.exists(dist_dir):
        try:
            # We don't want to delete the directory itself if it's open, but we should clean files
            # Actually, simpler to just delete deprecated files explicitly from LOCAL dist_dir
            deprecated_local = ["WESCOPE_SECURITY_WIPE.bat"]
            for d in deprecated_local:
                dp = os.path.join(dist_dir, d)
                if os.path.exists(dp): os.remove(dp)
            
            # Clean resources
            if os.path.exists(resources_dir):
                 deprecated_res_local = ["WESCOPE_SECURITY_WIPE.bat"]
                 for d in deprecated_res_local:
                    dp = os.path.join(resources_dir, d)
                    if os.path.exists(dp): os.remove(dp)
        except: pass

    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    # Files to copy to ROOT
    files_to_copy_root = {
        "SETUP_TEAM.bat": os.path.join(os.path.dirname(__file__), "SETUP_TEAM.bat"),
        "TEAM_SETUP_GUIDE.md": os.path.join(os.path.dirname(__file__), "TEAM_SETUP_GUIDE.md")
    }

    # Files to copy to RESOURCES (Hidden stuff)
    files_to_copy_resources = {
        "CLEANUP_POLICIES.bat": os.path.join(os.path.dirname(__file__), "CLEANUP_POLICIES.bat"),
        # REMOVED: WESCOPE_SECURITY_WIPE.bat (Admin only, not for distribution)
    }

    import shutil
    # Copy Root Files
    for filename, src_path in files_to_copy_root.items():
        try:
            if os.path.exists(src_path):
                # Force delete destination first to ensure update and timestamp refresh
                dest_path = os.path.join(dist_dir, filename)
                if os.path.exists(dest_path):
                    try:
                        os.remove(dest_path)
                    except: pass
                
                shutil.copy2(src_path, dist_dir)
                print(f"[OK] Copied {filename} to {dist_dir}")
            else:
                print(f"[WARNING] File not found: {filename}")
        except Exception as e:
            print(f"[ERROR] Copy failed for {filename}: {e}")

    # Copy Resource Files
    for filename, src_path in files_to_copy_resources.items():
        try:
            if os.path.exists(src_path):
                shutil.copy2(src_path, resources_dir)
                print(f"[OK] Copied {filename} to {resources_dir}")
            else:
                print(f"[WARNING] File not found: {filename}")
        except Exception as e:
            print(f"[ERROR] Copy failed for {filename}: {e}")

    # 2. Zip Shortcuts -> resources/Shortcuts.zip
    print("[-] Zipping Shortcuts...")
    try:
        shutil.make_archive(
            os.path.join(resources_dir, "Shortcuts"), 
            'zip', 
            SHORTCUT_DIR_TEAM
        )
        print(f"[OK] Created resources/Shortcuts.zip")
    except Exception as e:
        print(f"[ERROR] Zipping shortcuts failed: {e}")

    # 3. Create Clean Automation.zip -> resources/Automation.zip
    print("[-] Creating Clean Automation.zip (Icons, Dashboards Only)...")
    if IS_WINDOWS:
        automation_src = r"C:\Automation"
    else:
        automation_src = os.path.join(os.getcwd(), "dist", "Automation")
    
    # Selective Zip (Exclude Profiles to protect data)
    # Include Extensions if they exist
    folders_to_zip = ['Icons', 'Dashboards']
    if os.path.exists(os.path.join(automation_src, 'Extensions')):
        folders_to_zip.append('Extensions')

    create_subset_zip(
        automation_src, 
        folders_to_zip, 
        os.path.join(resources_dir, "Automation.zip")
    )

    # 4. Generate version file -> resources/version.txt
    from datetime import datetime
    version_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    version_file = os.path.join(resources_dir, "version.txt")
    try:
        with open(version_file, 'w') as f:
            f.write(version_timestamp)
        print(f"[OK] Generated version file: {version_timestamp}")
    except Exception as e:
        print(f"[WARNING] Failed to create version file: {e}")
    
    # --- AUTO-PUBLISH TO GOOGLE DRIVE (OPTIONAL) ---
    # Update this path to your G-Drive shared folder
    PUBLISH_PATH = r"G:\Shared drives\Client Shortcuts\WeScope_Browser_Installer"
    if os.path.exists(os.path.dirname(PUBLISH_PATH)):
        print(f"\nPublishing to Google Drive: {PUBLISH_PATH}...")
        try:
            if not os.path.exists(PUBLISH_PATH):
                os.makedirs(PUBLISH_PATH)
            
            # Clean old files in PUBLISH_PATH to remove deprecated junk
            # BE CAREFUL: Only delete if we are sure it's the right folder
            # For safety, we will just overwrite/add, but maybe we should delete deprecated files explicitly
            deprecated = ["Automation.zip", "Shortcuts.zip", "version.txt", "CLEANUP_POLICIES.bat", "WESCOPE_SECURITY_WIPE.bat"]
            for d_file in deprecated:
                d_path = os.path.join(PUBLISH_PATH, d_file)
                if os.path.exists(d_path):
                    try:
                        os.remove(d_path)
                        print(f"  [Clean] Removed old file: {d_file}")
                    except: pass
            
            # Also clean deprecated files from RESOURCES if they shouldn't be there
            deprecated_res = ["WESCOPE_SECURITY_WIPE.bat"]
            pub_res = os.path.join(PUBLISH_PATH, "resources")
            for d_file in deprecated_res:
                d_path = os.path.join(pub_res, d_file)
                if os.path.exists(d_path):
                    try:
                        os.remove(d_path)
                        print(f"  [Clean] Removed old resource: {d_file}")
                    except: pass

            # Copy ROOT files
            for item in os.listdir(dist_dir):
                s = os.path.join(dist_dir, item)
                d = os.path.join(PUBLISH_PATH, item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)
            
            # Copy RESOURCES folder
            pub_res = os.path.join(PUBLISH_PATH, "resources")
            if not os.path.exists(pub_res):
                os.makedirs(pub_res)
            
            for item in os.listdir(resources_dir):
                s = os.path.join(resources_dir, item)
                d = os.path.join(pub_res, item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)

            print("[OK] Published successfully to Google Drive.")
        except Exception as e:
            print(f"[WARNING] Auto-publish failed: {e}")
            print("You can still copy the files manually.")
    # -----------------------------------------------

    # 5. Final Instructions
    print("\n" + "="*80)
    print("PROCESS COMPLETE! READY TO DEPLOY")
    print("="*80)
    print(f"UNIVERSAL DISTRIBUTION CREATED:")
    print(f"  --> {dist_dir}")
    print(f"\nContains: Automation.zip + Shortcuts.zip + SETUP_TEAM.bat + version.txt (v{version_timestamp})")
    print("="*80 + "\n")

    # 6. Cleanup Staging Folder
    if os.path.exists(SHORTCUT_DIR_TEAM):
        try:
            shutil.rmtree(SHORTCUT_DIR_TEAM)
            print(f"[Clean] Removed staging folder: {os.path.basename(SHORTCUT_DIR_TEAM)}")
        except Exception as e:
            print(f"[Warning] Could not clean up staging folder: {e}")

if __name__ == "__main__":
    import sys
    limit_clients = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit_clients = int(sys.argv[1])
        print(f"Running with client limit: {limit_clients}")
    main(limit_clients=limit_clients)
