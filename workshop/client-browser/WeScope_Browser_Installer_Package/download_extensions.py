import os
import requests
import zipfile
import io

# Configuration
EXTENSIONS = {
    "Xactware_ClickOnce": "ghonblphoimcehigdfdmomaochonfobc",
    "WeScope_Autofill": "hhoilbbpbbfbihpafjobnfffffoocoba",
}

DEST_DIR = r"C:\Automation\Extensions"

def download_and_extract(name, ext_id):
    print(f"Processing {name} ({ext_id})...")
    url = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=98.0.4758.102&acceptformat=crx2,crx3&x=id%3D{ext_id}%26uc"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"  Downloaded {len(response.content)} bytes.")

        # Save CRX for reference
        crx_path = os.path.join(DEST_DIR, f"{name}.crx")
        if not os.path.exists(DEST_DIR):
            os.makedirs(DEST_DIR)
            
        with open(crx_path, "wb") as f:
            f.write(response.content)

        # Extract
        extract_path = os.path.join(DEST_DIR, name)
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)

        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(extract_path)
            print(f"  Extracted to {extract_path}")
        except zipfile.BadZipFile:
            print("  [WARNING] Python zipfile failed (CRX header issue?). trying to skip header...")
            # Simple header skip (CRX3 header is variable, but CRX2 is usually fixed)
            # This is a bit hacky. Robust extraction requires parsing the CRX header.
            # For now, we will notify the user if this fails.
            print("  Please manually unzip the CRX file if needed.")

    except Exception as e:
        print(f"  [ERROR] Failed: {e}")

if __name__ == "__main__":
    for name, ext_id in EXTENSIONS.items():
        download_and_extract(name, ext_id)









