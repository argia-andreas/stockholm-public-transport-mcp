# server.py
from datetime import datetime
from typing import Any

import pytz
import requests
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Stockholm Traffic Planner")

BASE_URL = "https://journeyplanner.integration.sl.se/v2"


def _convert_utc_to_stockholm(utc_time_str: str) -> str:
    """Convert UTC time string to Stockholm local time"""
    if not utc_time_str:
        return ""

    try:
        # Parse UTC time (format: "2025-07-05T11:18:00Z")
        utc_time = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))

        # Convert to Stockholm timezone
        stockholm_tz = pytz.timezone("Europe/Stockholm")
        stockholm_time = utc_time.astimezone(stockholm_tz)

        # Return in readable format
        return stockholm_time.strftime("%H:%M")
    except Exception:
        return utc_time_str


def _get_best_time(leg_data: dict[str, Any], time_type: str) -> str:
    """Get the best available time (real-time if available, otherwise planned)"""
    estimated_key = f"{time_type}TimeEstimated"
    planned_key = f"{time_type}TimePlanned"

    estimated_time = leg_data.get(estimated_key)
    planned_time = leg_data.get(planned_key)

    # Prefer real-time (estimated) over planned time
    return _convert_utc_to_stockholm(estimated_time or planned_time)


def _simplify_journey_response(data: dict[str, Any]) -> dict[str, Any]:
    """Simplify the complex journey response to essential information"""
    simplified = {"journeys": [], "system_messages": data.get("systemMessages", [])}

    for journey in data.get("journeys", []):
        simple_journey = {
            "duration_minutes": journey.get("tripDuration", 0) // 60,
            "interchanges": journey.get("interchanges", 0),
            "legs": [],
        }

        for leg in journey.get("legs", []):
            # Get best available times (real-time preferred)
            origin_data = leg.get("origin", {})
            destination_data = leg.get("destination", {})

            # Check both 'product' and 'transportation' for transport info
            product_info = leg.get("product", {})
            transportation_info = leg.get("transportation", {})

            # Extract transport details from the correct source
            if transportation_info:
                transport_type = transportation_info.get("product", {}).get(
                    "name", "Walk"
                )
                line = transportation_info.get("number", "")
                direction = transportation_info.get("direction", "")
            else:
                transport_type = product_info.get("name", "Walk")
                line = product_info.get("line", "")
                direction = product_info.get("direction", "")

            simple_leg = {
                "origin": origin_data.get("name", "Unknown"),
                "destination": destination_data.get("name", "Unknown"),
                "departure_time": _get_best_time(origin_data, "departure"),
                "arrival_time": _get_best_time(destination_data, "arrival"),
                "transport_type": transport_type,
                "line": line,
                "direction": direction,
                "duration_minutes": leg.get("duration", 0) // 60,
            }
            simple_journey["legs"].append(simple_leg)

        simplified["journeys"].append(simple_journey)

    return simplified


@mcp.tool()
def stop_lookup(name: str) -> list[dict[str, Any]]:
    """Look up stops/stations by name in Stockholm public transport system.

    IMPORTANT: Use this tool FIRST to get stop IDs before calling plan_journey.
    The journey planner requires exact stop IDs, not names.

    Args:
        name: Name of the stop/station to search for

    Returns:
        List of matching stops with their IDs, names, and coordinates
    """
    try:
        url = f"{BASE_URL}/stop-finder"
        params = {"name_sf": name, "any_obj_filter_sf": 2, "type_sf": "any"}

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Simplify the response to key information
        simplified_locations = []
        for location in data.get("locations", []):
            simplified_locations.append(
                {
                    "id": location.get("id"),
                    "name": location.get("name"),
                    "coordinates": location.get("coord", []),
                    "match_quality": location.get("matchQuality", 0),
                    "is_best_match": location.get("isBest", False),
                }
            )

        return simplified_locations
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def plan_journey(
    origin_id: str,
    destination_id: str,
    trips: int = 3,
    exclude_walking: bool = True,
    exclude_transport_types: list[str] = None,
    departure_time: str = None,
    max_walking_distance: int = 500,
) -> dict[str, Any]:
    """Plan a journey between two stops in Stockholm public transport system.

    WORKFLOW:
    1. First use stop_lookup() to find the origin stop ID
    2. Then use stop_lookup() to find the destination stop ID
    3. Finally use this tool with the exact stop IDs

    Args:
        origin_id: Origin stop ID (get from stop_lookup tool)
        destination_id: Destination stop ID (get from stop_lookup tool)
        trips: Number of alternative trips to return (default: 3)
        exclude_walking: Whether to exclude walking-only routes (default: True)
        exclude_transport_types: List of transport types to exclude: ['bus', 'metro', 'train', 'tram', 'ship'] (default: None)
        departure_time: Departure time in HH:MM format (default: now)
        max_walking_distance: Maximum walking distance in meters (default: 500)

    Returns:
        Simplified journey information with times, transport types, and transfers
    """
    try:
        url = f"{BASE_URL}/trips"
        params = {
            "type_origin": "any",
            "type_destination": "any",
            "name_origin": origin_id,
            "name_destination": destination_id,
            "calc_number_of_trips": trips,
            "maxWalkingDistanceOrigin": max_walking_distance,
            "maxWalkingDistanceDestination": max_walking_distance,
        }

        # Handle excluded transport types
        excluded_means = 0
        if exclude_walking:
            excluded_means |= 32  # Walking bit

        if exclude_transport_types:
            transport_map = {"bus": 1, "metro": 2, "train": 4, "tram": 8, "ship": 16}
            for transport in exclude_transport_types:
                if transport.lower() in transport_map:
                    excluded_means |= transport_map[transport.lower()]

        if excluded_means > 0:
            params["excludedMeans"] = excluded_means

        # Handle departure time
        if departure_time:
            try:
                # Parse HH:MM format and use today's date
                time_parts = departure_time.split(":")
                if len(time_parts) == 2:
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    now = datetime.now()
                    params["date"] = now.strftime("%Y-%m-%d")
                    params["time"] = f"{hour:02d}:{minute:02d}"
            except ValueError:
                pass  # Use current time if parsing fails

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Return simplified response
        return _simplify_journey_response(data)
    except Exception as e:
        return {"error": str(e)}
