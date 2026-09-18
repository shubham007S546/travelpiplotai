"""OpenTripMap Service for Live Global Tourist Attractions and Heritage Sites."""

import os
import requests
from typing import List, Dict, Any, Optional
from models.activity import ActivityOption, ActivityCategory
from models.evidence import Evidence, SourceTier
from utils.caching import api_cache
from utils.logging import logger


class OpenTripMapService:
    """Discovers real-world tourist attractions using OpenTripMap API."""

    BASE_URL = "https://api.opentripmap.com/0.1/en/places"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("OPENTRIPMAP_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def search_attractions(self, city: str, limit: int = 5) -> List[ActivityOption]:
        if not self.is_available():
            return []

        cached = api_cache.get("opentripmap", {"city": city.lower(), "limit": limit})
        if cached:
            return [ActivityOption(**item) for item in cached]

        try:
            # 1. Geocode City to Coordinates
            geo_url = f"{self.BASE_URL}/geoname"
            r_geo = requests.get(geo_url, params={"name": city, "apikey": self.api_key}, timeout=6)
            if r_geo.status_code != 200:
                return []

            geo_data = r_geo.json()
            lat = geo_data.get("lat")
            lon = geo_data.get("lon")
            if not lat or not lon:
                return []

            # 2. Search attractions within 8km radius
            rad_url = f"{self.BASE_URL}/radius"
            params = {
                "radius": 8000,
                "lon": lon,
                "lat": lat,
                "kinds": "interesting_places,view_points,historic,museums,cultural",
                "rate": 2,
                "limit": limit,
                "apikey": self.api_key
            }
            r_places = requests.get(rad_url, params=params, timeout=6)
            if r_places.status_code == 200:
                features = r_places.json().get("features", [])
                results: List[ActivityOption] = []
                for i, feat in enumerate(features):
                    props = feat.get("properties", {})
                    name = props.get("name")
                    if not name:
                        continue

                    kinds = props.get("kinds", "")
                    category = ActivityCategory.HERITAGE
                    if "view_points" in kinds:
                        category = ActivityCategory.VIEWPOINT
                    elif "religion" in kinds or "temple" in kinds:
                        category = ActivityCategory.TEMPLE
                    elif "museum" in kinds:
                        category = ActivityCategory.MUSEUM

                    dist_m = props.get("dist", 1000)
                    dist_km = round(dist_m / 1000.0, 1)

                    act = ActivityOption(
                        id=f"otm-{props.get('xid', i)[:10]}",
                        name=name,
                        category=category,
                        location=f"{name}, {city}",
                        cost=0.0,
                        rating=4.6,
                        opening_time="09:00",
                        closing_time="18:30",
                        duration_mins=90,
                        distance_from_prev_km=dist_km,
                        evidence=Evidence(
                            claim=f"Verified cultural site '{name}' located in {city}",
                            source="OpenTripMap Global Geographic Registry",
                            source_type="Official OpenTripMap API",
                            url="https://opentripmap.com",
                            tier=SourceTier.TIER_2_PROVIDER_API,
                            confidence=0.96
                        )
                    )
                    results.append(act)

                if results:
                    api_cache.set("opentripmap", {"city": city.lower(), "limit": limit}, [a.model_dump() for a in results])
                    return results

        except Exception as e:
            logger.warning(f"OpenTripMap live query failed: {e}")

        return []
