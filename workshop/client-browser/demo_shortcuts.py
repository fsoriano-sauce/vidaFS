#!/usr/bin/env python3
"""
Demo script to create desktop shortcuts with custom icons.
This demonstrates the complete functionality without requiring BigQuery.
"""

import os
import sys
from typing import List

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our functions
from client_browser_setup import (
    sanitize_filename,
    generate_client_icon,
    create_desktop_shortcut,
    get_desktop_path
)

def main():
    """Demo function to create shortcuts with custom icons."""
    print("Client Browser - Shortcut Creation Demo")
    print("=" * 45)

    # Sample client data
    clients_data = {
        "State Farm": ["https://login.statefarm.com"],
        "Allstate Insurance": ["https://agent.allstate.com"],
        "Farmers Insurance": ["https://portal.farmers.com"]
    }

    print(f"Creating shortcuts for {len(clients_data)} clients on your desktop...")
    print()

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    for client_name, urls in clients_data.items():
        print(f"Processing: {client_name}")

        # Generate custom icon
        icon_path = generate_client_icon(client_name)

        # Create URL arguments
        url_args = " ".join([f'"{url}"' for url in urls])

        # Create desktop shortcut
        shortcut_name = sanitize_filename(client_name)
        profile_path = f"./profiles/{shortcut_name}"  # Mock profile path

        create_desktop_shortcut(
            name=shortcut_name,
            target=chrome_path,
            arguments=f'--user-data-dir="{profile_path}" {url_args}',
            folder=get_desktop_path(),
            description=f"Launch {client_name} Systems (Demo)",
            icon_path=icon_path
        )

        print(f"  ✓ Created shortcut with custom icon")
        print()

    print("Demo Complete!")
    print(f"Check your desktop for {len(clients_data)} new shortcuts with unique icons.")
    print("Each shortcut has a different colored icon with the client's initials!")

if __name__ == "__main__":
    main()


