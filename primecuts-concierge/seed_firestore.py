"""Seed script for PrimeCuts Firestore catalog."""

from google.cloud import firestore

# Explicitly hardcoded Project ID (not derived from env or google.auth.default)
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-698d519bd637"

SEEDED_CUTS = [
    {
        "id": "CHK-CURRY",
        "name": "Fresh Farm Chicken Curry Cut",
        "category": "chicken",
        "weight": "500g",
        "price": 180.0,
        "description": "Tender, skinless bone-in mix of breast, leg, and thigh pieces. Ideal for traditional curries.",
        "best_for": ["Curry", "Korma", "Stew"],
        "stock": 25,
        "protein_per_100g": "24g",
        "fat_level": "medium",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "CHK-BONELESS",
        "name": "Fresh Chicken Breast (Boneless)",
        "category": "chicken",
        "weight": "500g",
        "price": 260.0,
        "description": "Lean, tender chicken breast fillets. High protein and antibiotic-residue-free.",
        "best_for": ["Grilling", "Stir-fry", "Salads", "Sandwiches", "Gym Diet"],
        "stock": 20,
        "protein_per_100g": "31g",
        "fat_level": "low",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "CHK-DRUMSTICK",
        "name": "Chicken Drumsticks (Skinless)",
        "category": "chicken",
        "weight": "500g (4-5 pcs)",
        "price": 220.0,
        "description": "Juicy and meaty drumsticks, perfect for roasting, frying, or rich gravies.",
        "best_for": ["Tandoori", "Roasting", "Fried Chicken", "Barbecue"],
        "stock": 18,
        "protein_per_100g": "23g",
        "fat_level": "medium",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "CHK-BIRYANI",
        "name": "Premium Chicken Biryani Cut (Large Pieces)",
        "category": "chicken",
        "weight": "1kg",
        "price": 350.0,
        "description": "Specially cut large succulent pieces that stay moist during slow dum cooking.",
        "best_for": ["Dum Biryani", "Awadhi Pulao"],
        "stock": 15,
        "protein_per_100g": "25g",
        "fat_level": "medium",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "CHK-KEEMA",
        "name": "Fresh Chicken Keema (Mince)",
        "category": "chicken",
        "weight": "450g",
        "price": 240.0,
        "description": "Finely minced lean chicken meat for juicy kebabs and quick keema curries.",
        "best_for": ["Seekh Kebabs", "Keema Matar", "Chicken Patties", "Meatballs"],
        "stock": 12,
        "protein_per_100g": "26g",
        "fat_level": "low",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "MUT-CURRY",
        "name": "Rich Goat Mutton Curry Cut",
        "category": "mutton",
        "weight": "500g",
        "price": 460.0,
        "description": "Tender young goat cuts with a balanced mix of bone-in and meat pieces.",
        "best_for": ["Rogan Josh", "Nihari", "Mutton Curry", "Stew"],
        "stock": 15,
        "protein_per_100g": "25g",
        "fat_level": "medium",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "MUT-CHOPS",
        "name": "Goat Ribs & Chops (Chaap)",
        "category": "mutton",
        "weight": "500g",
        "price": 520.0,
        "description": "Succulent rib cuts with fat-marbled bone-in meat.",
        "best_for": ["Mutton Chaap Fry", "Grilling", "Pan-sear", "Barbecue"],
        "stock": 10,
        "protein_per_100g": "22g",
        "fat_level": "high",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "MUT-BONELESS",
        "name": "Tender Boneless Goat Meat",
        "category": "mutton",
        "weight": "500g",
        "price": 590.0,
        "description": "Clean, fat-trimmed boneless meat cubes from the leg and shoulder.",
        "best_for": ["Boti Kebab", "Mutton Sukka", "Slow Roasts"],
        "stock": 8,
        "protein_per_100g": "28g",
        "fat_level": "low",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "MUT-KEEMA",
        "name": "Fresh Goat Keema (Mince)",
        "category": "mutton",
        "weight": "450g",
        "price": 490.0,
        "description": "Hand-trimmed finely ground goat mince, ideal for kebabs and samosas.",
        "best_for": ["Galouti Kebab", "Keema Pav", "Mutton Kofta", "Keema Samosa"],
        "stock": 10,
        "protein_per_100g": "24g",
        "fat_level": "medium",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
    {
        "id": "MUT-BIRYANI",
        "name": "Special Goat Biryani Cut",
        "category": "mutton",
        "weight": "1kg",
        "price": 890.0,
        "description": "Prime cuts from shoulder and leg portions, cut uniformly for biryani.",
        "best_for": ["Hyderabadi Dum Biryani", "Awadhi Biryani", "Mutton Yakhni Pulao"],
        "stock": 12,
        "protein_per_100g": "25g",
        "fat_level": "medium",
        "temperature_standard": "0-4°C fresh chilled",
        "is_available": True,
    },
]

def seed():
    print(f"Connecting to Firestore using project ID: '{FIRESTORE_PROJECT_ID}'...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("cuts")
    
    for cut in SEEDED_CUTS:
        doc_ref = collection_ref.document(cut["id"])
        doc_ref.set(cut)
        print(f"✓ Seeded cut: {cut['id']} - {cut['name']}")

    print("\n✅ All fresh cuts seeded into Firestore collection 'cuts' successfully.")

if __name__ == "__main__":
    seed()
