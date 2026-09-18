"""Helper functions for geospatial, time, and currency operations."""

import math
from datetime import datetime, timedelta
from typing import Tuple


def haversine_distance_km(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Computes great-circle distance between two (lat, lon) coordinates in kilometers."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    r = 6371.0  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)


def add_minutes_to_time_str(time_str: str, minutes: int) -> str:
    """Adds minutes to HH:MM format string."""
    try:
        dt = datetime.strptime(time_str.strip(), "%H:%M")
        new_dt = dt + timedelta(minutes=minutes)
        return new_dt.strftime("%H:%M")
    except Exception:
        return time_str


def time_difference_minutes(start_str: str, end_str: str) -> int:
    """Calculates minutes between start and end (HH:MM)."""
    try:
        t1 = datetime.strptime(start_str.strip(), "%H:%M")
        t2 = datetime.strptime(end_str.strip(), "%H:%M")
        diff = (t2 - t1).total_seconds() / 60
        return int(diff)
    except Exception:
        return 0


def format_currency(amount: float, currency: str = "INR") -> str:
    """Formats monetary amounts with correct symbol."""
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }
    symbol = symbols.get(currency.upper(), f"{currency} ")
    return f"{symbol}{amount:,.0f}" if amount == int(amount) else f"{symbol}{amount:,.2f}"
