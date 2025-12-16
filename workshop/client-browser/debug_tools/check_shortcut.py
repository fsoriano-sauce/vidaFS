import win32com.client
import os

def read_shortcut(path):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        print(f"Target: {shortcut.TargetPath}")
        print(f"Arguments: {shortcut.Arguments}")
        return shortcut.Arguments
    except Exception as e:
        print(f"Error reading shortcut: {e}")

path = r"c:\Users\frank\OneDrive\Desktop\vidaFS\workshop\client-browser\For_Team_Desktop\4 - High Caliber Restoration.lnk"
if os.path.exists(path):
    print(f"Checking shortcut: {path}")
    args = read_shortcut(path)
    if "xactimate.com/xor/app/" in args:
        print("\nSUCCESS: Found correct Xactimate URL.")
    else:
        print("\nFAILURE: Did NOT find correct Xactimate URL.")
        # Print what was found for Xactimate
        import re
        found = re.search(r"https://.*?xactimate.*?(\s|$)", args)
        if found:
            print(f"Found instead: {found.group(0)}")
else:
    print("Shortcut not found.")


