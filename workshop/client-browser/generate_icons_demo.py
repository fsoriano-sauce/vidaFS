#!/usr/bin/env python3
"""
Simple demo script to generate custom icons for clients.
This can be run independently to test icon generation.
"""

import os
import re
from typing import List
import colorsys

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL (Pillow) not found. Install with: pip install Pillow")

# Configuration
ICON_SIZE = (256, 256)
ICON_DIR = os.path.join(os.getcwd(), "client_icons")

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be safe for use as a filename."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def generate_client_icon(client_name: str) -> str:
    """
    Generates a custom icon for the client with their name and a colored background.
    Returns the path to the generated icon file.
    """
    if not HAS_PIL:
        print("Warning: PIL not available. Cannot generate icons.")
        return ""

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

def main():
    """Demo function to generate icons for sample clients."""
    print("Client Browser - Icon Generation Demo")
    print("=" * 40)

    if not HAS_PIL:
        print("PIL (Pillow) is required for icon generation.")
        print("Install with: pip install Pillow")
        return

    # Sample clients for demo
    clients = [
        "State Farm",
        "Allstate Insurance",
        "Farmers Insurance",
        "Progressive",
        "Geico",
        "Liberty Mutual"
    ]

    print(f"Generating icons for {len(clients)} clients...")
    print()

    generated_icons = []
    for client in clients:
        icon_path = generate_client_icon(client)
        if icon_path:
            generated_icons.append((client, icon_path))

    print()
    print("Icon Generation Complete!")
    print(f"Generated {len(generated_icons)} icons in: {ICON_DIR}")
    print()
    print("Generated icons:")
    for client, icon_path in generated_icons:
        print(f"  {client}: {os.path.basename(icon_path)}")

    print()
    print("You can now use these .ico files for desktop shortcuts!")

if __name__ == "__main__":
    main()


