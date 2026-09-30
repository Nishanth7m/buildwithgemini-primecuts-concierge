"""Public recipe API tool for PrimeCuts Agent using TheMealDB.

Fetches real authentic culinary recipes, ingredient proportions, and cooking
instructions from the free public TheMealDB API.
"""

import os
import urllib.parse
import urllib.request
import json


def lookup_authentic_recipe(dish_name: str) -> str:
    """Searches a free public culinary database (TheMealDB) for real recipes, authentic ingredient measurements, and cooking steps.

    Args:
        dish_name: The name or keyword of the dish (e.g. 'biryani', 'curry', 'tandoori', 'korma', 'stew', 'chicken').

    Returns:
        Structured culinary details including dish origin, ingredients list with measurements, and step-by-step instructions.
    """
    api_key = os.getenv("MEALDB_API_KEY", "1")  # Default public free tier key is '1'
    query = urllib.parse.quote(dish_name.strip())
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PrimeCutsAgent/1.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode())

        meals = data.get("meals")
        if not meals:
            return f"No verified recipe found in the public recipe database for '{dish_name}'. You can try broader keywords like 'biryani', 'chicken', 'lamb', or 'curry'."

        meal = meals[0]  # Take the top match
        name = meal.get("strMeal")
        category = meal.get("strCategory", "Meat Dish")
        cuisine = meal.get("strArea", "Culinary")
        instructions = meal.get("strInstructions", "").strip()

        # Extract ingredients and measurements
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                measure_str = f" ({measure.strip()})" if measure and measure.strip() else ""
                ingredients.append(f"  • {ing.strip()}{measure_str}")

        ingredients_text = "\n".join(ingredients) if ingredients else "  • Standard meat and whole spices"
        
        # Summarize instructions if excessively long
        formatted_instructions = instructions if len(instructions) <= 900 else instructions[:900] + "...\n(Full traditional method continues)"

        return (
            f"🍳 Authentic Recipe: **{name}**\n"
            f"• Cuisine & Style: {cuisine} ({category})\n\n"
            f"📋 Required Ingredients & Quantities:\n"
            f"{ingredients_text}\n\n"
            f"👨‍🍳 Chef's Cooking Instructions:\n"
            f"{formatted_instructions}"
        )
    except Exception as e:
        return f"Error retrieving recipe from public database: {str(e)}"
