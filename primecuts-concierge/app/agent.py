# ruff: noqa
import os
import datetime
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.genai import types

from app.meat_tools import (
    list_fresh_cuts,
    recommend_cut_for_dish,
    check_delivery_slots,
    place_meat_order,
    track_order_status,
)
from app.firestore_tools import (
    firestore_list_cuts,
    firestore_get_cut_details,
    firestore_save_customer_preferences,
    firestore_get_customer_preferences,
)
from app.plating_visual_tool import generate_recipe_plating_visual
from app.video_tools import generate_cut_showcase_video
from app.recipe_api_tool import lookup_authentic_recipe
from app.maps_tools import geocode_address, find_nearby_places

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from app.a2ui_utils import a2ui_callback

MODEL = "gemini-2.5-flash"
SANDBOX_RESOURCE_NAME = (
    "projects/83005844745/locations/us-east1/reasoningEngines/628478647413506048/sandboxEnvironments/1437994083363586048"
)

BASE_ROLE_DESCRIPTION = """You are 'PrimeCuts Concierge', an expert AI butcher and fresh chicken & mutton delivery assistant.

You have access to persistent cross-session memory, live external culinary, location, and database tools, as well as a secure Python code execution sandbox:
- You remember user stated preferences and facts from previous conversations, especially ALLERGIES (e.g. dairy, gluten, nuts, sulfites, mustard, shellfish, specific spices) and dietary restrictions. Always check and respect previously remembered allergies and preferences when recommending recipes, marinades, or meat cuts.
- Use firestore_list_cuts and firestore_get_cut_details to query the live meat catalog and inventory from Firestore.
- Use firestore_save_customer_preferences and firestore_get_customer_preferences to store and retrieve customer dietary profiles, favorite cuts, and notes.
- Use lookup_authentic_recipe to fetch real ingredient quantities and cooking instructions from the authentic culinary recipe database when customers ask how to cook a dish or ask for a recipe.
- Use generate_recipe_plating_visual to generate a culinary plating visual card saved to Cloud Storage whenever a customer asks what a dish looks like or requests a visual preview.
- Use generate_cut_showcase_video to generate a short showcase video using the Omni model whenever a customer asks for a video of a meat cut or dish.
- Use geocode_address to verify delivery addresses and obtain exact latitude and longitude coordinates.
- Use find_nearby_places to discover partner butcher hubs, cold storage distribution centers, supermarkets, or restaurants near a location.
- You can write and execute Python code in your secure sandbox environment whenever exact calculations, nutritional breakdown totals, marinade ratios, or data analysis are needed.
- Use place_meat_order to book deliveries and track_order_status to check live orders.

Available Cuts & Product Codes:
- Chicken:
  * CHK-CURRY: Fresh Farm Chicken Curry Cut (500g, ₹180) - Curries, Korma, Stew
  * CHK-BONELESS: Fresh Chicken Breast Boneless (500g, ₹260) - Grilling, Salads, Stir-fry
  * CHK-DRUMSTICK: Chicken Drumsticks Skinless (500g, ₹220) - Tandoori, Roasting, Fried
  * CHK-BIRYANI: Premium Chicken Biryani Cut (1kg, ₹350) - Dum Biryani, Pulao
  * CHK-KEEMA: Fresh Chicken Keema Mince (450g, ₹240) - Kebabs, Keema Matar
- Mutton (Goat):
  * MUT-CURRY: Rich Goat Mutton Curry Cut (500g, ₹460) - Rogan Josh, Nihari, Gravies
  * MUT-CHOPS: Goat Ribs & Chops Chaap (500g, ₹520) - Chaap Fry, Grilling
  * MUT-BONELESS: Tender Boneless Goat Meat (500g, ₹590) - Boti Kebab, Mutton Sukka
  * MUT-KEEMA: Fresh Goat Keema Mince (450g, ₹490) - Galouti Kebab, Keema Pav
  * MUT-BIRYANI: Special Goat Biryani Cut (1kg, ₹890) - Hyderabadi / Awadhi Dum Biryani

Your responsibilities:
1. Help customers choose fresh chicken and goat mutton cuts while strictly honoring all remembered user allergies and dietary restrictions.
2. Provide culinary advice and fetch authentic recipes/ingredients using lookup_authentic_recipe.
3. Validate addresses and find nearby distribution points using Google Maps geocoding and Places tools.
4. Generate dish plating visuals for customers upon request to showcase the final presentation.
5. Check delivery slots and explain temperature-controlled fresh packaging (0-4°C, never frozen).
6. Save customer dietary goals, favorite cuts, or delivery notes in Firestore when they share them.
7. When a customer wants to place an order, match the cut to the appropriate product code. If you have the cut/product, quantity, address, name, phone, and slot, directly call place_meat_order.
8. If details like delivery address, phone, or name are missing, kindly ask the customer for them.
"""

try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )
    SYSTEM_INSTRUCTION = schema_manager.generate_system_prompt(
        role_description=BASE_ROLE_DESCRIPTION,
        workflow_description="Analyze the customer request and return structured UI when appropriate (such as showing cuts, orders, recipes, or locations).",
        ui_description=(
            "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
            "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
            "nothing in adk web). "
            "You may include one Image component, but only when you have a public https "
            "URL for the image (for example the URL an image tool returns after uploading "
            "to a public bucket). Set the Image url to that exact https link, for example "
            '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
            "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
            "not have a public URL, add a short Text line noting the image instead. "
            "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
            "headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
            "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
        ),
        include_schema=True,
        include_examples=True,
    )
except ImportError:
    prompt_path = os.path.join(os.path.dirname(__file__), "a2ui_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            SYSTEM_INSTRUCTION = f.read()
    else:
        SYSTEM_INSTRUCTION = BASE_ROLE_DESCRIPTION


async def generate_memories_callback(callback_context: CallbackContext):
    """Saves session events to Memory Bank so user facts and allergies persist across sessions."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="primecuts_delivery_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    ),
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    tools=[
        PreloadMemoryTool(),
        list_fresh_cuts,
        recommend_cut_for_dish,
        check_delivery_slots,
        place_meat_order,
        track_order_status,
        firestore_list_cuts,
        firestore_get_cut_details,
        firestore_save_customer_preferences,
        firestore_get_customer_preferences,
        generate_recipe_plating_visual,
        generate_cut_showcase_video,
        lookup_authentic_recipe,
        geocode_address,
        find_nearby_places,
    ],
)

app = App(
    root_agent=root_agent,
    name="fresh_meat_delivery_app",
)
