"""ADK Function Tools for Fresh Chicken & Mutton Delivery Agent."""

import datetime
import uuid
from typing import Dict, List, Optional
from app.meat_catalog import CATALOG, save_order, get_order, load_orders


def list_fresh_cuts(category: Optional[str] = None) -> str:
    """Browse fresh chicken and mutton cuts currently in stock.

    Args:
        category: Optional filter: "chicken", "mutton", or None/empty for all products.

    Returns:
        Formatted catalog listing with prices, cuts, weights, and cooking recommendations.
    """
    category_clean = category.strip().lower() if category else None
    items = []
    for item in CATALOG.values():
        if category_clean and item["category"] != category_clean:
            continue
        items.append(
            f"• [{item['id']}] {item['name']} - ₹{item['price']:.0f} / {item['weight']}\n"
            f"  Description: {item['description']}\n"
            f"  Best for: {item['best_for']} | In Stock: {item['stock']} packs"
        )

    if not items:
        return f"No cuts found for category '{category}'. Available categories are 'chicken' and 'mutton'."

    header = f"🥩 Fresh Cut Selection ({category_clean.upper() if category_clean else 'ALL MEATS'}):"
    return f"{header}\n\n" + "\n\n".join(items)


def recommend_cut_for_dish(dish_name: str) -> str:
    """Provides expert butchery recommendation of the best fresh meat cuts for a specific dish.

    Args:
        dish_name: The name of the dish (e.g., 'Dum Biryani', 'Kebab', 'Curry', 'Roast', 'Diet/Gym').

    Returns:
        Recommendations on the best meat cut and why it fits the cooking technique.
    """
    dish = dish_name.lower()
    matches = []
    for item in CATALOG.values():
        if any(term in dish for term in item["best_for"].lower().split(", ")) or any(term in item["best_for"].lower() for term in dish.split()):
            matches.append(item)

    if matches:
        output = [f"👨‍🍳 Chef's Pick for '{dish_name}':"]
        for m in matches:
            output.append(
                f"- **{m['name']}** (₹{m['price']:.0f} / {m['weight']})\n"
                f"  Why: {m['description']} Specifically cut for {m['best_for']}."
            )
        return "\n\n".join(output)

    return (
        f"For '{dish_name}', here are our top recommendations:\n"
        f"• For curries/gravies: 'Fresh Farm Chicken Curry Cut' (CHK-CURRY) or 'Rich Goat Mutton Curry Cut' (MUT-CURRY).\n"
        f"• For slow dum cooking: 'Premium Chicken Biryani Cut' (CHK-BIRYANI) or 'Special Goat Biryani Cut' (MUT-BIRYANI).\n"
        f"• For fitness/grilling: 'Fresh Chicken Breast Boneless' (CHK-BONELESS).\n"
        f"• For kebabs/patties: 'Fresh Chicken Keema' (CHK-KEEMA) or 'Fresh Goat Keema' (MUT-KEEMA)."
    )


def check_delivery_slots(area_or_pincode: str) -> str:
    """Checks delivery availability and estimated arrival times for a given area or pincode.

    Args:
        area_or_pincode: City area, neighborhood, or 6-digit postal code.

    Returns:
        Delivery availability, express delivery slot (temperature-controlled), and scheduled slots.
    """
    now = datetime.datetime.now()
    express_time = (now + datetime.timedelta(minutes=45)).strftime("%I:%M %p")
    slot_evening = "06:00 PM - 08:00 PM"
    slot_morning = "07:00 AM - 09:00 AM (Tomorrow Morning)"

    return (
        f"🚚 Delivery Availability for '{area_or_pincode}':\n"
        f"✅ Service Available in temperature-controlled insulated packaging (0-4°C fresh guaranteed).\n"
        f"• ⚡ Express Delivery: Arrives by ~{express_time} (in ~45 mins)\n"
        f"• 📦 Evening Slot: Today, {slot_evening}\n"
        f"• 🌅 Early Morning Fresh Catch Slot: {slot_morning}\n"
        f"Standard Delivery Fee: ₹40 (Free on orders above ₹499)."
    )


def place_meat_order(
    item_id: str,
    quantity: int,
    delivery_address: str,
    customer_name: str,
    customer_phone: str,
    delivery_slot: str = "Express (45 mins)",
) -> str:
    """Places an order for fresh chicken or mutton cuts with temperature-controlled delivery.

    Args:
        item_id: Product ID code from the catalog (e.g. 'CHK-CURRY', 'MUT-CURRY', 'CHK-BONELESS', etc.).
        quantity: Number of packs to order (minimum 1).
        delivery_address: Complete street address or apartment details.
        customer_name: Name of the customer.
        customer_phone: Phone number for delivery updates.
        delivery_slot: Preferred slot ('Express (45 mins)', 'Evening', or 'Morning').

    Returns:
        Order confirmation details with Order ID, total amount, and delivery tracking information.
    """
    item_key = item_id.strip().upper()
    if item_key not in CATALOG:
        available = ", ".join(CATALOG.keys())
        return f"Error: Item code '{item_id}' not found. Please choose from: {available}"

    if quantity <= 0:
        return "Error: Quantity must be at least 1."

    product = CATALOG[item_key]
    if product["stock"] < quantity:
        return f"Apologies, only {product['stock']} units of {product['name']} currently in stock."

    # Update stock in memory
    product["stock"] -= quantity

    item_total = product["price"] * quantity
    delivery_fee = 0.0 if item_total >= 499.0 else 40.0
    total_amount = item_total + delivery_fee

    order_id = f"MEAT-{uuid.uuid4().hex[:6].upper()}"
    order_record = {
        "order_id": order_id,
        "product_id": item_key,
        "product_name": product["name"],
        "weight_per_pack": product["weight"],
        "quantity": quantity,
        "item_total": item_total,
        "delivery_fee": delivery_fee,
        "total_amount": total_amount,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "delivery_address": delivery_address,
        "delivery_slot": delivery_slot,
        "status": "Confirmed & Cold-Chamber Packed",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_order(order_record)

    return (
        f"🎉 Order Confirmed Successfully!\n"
        f"----------------------------------------\n"
        f"Order ID: #{order_id}\n"
        f"Customer: {customer_name} ({customer_phone})\n"
        f"Item: {product['name']} ({product['weight']}) x {quantity}\n"
        f"Subtotal: ₹{item_total:.2f}\n"
        f"Delivery Fee: ₹{delivery_fee:.2f} ({'FREE' if delivery_fee == 0 else 'Standard'})\n"
        f"Grand Total: ₹{total_amount:.2f} (Pay on Delivery / UPI)\n"
        f"Delivery Slot: {delivery_slot}\n"
        f"Address: {delivery_address}\n"
        f"Status: Cold-Chamber Packed (0-4°C fresh guaranteed)\n"
        f"----------------------------------------\n"
        f"You can track this order anytime with track_order_status('{order_id}')."
    )


def track_order_status(order_id: str) -> str:
    """Tracks the live preparation and delivery status of an existing order.

    Args:
        order_id: The order ID returned during order placement (e.g., 'MEAT-A1B2C3').

    Returns:
        Live status and details of the order.
    """
    clean_id = order_id.strip().upper()
    if not clean_id.startswith("MEAT-") and not clean_id.startswith("#MEAT-"):
        clean_id = f"MEAT-{clean_id}"
    clean_id = clean_id.lstrip("#")

    order = get_order(clean_id)
    if not order:
        # Also check if user entered partial hex
        all_orders = load_orders()
        for k, v in all_orders.items():
            if clean_id in k or k.endswith(clean_id):
                order = v
                break

    if not order:
        return f"Order '{order_id}' not found. Please check your order ID."

    return (
        f"📦 Order Status for #{order['order_id']}:\n"
        f"• Status: {order['status']}\n"
        f"• Items: {order['product_name']} x {order['quantity']}\n"
        f"• Delivery Slot: {order['delivery_slot']}\n"
        f"• Delivery To: {order['delivery_address']}\n"
        f"• Total: ₹{order['total_amount']:.2f}\n"
        f"• Ordered at: {order.get('timestamp', 'Recent')}"
    )
