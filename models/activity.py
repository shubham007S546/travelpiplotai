"""Activities, Dining, and Essential Safety Services Models."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from models.evidence import Evidence


class ActivityCategory(str, Enum):
    VIEWPOINT = "viewpoint"
    HERITAGE = "heritage"
    TEMPLE = "temple"
    MUSEUM = "museum"
    NATURE = "nature"
    TREKKING = "trekking"
    CULTURAL = "cultural"
    MARKET = "market"
    ADVENTURE = "adventure"
    FREE = "free_activity"


from datetime import datetime, timezone


class ActivityOption(BaseModel):
    """Structured tourist attraction or activity."""
    id: str
    name: str
    category: ActivityCategory = Field(default=ActivityCategory.HERITAGE)
    location: str
    latitude: Optional[float] = Field(default=None, description="Geographic latitude")
    longitude: Optional[float] = Field(default=None, description="Geographic longitude")
    cost: Optional[float] = Field(default=None, description="Entry fee per person (null if unverified)")
    admission_fee_status: str = Field(default="UNKNOWN", description="VERIFIED, FREE, UNKNOWN")
    currency: str = Field(default="INR")
    rating: float = Field(default=4.0, ge=0.0, le=5.0)
    opening_time: str = Field(default="09:00", description="HH:MM (24h)")
    closing_time: str = Field(default="18:00", description="HH:MM (24h)")
    duration_mins: int = Field(default=90, description="Estimated time spent at venue")
    distance_from_prev_km: float = Field(default=0.0)
    source: str = Field(default="OpenStreetMap / Tourism Directory")
    source_url: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence: Optional[Evidence] = None

    @property
    def cost_safe(self) -> float:
        """Safe cost accessor: returns float cost or 0.0 when unverified."""
        return self.cost if self.cost is not None else 0.0


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class FoodOption(BaseModel):
    """Dining recommendation optimized around itinerary locations."""
    id: str
    name: str
    meal_type: MealType
    cuisine: str
    price_level: str = Field(default="cheap", description="cheap / medium / premium")
    cost_estimate: Optional[float] = Field(default=None, description="Estimated meal cost per person (null if unsourced)")
    price_status: str = Field(default="UNKNOWN", description="SOURCED, UNKNOWN")
    currency: str = Field(default="INR")
    rating: float = Field(default=4.0, ge=0.0, le=5.0)
    location: str
    latitude: Optional[float] = Field(default=None, description="Geographic latitude")
    longitude: Optional[float] = Field(default=None, description="Geographic longitude")
    dietary_info: str = Field(default="Vegetarian / Non-Vegetarian")
    opening_hours: str = Field(default="08:00 - 22:00")
    source: str = Field(default="OpenStreetMap / Local Dining Directory")
    source_url: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence: Evidence

    @property
    def cost_estimate_safe(self) -> float:
        """Safe cost accessor returning float or 0.0."""
        return self.cost_estimate if self.cost_estimate is not None else 0.0



class ServiceType(str, Enum):
    HOSPITAL = "hospital"
    PHARMACY = "pharmacy"
    POLICE = "police"
    ATM = "atm"
    BANK = "bank"
    PETROL_PUMP = "petrol_pump"
    BUS_STATION = "bus_station"
    RAILWAY_STATION = "railway_station"
    AIRPORT = "airport"
    TOURIST_INFO = "tourist_info"
    EMERGENCY = "emergency"


class EssentialService(BaseModel):
    """Verified safety and essential service near destination or stay."""
    id: str
    name: str
    service_type: ServiceType
    address: str
    distance_km: float = Field(default=0.0)
    phone: Optional[str] = None
    is_24x7: bool = Field(default=False)
    opening_status: str = Field(default="Open")
    evidence: Evidence
