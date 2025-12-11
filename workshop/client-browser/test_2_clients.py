#!/usr/bin/env python3
"""
Test script to run client browser setup with just 2 clients.
This implements the correct interactive workflow.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function
from client_browser_setup import main

if __name__ == "__main__":
    print("=" * 60)
    print("CLIENT BROWSER SETUP - 2 CLIENT TEST")
    print("=" * 60)
    print("This will:")
    print("1. Fetch 2 real clients from BigQuery")
    print("2. Create profiles for Self and Ana")
    print("3. Launch interactive browser sessions for login")
    print("4. Create shortcuts with custom icons")
    print("=" * 60)

    # Run with 2 client limit
    main(limit_clients=2)
