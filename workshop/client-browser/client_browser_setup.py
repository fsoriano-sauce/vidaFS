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
        AND (sa.client_id IS NULL OR sa.client_id = '')  -- Exclude API-connected systems
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

def create_client_dashboard(clean_name: str, client_name: str, urls: List[str]) -> str:
    """
    Creates a local HTML dashboard file for the client.
    Returns the absolute path to the file.
    """
    # Dashboard directory - fixed path for portability
    dash_dir = r"C:\Automation\Dashboards"
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

def get_standard_icon() -> str:
    """
    Returns the path to the standard WeScope green icon.
    Creates it if it doesn't exist.
    """
    if not HAS_PIL:
        print("Warning: PIL not available. Using default Chrome icon.")
        return CHROME_EXE_PATH

    # Ensure icon directory exists
    if not os.path.exists(ICON_DIR):
        os.makedirs(ICON_DIR)

    # Path to standard icon
    icon_path = os.path.join(ICON_DIR, "WeScope_Standard.ico")
    
    # Create if doesn't exist
    if not os.path.exists(icon_path):
        print("Creating standard WeScope icon...")
        GREEN_COLOR = (46, 204, 113)  # Professional green
        img = Image.new('RGB', ICON_SIZE, GREEN_COLOR)
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

def clean_target_url(url: str) -> str:
    """
    Removes specific login paths from the URL so the browser lands on the dashboard
    if the session is already active. Also applies known URL fixes/overrides.
    """
    # =========================================================================
    # URL OVERRIDES - Fix known bad URLs from source data
    # =========================================================================
    URL_OVERRIDES = {
        # Docusketch: portal_2 doesn't exist, should be portal
        "app.docusketch.com/portal_2": "app.docusketch.com/portal",
    }
    
    # =========================================================================
    # FULL URL REPLACEMENTS - Replace entire URL with a better destination
    # These take priority and return immediately
    # =========================================================================
    
    # Xactimate/XactAnalysis/ContentsTrack - Verisk login URLs should go directly to the portal
    # These all share the same Verisk backend but need different portal URLs
    if "identity.verisk.com" in url.lower() or "xactimate.com" in url.lower() or "xactanalysis.com" in url.lower() or "contentstrack.com" in url.lower():
        if "xactimate" in url.lower() or "xor" in url.lower():
            print(f"  [URL Replacement] Xactimate: -> portal page")
            return "https://xactimate.com/xor/app/dashboard"
        elif "xactanalysis" in url.lower():
            print(f"  [URL Replacement] XactAnalysis: -> portal page")
            return "https://xactanalysis.com/apps/xnportal/xid_landing.jsp?context=GENER"
        elif "contentstrack" in url.lower():
            print(f"  [URL Replacement] ContentsTrack: -> portal page")
            return "https://contentstrack.com/dashboard"
        else:
            # Generic Verisk - just go to settings (or the base)
            print(f"  [URL Replacement] Verisk: stripping login params")
            return "https://identity.verisk.com"
    
    # Symbility/Claims Workspace - go directly to claims page, not login
    # NOTE: Symbility expires sessions on browser close (like MICA)
    if "symbility.net" in url.lower():
        print(f"  [URL Replacement] Symbility: -> #/claims")
        return "https://www.symbility.net/ux/site/#/claims"
    
    # NextGear Platforms - go to post-login page to avoid "Hello World" error
    # These platforms all use NextGear software and have the same Login.aspx issue
    # All white labels: RESTORE365, DASH, Alacrity, FUSION, RMS, Solitaire
    if "restore365.net" in url.lower():
        print(f"  [URL Replacement] RESTORE365: -> uPostLogin.aspx")
        return "https://restore365.net/Enterprise/Module/User/uPostLogin.aspx"
    
    if "dash-ngs.net" in url.lower():
        print(f"  [URL Replacement] DASH: -> uPostLogin.aspx")
        return "https://dash-ngs.net/NextGear/Enterprise/Module/User/uPostLogin.aspx"
    
    if "fusion-ngs.net" in url.lower():
        print(f"  [URL Replacement] FUSION: -> uPostLogin.aspx")
        return "https://fusion-ngs.net/Enterprise/Module/User/uPostLogin.aspx"
    
    if "rms-ngs.net" in url.lower():
        print(f"  [URL Replacement] RMS: -> uPostLogin.aspx")
        return "https://rms-ngs.net/RMS/Module/User/uPostLogin.aspx"
    
    if "solitaire-ngs.net" in url.lower():
        print(f"  [URL Replacement] Solitaire: -> uPostLogin.aspx")
        return "https://solitaire-ngs.net/DKI/Module/User/uPostLogin.aspx"
    
    if "alacrity.net" in url.lower():
        print(f"  [URL Replacement] Alacrity: -> uPostLogin.aspx")
        return "https://www.alacrity.net/User/uPostLogin.aspx"
    
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


def fetch_client_data(limit_clients: int = None) -> Dict[str, List[str]]:
    """
    Fetches client systems from BigQuery.
    Mocks data if in Demo Mode and BQ lib is missing.
    limit_clients: If specified, limit to this many clients for testing
    """
    if DEMO_MODE and not HAS_BIGQUERY:
        print("Warning: 'google-cloud-bigquery' not found. Using MOCK data for demo.")
        mock_data = {
            "State Farm": ["https://login.statefarm.com", "https://claims.statefarm.com/login"],
            "Allstate": ["https://agent.allstate.com/signin"],
            "Farmers": ["https://portal.farmers.com/auth/login", "https://billing.farmers.com"],
            "Docusketch": ["https://app.docusketch.com/login"]
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

# ... (Existing funcs) ...


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

    # Get the standard WeScope icon (once for all clients)
    standard_icon_path = get_standard_icon()
    
    # 2. Iterate and Process
    for client_name, urls in clients_data.items():
        clean_name = sanitize_filename(client_name)
        
        # Clean URLs for the shortcut arguments
        # We want the shortcut to open the dashboard, not the login page
        cleaned_urls = [clean_target_url(u) for u in urls]
        
        # Sort URLs by category (CRM first, then docs, then estimating, etc.)
        cleaned_urls_sorted = sorted(cleaned_urls, key=lambda url: categorize_system(url))
        
        # EXCLUSIONS: Remove API-integrated systems even if they have credentials
        # These systems are typically accessed via API and don't need browser tabs
        excluded_keywords = ['matterport', 'hover', 'eagleview', 'westhill', 'jobnimbus']
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
        
        # Combine all URLs (Dashboard + Systems)
        all_urls = [dashboard_url] + final_urls
        url_args = " ".join([f'"{url}"' for url in all_urls])

        # --- Scope: Self ---
        print(f"\n[Creating Shortcut] {clean_name} (Self)")
        self_profile_path = os.path.join(BASE_DIR_SELF, clean_name)
        
        # Ensure profile directory exists
        if not os.path.exists(self_profile_path):
            os.makedirs(self_profile_path)
        
        # Add profile name to Chrome arguments so it shows in window title
        chrome_args = f'--user-data-dir="{self_profile_path}" --profile-directory="Default" {url_args}'
        
        # Output to "For_Frankie_Desktop" folder for packaging
        frankie_shortcut_dir = os.path.join(os.getcwd(), "For_Frankie_Desktop")
        if not os.path.exists(frankie_shortcut_dir):
            os.makedirs(frankie_shortcut_dir)

        create_desktop_shortcut(
            name=clean_name,
            target=CHROME_EXE_PATH,
            arguments=chrome_args,
            folder=frankie_shortcut_dir,
            description=f"Launch {client_name} Systems",
            icon_path=standard_icon_path
        )

        # --- Scope: Ana ---
        print(f"[Creating Shortcut] {clean_name} (Ana)")
        ana_profile_path = os.path.join(BASE_DIR_ANA, clean_name)
        
        # Ensure profile directory exists
        if not os.path.exists(ana_profile_path):
            os.makedirs(ana_profile_path)

        create_desktop_shortcut(
            name=f"Ana - {clean_name}",
            target=CHROME_EXE_PATH,
            arguments=f'--user-data-dir="{ana_profile_path}" {url_args}',
            folder=SHORTCUT_DIR_ANA,
            description=f"Launch {client_name} Systems for Ana",
            icon_path=standard_icon_path
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
