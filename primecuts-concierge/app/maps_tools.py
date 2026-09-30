"""Google Maps Geocoding and Places API (New) function tools for PrimeCuts Agent.

Uses direct REST calls using standard library urllib.
Reads GOOGLE_MAPS_API_KEY from environment variables.
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Optional


def _get_api_key() -> str:
    return os.getenv("GOOGLE_MAPS_API_KEY", "").strip()


def geocode_address(address: str) -> str:
    """Converts a human-readable street address into geographic latitude/longitude coordinates using Google Maps Geocoding API.

    Args:
        address: Delivery address or landmark (e.g. '42 MG Road, Koramangala, Bengaluru').

    Returns:
        Structured location details including formatted address, latitude, and longitude.
    """
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Google Maps API key is not configured. Please set GOOGLE_MAPS_API_KEY in .env."

    encoded_address = urllib.parse.quote(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PrimeCutsAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        status = data.get("status")
        if status != "OK":
            err_msg = data.get("error_message", status)
            return f"Geocoding failed for '{address}': {err_msg}"

        results = data.get("results", [])
        if not results:
            return f"No geocoding results found for address: '{address}'"

        first = results[0]
        formatted = first.get("formatted_address")
        location = first.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return (
            f"📍 Geocoding Result:\n"
            f"• Formatted Address: {formatted}\n"
            f"• Latitude: {lat}\n"
            f"• Longitude: {lng}"
        )
    except Exception as e:
        return f"Error connecting to Geocoding API: {str(e)}"


def find_nearby_places(latitude: float, longitude: float, place_type: str = "restaurant", radius_meters: float = 2000.0) -> str:
    """Finds nearby places of a specific type around geographic coordinates using Google Places API (New) Nearby Search.

    Args:
        latitude: Latitude coordinate (e.g. 12.9352).
        longitude: Longitude coordinate (e.g. 77.6245).
        place_type: Type of place to search for (e.g. 'restaurant', 'supermarket', 'butcher_shop', 'meal_takeaway').
        radius_meters: Search radius in meters (default 2000 meters / 2km).

    Returns:
        List of nearby matching places with name, formatted address, and coordinates.
    """
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Google Maps API key is not configured. Please set GOOGLE_MAPS_API_KEY in .env."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
    }

    body = {
        "includedTypes": [place_type.strip().lower()],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        lines = [f"🏢 Nearby Places ({place_type.title()}):"]
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown Place")
            addr = p.get("formattedAddress", "Address unavailable")
            loc = p.get("location", {})
            p_lat = loc.get("latitude")
            p_lng = loc.get("longitude")
            lines.append(f"• **{name}**\n  Address: {addr}\n  Coordinates: ({p_lat}, {p_lng})")

        return "\n\n".join(lines)
    except Exception as e:
        return f"Error connecting to Places API (New): {str(e)}"
