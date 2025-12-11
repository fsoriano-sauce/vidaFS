import os
import zipfile

output_dir = r"C:\Users\frank\OneDrive\Desktop\vidaFS\workshop\client-browser"

print("=" * 80)
print("Creating Final Package for Ana")
print("=" * 80)

# 1. Create Dashboards zip
print("\nCreating Ana_Dashboards.zip...")
dash_zip = os.path.join(output_dir, "Ana_Dashboards.zip")
dash_dir = r"C:\Automation\Dashboards"

if not os.path.exists(dash_dir):
    print(f"ERROR: Dashboards directory not found: {dash_dir}")
    print("Run client_browser_setup.py first!")
    exit(1)

with zipfile.ZipFile(dash_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    count = 0
    for file in os.listdir(dash_dir):
        if file.endswith('.html'):
            z.write(os.path.join(dash_dir, file), file)
            count += 1
    print(f"  Added {count} dashboard files")

# 2. Create Final Package
final_package = os.path.join(output_dir, "Ana_Complete_Setup_Package.zip")
if os.path.exists(final_package):
    os.remove(final_package)

print(f"\nCreating: {final_package}")

with zipfile.ZipFile(final_package, 'w', zipfile.ZIP_DEFLATED) as zipf:
    files_to_include = [
        "Ana_Desktop_Shortcuts.zip",
        "Ana_Dashboards.zip",
        "SETUP_FOR_ANA.bat",
        "README_FOR_ANA.txt",
    ]
    
    for filename in files_to_include:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            zipf.write(filepath, filename)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  [OK] {filename} ({size_mb:.2f} MB)")
        else:
            print(f"  [MISSING] {filename}")

size_mb = os.path.getsize(final_package) / (1024 * 1024)
print(f"\n{'=' * 80}")
print(f"SUCCESS! Complete package created:")
print(f"  Location: {final_package}")
print(f"  Size: {size_mb:.2f} MB")
print(f"\nContents:")
print(f"  - 28 client shortcuts")
print(f"  - Client Dashboards (HTML landing pages)")
print(f"  - Automated setup script")
print(f"  - Instructions")
print(f"{'=' * 80}")

