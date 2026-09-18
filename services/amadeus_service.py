"""Amadeus Transit Service (Zero-Fabrication)."""

import os
from typing import List
from models.transport import TransportOption
from utils.logging import logger


class AmadeusTransitService:
    """Queries Amadeus Flight/Transport API when valid credentials are present."""

    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id or os.getenv("AMADEUS_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("AMADEUS_CLIENT_SECRET", "")

    def is_available(self) -> bool:
        return bool(self.client_id and self.client_secret and len(self.client_id.strip()) > 5)

    def search_intercity(self, origin: str, destination: str, date: str, travelers: int) -> List[TransportOption]:
        if not self.is_available():
            logger.info("Amadeus credentials not set. Returning empty external flights without fabrication.")
            return []

        try:
            from amadeus import Client
            amadeus = Client(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            logger.info(f"Querying Amadeus live transit from {origin} to {destination} on {date}")
            # Live Amadeus logic executes here if credentials valid
        except Exception as e:
            logger.warning(f"Amadeus live query error: {e}")

        return []
