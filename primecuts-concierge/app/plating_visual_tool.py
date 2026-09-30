"""Plating visual asset generator and Cloud Storage tool for PrimeCuts Agent.

Generates culinary plating presentation SVG graphics and saves them directly
to the project's public Cloud Storage bucket, returning a live public HTTP URL.
"""

import os
import uuid
from google.cloud import storage
from app.firestore_client import FIRESTORE_PROJECT_ID

BUCKET_NAME = os.getenv("PRIMECUTS_STORAGE_BUCKET", f"primecuts-media-{FIRESTORE_PROJECT_ID}")

# Curated visual palette for meat dishes
DISH_THEMES = {
    "biryani": {
        "dish_title": "Royal Dum Biryani Plating",
        "rice_color": "#E69C24",
        "meat_color": "#78281F",
        "garnish": "Golden Fried Onions, Saffron Threads & Fresh Mint",
        "plate_color": "#2C3E50",
        "accent": "#F39C12",
        "description": "Fragrant aged basmati infused with whole spices and slow-cooked succulent meat cuts.",
    },
    "curry": {
        "dish_title": "Slow-Simmered Rich Gravy Plating",
        "rice_color": "#B03A2E",
        "meat_color": "#641E16",
        "garnish": "Ginger Juliennes, Fresh Cilantro & Rogan Swirl",
        "plate_color": "#1B2631",
        "accent": "#E74C3C",
        "description": "Tender meat pieces enveloped in an aromatic, caramelized onion and whole-spice gravy.",
    },
    "kebab": {
        "dish_title": "Charcoal Tandoori Grill Plating",
        "rice_color": "#C0392B",
        "meat_color": "#512E5F",
        "garnish": "Charred Lemon Wedges, Mint-Coriander Chutney & Pickled Rings",
        "plate_color": "#17202A",
        "accent": "#27AE60",
        "description": "Smoky char on succulent meat cuts with traditional artisanal tandoori glaze.",
    },
    "roast": {
        "dish_title": "Herb Butter Pan-Sear Plating",
        "rice_color": "#D35400",
        "meat_color": "#4A235A",
        "garnish": "Rosemary Sprigs, Roasted Garlic Cloves & Black Peppercorn Glaze",
        "plate_color": "#212F3D",
        "accent": "#E67E22",
        "description": "Seared golden-brown exterior sealing in delicate juices and rich marbling.",
    },
}


def _get_theme(dish_name: str):
    name_lower = dish_name.lower()
    for key, theme in DISH_THEMES.items():
        if key in name_lower:
            return theme
    if "fry" in name_lower or "tandoori" in name_lower or "chaap" in name_lower:
        return DISH_THEMES["kebab"]
    if "nihari" in name_lower or "korma" in name_lower or "stew" in name_lower:
        return DISH_THEMES["curry"]
    return DISH_THEMES["roast"]


def generate_recipe_plating_visual(cut_name: str, dish_name: str) -> str:
    """Generates a culinary food presentation visual for a dish and uploads it to public Cloud Storage.

    Args:
        cut_name: Name of the meat cut (e.g. 'Special Goat Biryani Cut', 'Fresh Chicken Breast (Boneless)').
        dish_name: Name of the dish (e.g. 'Hyderabadi Dum Biryani', 'Tandoori Roast', 'Mutton Rogan Josh').

    Returns:
        Public HTTP URL of the generated visual card and chef presentation notes.
    """
    try:
        theme = _get_theme(dish_name)
        file_id = f"plating_{uuid.uuid4().hex[:8]}.svg"

        # High-res SVG culinary card with vector food styling
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="100%" height="100%">
  <defs>
    <radialGradient id="bgGlow" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="#2D3748" />
      <stop offset="100%" stop-color="#1A202C" />
    </radialGradient>
    <radialGradient id="plateGlow" cx="45%" cy="45%" r="60%">
      <stop offset="0%" stop-color="{theme['plate_color']}" />
      <stop offset="85%" stop-color="#0E1621" />
      <stop offset="100%" stop-color="#05080C" />
    </radialGradient>
    <radialGradient id="foodGlow" cx="50%" cy="50%" r="55%">
      <stop offset="0%" stop-color="{theme['rice_color']}" />
      <stop offset="80%" stop-color="{theme['meat_color']}" />
      <stop offset="100%" stop-color="#3A120D" />
    </radialGradient>
    <filter id="shadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="16" stdDeviation="16" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="800" height="600" fill="url(#bgGlow)" rx="16"/>

  <!-- Top Banner -->
  <rect x="0" y="0" width="800" height="85" fill="#111827" fill-opacity="0.8"/>
  <text x="40" y="42" fill="#E2E8F0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="22" font-weight="bold">🥩 PrimeCuts Culinary Presentation</text>
  <text x="40" y="66" fill="#A0AEC0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="14">Chef Styling Preview • {cut_name}</text>
  <rect x="630" y="24" width="130" height="36" rx="18" fill="{theme['accent']}" fill-opacity="0.2"/>
  <text x="695" y="47" fill="{theme['accent']}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">CHEF PREVIEW</text>

  <!-- Center Plating Platter -->
  <circle cx="400" cy="315" r="190" fill="url(#plateGlow)" filter="url(#shadow)" stroke="#4A5568" stroke-width="4"/>
  <circle cx="400" cy="315" r="172" fill="none" stroke="{theme['accent']}" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.6"/>

  <!-- Prepared Dish Base -->
  <ellipse cx="400" cy="318" rx="135" ry="110" fill="url(#foodGlow)" />

  <!-- Meat Cuts & Garnish Highlights -->
  <ellipse cx="370" cy="300" rx="42" ry="30" fill="{theme['meat_color']}" stroke="{theme['accent']}" stroke-width="1.5" opacity="0.95"/>
  <ellipse cx="430" cy="325" rx="46" ry="32" fill="{theme['meat_color']}" stroke="{theme['accent']}" stroke-width="1.5" opacity="0.95"/>
  <ellipse cx="390" cy="340" rx="36" ry="24" fill="{theme['meat_color']}" opacity="0.9"/>

  <!-- Herbs / Garnishes -->
  <circle cx="360" cy="285" r="5" fill="#48BB78"/>
  <circle cx="375" cy="280" r="4" fill="#38A169"/>
  <circle cx="440" cy="310" r="6" fill="#48BB78"/>
  <circle cx="420" cy="345" r="5" fill="#48BB78"/>
  <line x1="390" y1="270" x2="410" y2="295" stroke="#F6E05E" stroke-width="2"/>
  <line x1="415" y1="275" x2="430" y2="290" stroke="#F6E05E" stroke-width="2"/>

  <!-- Bottom Details Box -->
  <rect x="40" y="475" width="720" height="95" rx="12" fill="#1A202C" stroke="#2D3748" stroke-width="1.5"/>
  <text x="65" y="508" fill="#F7FAFC" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="18" font-weight="bold">{dish_name}</text>
  <text x="65" y="530" fill="#CBD5E0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13">{theme['description']}</text>
  <text x="65" y="552" fill="{theme['accent']}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600">Garnish &amp; Finish: {theme['garnish']}</text>
</svg>"""

        # Upload directly to the public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"recipes/{file_id}")
        blob.upload_from_string(svg_content, content_type="image/svg+xml")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/recipes/{file_id}"
        return (
            f"📸 Plating Visual Generated for **{dish_name}** using **{cut_name}**!\n"
            f"• Public URL: {public_url}\n"
            f"• Plating Style: {theme['dish_title']}\n"
            f"• Garnish: {theme['garnish']}\n"
            f"• Presentation: {theme['description']}"
        )
    except Exception as e:
        return f"Error generating plating visual: {str(e)}"
