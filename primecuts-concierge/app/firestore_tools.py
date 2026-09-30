"""Firestore read and write function tools for PrimeCuts ADK Agent."""

import datetime
from typing import Dict, List, Optional
from app.firestore_client import get_db

CUTS_COLLECTION = "cuts"
ORDERS_COLLECTION = "orders"
PREFS_COLLECTION = "customer_preferences"


def firestore_list_cuts(category: Optional[str] = None) -> str:
    """Reads fresh meat cuts directly from the Firestore 'cuts' database.

    Args:
        category: Optional category filter: 'chicken', 'mutton', or None for all.

    Returns:
        Formatted catalog listing from Firestore.
    """
    try:
        db = get_db()
        query = db.collection(CUTS_COLLECTION)
        if category and category.strip().lower() in ["chicken", "mutton"]:
            query = query.where("category", "==", category.strip().lower())

        docs = list(query.stream())
        if not docs:
            return f"No cuts found in Firestore for category: {category}"

        lines = [f"🥩 PrimeCuts Live Firestore Catalog ({len(docs)} items):"]
        for doc in docs:
            d = doc.to_dict()
            status = "In Stock" if d.get("is_available", True) and d.get("stock", 0) > 0 else "Out of Stock"
            lines.append(
                f"• [{d.get('id', doc.id)}] {d.get('name')} - ₹{d.get('price', 0):.0f} / {d.get('weight')}\n"
                f"  Category: {d.get('category')} | Protein: {d.get('protein_per_100g')} | Stock: {d.get('stock')} ({status})\n"
                f"  Best For: {', '.join(d.get('best_for', [])) if isinstance(d.get('best_for'), list) else d.get('best_for')}\n"
                f"  Temp Standard: {d.get('temperature_standard')}"
            )

        return "\n\n".join(lines)
    except Exception as e:
        return f"Error reading cuts from Firestore: {str(e)}"


def firestore_get_cut_details(item_id: str) -> str:
    """Retrieves full specifications and stock for a specific cut from Firestore.

    Args:
        item_id: Product ID code (e.g., 'MUT-BIRYANI', 'CHK-BONELESS', etc.).

    Returns:
        Detailed specifications including nutritional macros, freshness standard, and stock.
    """
    try:
        db = get_db()
        key = item_id.strip().upper()
        doc_ref = db.collection(CUTS_COLLECTION).document(key)
        doc = doc_ref.get()
        if not doc.exists:
            return f"Cut '{item_id}' not found in Firestore."

        d = doc.to_dict()
        best_for = ", ".join(d.get("best_for", [])) if isinstance(d.get("best_for"), list) else d.get("best_for")
        return (
            f"🥩 Cut Specification: {d.get('name')} ({d.get('id')})\n"
            f"• Category: {d.get('category')}\n"
            f"• Price: ₹{d.get('price', 0):.0f} per {d.get('weight')}\n"
            f"• Description: {d.get('description')}\n"
            f"• Recommended Cooking / Dishes: {best_for}\n"
            f"• Protein Content: {d.get('protein_per_100g', 'N/A')}\n"
            f"• Fat Profile: {d.get('fat_level', 'N/A')}\n"
            f"• Cold-Chain Standard: {d.get('temperature_standard', '0-4°C fresh')}\n"
            f"• Current Inventory: {d.get('stock', 0)} packs available"
        )
    except Exception as e:
        return f"Error retrieving cut details from Firestore: {str(e)}"


def firestore_save_customer_preferences(
    customer_name: str,
    customer_phone: str,
    favorite_cuts: Optional[str] = None,
    dietary_goal: Optional[str] = None,
    preferred_spice_level: Optional[str] = None,
    delivery_notes: Optional[str] = None,
) -> str:
    """Saves or updates a customer's dietary preferences and delivery profile in Firestore.

    Args:
        customer_name: Customer's name.
        customer_phone: Customer's phone number (used as unique identifier).
        favorite_cuts: Preferred meat cuts (e.g. 'Boneless chicken breast, Goat biryani cut').
        dietary_goal: Dietary preference (e.g. 'High protein / gym diet', 'Traditional slow-cooking', 'Lean cuts').
        preferred_spice_level: Spice preference (e.g. 'Mild', 'Medium', 'Spicy').
        delivery_notes: Custom delivery instructions or apartment notes.

    Returns:
        Confirmation that preferences were recorded in Firestore.
    """
    try:
        db = get_db()
        doc_ref = db.collection(PREFS_COLLECTION).document(customer_phone.strip())
        data = {
            "customer_name": customer_name,
            "customer_phone": customer_phone.strip(),
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if favorite_cuts:
            data["favorite_cuts"] = favorite_cuts
        if dietary_goal:
            data["dietary_goal"] = dietary_goal
        if preferred_spice_level:
            data["preferred_spice_level"] = preferred_spice_level
        if delivery_notes:
            data["delivery_notes"] = delivery_notes

        doc_ref.set(data, merge=True)
        return (
            f"✅ Saved customer profile for {customer_name} ({customer_phone}) to Firestore!\n"
            f"• Dietary Goal: {data.get('dietary_goal', 'Not specified')}\n"
            f"• Favorite Cuts: {data.get('favorite_cuts', 'Not specified')}\n"
            f"• Notes: {data.get('delivery_notes', 'None')}"
        )
    except Exception as e:
        return f"Error saving customer preferences: {str(e)}"


def firestore_get_customer_preferences(customer_phone: str) -> str:
    """Fetches saved customer profile, dietary preferences, and notes from Firestore.

    Args:
        customer_phone: Customer's phone number.

    Returns:
        Customer's recorded preferences or indication that profile doesn't exist yet.
    """
    try:
        db = get_db()
        doc_ref = db.collection(PREFS_COLLECTION).document(customer_phone.strip())
        doc = doc_ref.get()
        if not doc.exists:
            return f"No previous profile found in Firestore for phone {customer_phone}."

        d = doc.to_dict()
        return (
            f"👤 Customer Profile ({d.get('customer_name')}, {customer_phone}):\n"
            f"• Dietary Goal: {d.get('dietary_goal', 'Standard')}\n"
            f"• Favorite Cuts: {d.get('favorite_cuts', 'None specified')}\n"
            f"• Spice Level: {d.get('preferred_spice_level', 'Medium')}\n"
            f"• Delivery Notes: {d.get('delivery_notes', 'None')}\n"
            f"• Last Updated: {d.get('updated_at', 'Recent')}"
        )
    except Exception as e:
        return f"Error reading customer preferences: {str(e)}"
