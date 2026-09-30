"""Fresh Chicken and Mutton Catalog and Persistent Order Management."""

import json
import os
import uuid
from typing import Dict, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders_db.json")

# Inventory of fresh meat products
CATALOG = {
    # Chicken cuts
    "CHK-CURRY": {
        "id": "CHK-CURRY",
        "name": "Fresh Farm Chicken Curry Cut",
        "category": "chicken",
        "weight": "500g",
        "price": 180.0,
        "description": "Tender, skinless bone-in mix of breast, leg, and thigh pieces. Ideal for traditional curries.",
        "best_for": "Curry, Korma, Stew",
        "stock": 25,
    },
    "CHK-BONELESS": {
        "id": "CHK-BONELESS",
        "name": "Fresh Chicken Breast (Boneless)",
        "category": "chicken",
        "weight": "500g",
        "price": 260.0,
        "description": "Lean, tender chicken breast fillets. High protein and antibiotic-residue-free.",
        "best_for": "Grilling, Stir-fry, Salads, Sandwiches",
        "stock": 20,
    },
    "CHK-DRUMSTICK": {
        "id": "CHK-DRUMSTICK",
        "name": "Chicken Drumsticks (Skinless)",
        "category": "chicken",
        "weight": "500g (4-5 pcs)",
        "price": 220.0,
        "description": "Juicy and meaty drumsticks, perfect for roasting, frying, or rich gravies.",
        "best_for": "Tandoori, Roasting, Fried Chicken",
        "stock": 18,
    },
    "CHK-BIRYANI": {
        "id": "CHK-BIRYANI",
        "name": "Premium Chicken Biryani Cut (Large Pieces)",
        "category": "chicken",
        "weight": "1kg",
        "price": 350.0,
        "description": "Specially cut large succulent pieces that stay moist during slow dum cooking.",
        "best_for": "Dum Biryani, Pulao",
        "stock": 15,
    },
    "CHK-KEEMA": {
        "id": "CHK-KEEMA",
        "name": "Fresh Chicken Keema (Mince)",
        "category": "chicken",
        "weight": "450g",
        "price": 240.0,
        "description": "Finely minced lean chicken meat for juicy kebabs and quick keema curries.",
        "best_for": "Seekh Kebabs, Keema Matar, Patties",
        "stock": 12,
    },
    # Mutton cuts
    "MUT-CURRY": {
        "id": "MUT-CURRY",
        "name": "Rich Goat Mutton Curry Cut",
        "category": "mutton",
        "weight": "500g",
        "price": 460.0,
        "description": "Tender young goat cuts with a balanced mix of bone-in and meat pieces.",
        "best_for": "Mutton Rogan Josh, Nihari, Traditional Curry",
        "stock": 15,
    },
    "MUT-CHOPS": {
        "id": "MUT-CHOPS",
        "name": "Goat Ribs & Chops (Chaap)",
        "category": "mutton",
        "weight": "500g",
        "price": 520.0,
        "description": "Succulent rib cuts with fat-marbled bone-in meat.",
        "best_for": "Mutton Chaap Fry, Grilling, Pan-sear",
        "stock": 10,
    },
    "MUT-BONELESS": {
        "id": "MUT-BONELESS",
        "name": "Tender Boneless Goat Meat",
        "category": "mutton",
        "weight": "500g",
        "price": 590.0,
        "description": "Clean, fat-trimmed boneless meat cubes from the leg and shoulder.",
        "best_for": "Boti Kebab, Mutton Sukka, Slow Roasts",
        "stock": 8,
    },
    "MUT-KEEMA": {
        "id": "MUT-KEEMA",
        "name": "Fresh Goat Keema (Mince)",
        "category": "mutton",
        "weight": "450g",
        "price": 490.0,
        "description": "Hand-trimmed finely ground goat mince, ideal for kebabs and samosas.",
        "best_for": "Galouti Kebab, Keema Pav, Kofta",
        "stock": 10,
    },
    "MUT-BIRYANI": {
        "id": "MUT-BIRYANI",
        "name": "Special Goat Biryani Cut",
        "category": "mutton",
        "weight": "1kg",
        "price": 890.0,
        "description": "Prime cuts from shoulder and leg portions, cut uniformly for biryani.",
        "best_for": "Hyderabadi Dum Biryani, Awadhi Biryani",
        "stock": 12,
    },
}

def load_orders() -> Dict[str, dict]:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_order(order_record: dict):
    orders = load_orders()
    orders[order_record["order_id"]] = order_record
    with open(DB_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def get_order(order_id: str) -> Optional[dict]:
    orders = load_orders()
    return orders.get(order_id)
