"""YouTube Ground-Truth Travel Vlog & Timeline Verification Service.

Fetches authentic real-world traveler video guides, parses their upload timeline,
and applies temporal tariff audit (warning users if older videos quote pre-2023 fares).
"""

import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv
from utils.caching import api_cache
from utils.logging import logger

load_dotenv()


class YouTubeTravelService:
    """Retrieves real traveler vlogs and audits their temporal freshness."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def search_travel_vlogs(
        self,
        origin: str,
        destination: str,
        topic: str = "bus fare trek guide",
        max_results: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Searches YouTube for real-world traveler guides and analyzes the upload timeline.
        """
        if not self.is_available():
            return []

        query = f"{origin} to {destination} {topic}".strip()
        cache_key = {"query": query.lower(), "max": max_results}
        cached = api_cache.get("youtube_travel_vlogs", cache_key)
        if cached:
            return cached

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "relevanceLanguage": "en",
            "key": self.api_key
        }

        videos: List[Dict[str, Any]] = []
        try:
            res = requests.get(url, params=params, timeout=6)
            if res.status_code == 200:
                data = res.json()
                current_year = datetime.now(timezone.utc).year

                for item in data.get("items", []):
                    sn = item.get("snippet", {})
                    v_id = item.get("id", {}).get("videoId")
                    if not v_id:
                        continue

                    pub_raw = sn.get("publishedAt", "")
                    pub_year = current_year
                    pub_date_formatted = "Unknown Date"
                    if pub_raw:
                        try:
                            dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
                            pub_year = dt.year
                            pub_date_formatted = dt.strftime("%b %Y")
                        except Exception:
                            pass

                    # Temporal assessment according to user's insight
                    if pub_year >= current_year - 1:
                        freshness_badge = "🟢 Recent Ground Truth"
                        fare_note = "Reflects current post-2023 HP tariff revisions & live ground conditions."
                        is_fresh = True
                    elif pub_year >= 2022:
                        freshness_badge = "🟡 Moderately Recent"
                        fare_note = f"Recorded in {pub_year}. Fares may be ~15-20% higher now following the 2023 HRTC revision."
                        is_fresh = True
                    else:
                        freshness_badge = "⚠️ Historical Reference"
                        fare_note = f"Recorded in {pub_year}. Route & trek trail remain accurate, but fares and tent rentals were lower back then."
                        is_fresh = False

                    thumbnails = sn.get("thumbnails", {})
                    thumb_url = (
                        thumbnails.get("medium", {}).get("url") or
                        thumbnails.get("default", {}).get("url") or
                        f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg"
                    )

                    videos.append({
                        "video_id": v_id,
                        "title": sn.get("title", ""),
                        "channel": sn.get("channelTitle", "Travel Vlogger"),
                        "published_at": pub_raw,
                        "published_year": pub_year,
                        "published_date_formatted": pub_date_formatted,
                        "description": sn.get("description", "")[:200],
                        "video_url": f"https://www.youtube.com/watch?v={v_id}",
                        "thumbnail_url": thumb_url,
                        "freshness_badge": freshness_badge,
                        "fare_note": fare_note,
                        "is_fresh": is_fresh
                    })

                if videos:
                    api_cache.set("youtube_travel_vlogs", cache_key, videos)
            else:
                logger.warning(f"YouTube API returned status {res.status_code}: {res.text[:200]}")
        except Exception as e:
            logger.warning(f"YouTube search error: {e}")

        return videos
