"""Accommodation and Lodging Models."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from models.evidence import Evidence


class StayType(str, Enum):
    HOTEL = "hotel"
    HOSTEL = "hostel"
    HOMESTAY = "homestay"
    GUESTHOUSE = "guesthouse"
    PG = "pg"
    RESORT = "resort"
    DORMITORY = "dormitory"
    CAMP = "camp"
    CAMPSITE = "campsite"
    TENT_RENTAL = "tent_rental"


class StayOption(BaseModel):
    """Structured accommodation option grounded in verifiable rates."""
    id: str = Field(..., description="Unique stay identifier")
    name: str = Field(..., description="Property name")
    stay_type: StayType = Field(default=StayType.HOTEL)
    address: str
    city: str
    latitude: Optional[float] = Field(default=None, description="Geographic latitude")
    longitude: Optional[float] = Field(default=None, description="Geographic longitude")
    price_per_night: Optional[float] = Field(default=None, ge=0.0, description="Rate per night per room (null if unavailable)")
    total_price: Optional[float] = Field(default=None, ge=0.0, description="Total stay cost for all nights (null if unavailable)")
    currency: str = Field(default="INR")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Rating out of 5")
    reviews_count: int = Field(default=0, ge=0)
    distance_to_center_km: float = Field(default=0.0, ge=0.0)
    amenities: List[str] = Field(default_factory=list)
    check_in_time: str = Field(default="12:00")
    check_out_time: str = Field(default="11:00")
    booking_url: Optional[str] = None
    source_url: Optional[str] = Field(default=None, description="Direct URL or booking portal link")
    image_url: Optional[str] = Field(default=None, description="Verified property photo from hotel listing")
    room_type: str = Field(default="Standard Room", description="Room classification")
    number_of_rooms: int = Field(default=1, ge=1, description="Quantity of rooms requested")
    availability_status: str = Field(default="AVAILABLE", description="AVAILABLE, UNVERIFIED, NOT_APPLICABLE")
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_available: bool = Field(default=True)
    is_camping: bool = Field(default=False, description="True if accommodation is a campsite, camp or tent rental")
    gear_included: List[str] = Field(default_factory=list, description="Camping equipment included (e.g. dome tent, sleeping bag)")
    pitch_fee: Optional[float] = Field(default=None, description="Base ground pitch fee if bringing own tent")
    source: str = Field(default="SerpApi / Google Hotels", description="Data provenance source")
    evidence: Optional[Evidence] = None

    @property
    def price_per_night_safe(self) -> float:
        """Safe fallback for arithmetic: returns float or 0.0."""
        return self.price_per_night if self.price_per_night is not None else 0.0

