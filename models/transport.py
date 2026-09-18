"""Transport and Mobility Data Models with Grounded Verification."""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from models.evidence import Evidence, SourceTier


class TransportType(str, Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    TAXI = "taxi"
    SHARED_TAXI = "shared_taxi"
    AUTO_RICKSHAW = "auto_rickshaw"
    E_RICKSHAW = "e_rickshaw"
    BIKE_RENTAL = "bike_rental"
    METRO = "metro"
    WALKING = "walking"
    CYCLING = "cycling"


class FareType(str, Enum):
    LIVE = "LIVE"
    OFFICIAL_TARIFF = "OFFICIAL_TARIFF"
    PROVIDER_QUOTE = "PROVIDER_QUOTE"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class FareModelType(str, Enum):
    DISTANCE_BASED = "DISTANCE_BASED"
    ZONE_BASED = "ZONE_BASED"
    ROUTE_BASED = "ROUTE_BASED"
    FIXED = "FIXED"
    METERED = "METERED"
    DYNAMIC = "DYNAMIC"
    CLASS_BASED = "CLASS_BASED"
    UNKNOWN = "UNKNOWN"


class EstimatedFareDetails(BaseModel):
    """Authoritative gazette / tariff formula breakdown (Section 5 requirement)."""
    tariff_name: str = Field(..., description="Official name of tariff notice")
    tariff_source: str = Field(..., description="Issuing transport authority or gazette notification")
    tariff_url: Optional[str] = Field(default=None, description="Official portal or gazette URL")
    tariff_effective_date: str = Field(default="2023-08-01", description="Date tariff came into legal effect")
    vehicle_type: str = Field(default="Ordinary Stage Carriage", description="Vehicle type / service class")
    base_fare: float = Field(default=0.0, ge=0.0)
    per_km_rate: float = Field(default=0.0, ge=0.0)
    road_distance_km: float = Field(default=0.0, ge=0.0)
    calculation: str = Field(..., description="Deterministic formula breakdown")
    resulting_fare: float = Field(..., ge=0.0)
    applicable_region: str = Field(default="Regional / State", description="Jurisdiction")
    applicable_service: str = Field(default="Point-to-Point / Stage Carriage", description="Service category")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)


class TransportOption(BaseModel):
    """Represents a validated transit option between two locations."""
    @model_validator(mode="before")
    @classmethod
    def map_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "transport_type" in data and "mode" not in data:
                data["mode"] = data["transport_type"]
            if "departure_time" in data and "departure" not in data:
                data["departure"] = data["departure_time"]
            if "arrival_time" in data and "arrival" not in data:
                data["arrival"] = data["arrival_time"]
            if "duration_mins" in data and "duration" not in data:
                data["duration"] = data["duration_mins"]
            if "price" in data and "fare" not in data:
                data["fare"] = data["price"]
        return data

    id: str = Field(..., description="Unique transit identifier")
    mode: TransportType = Field(..., description="Mode of transport")
    provider: str = Field(..., description="Operating company or agency (e.g. HRTC, Indian Railways)")
    provider_id: Optional[str] = Field(default=None, description="Official provider or agency ID")
    origin: str = Field(..., description="Departure locality/station")
    destination: str = Field(..., description="Arrival locality/station")
    actual_stop: Optional[str] = Field(default=None, description="Physical bus stand, railway station, or hub name")
    departure: str = Field(..., description="HH:MM (24h) or ISO datetime")
    arrival: str = Field(..., description="HH:MM (24h) or ISO datetime")
    duration: int = Field(..., description="Total journey time in minutes")
    distance_km: float = Field(default=0.0, description="Verified road distance in km")
    fare: Optional[float] = Field(default=None, description="Verified fare per traveler (null if unavailable)")
    currency: str = Field(default="INR")
    fare_type: str = Field(default=FareType.UNKNOWN.value, description="LIVE, OFFICIAL_TARIFF, PROVIDER_QUOTE, ESTIMATED, UNKNOWN")
    booking_url: Optional[str] = Field(default=None, description="Direct booking or official schedule URL")
    source_url: Optional[str] = Field(default=None, description="Source URL where data was fetched")
    source_type: str = Field(default="Official Transit Feed", description="API, Schedule, Tariff, Map")
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verified: bool = Field(default=True, description="True if passes verification gate")
    verification_score: float = Field(default=1.0, ge=0.0, le=1.0)
    estimated: bool = Field(default=False, description="True if fare is calculated via tariff formula")
    availability_status: str = Field(default="AVAILABLE", description="AVAILABLE, UNVERIFIED, NOT_APPLICABLE")

    # Multi-leg transit support (Village-to-Village hub-and-spoke)
    is_multi_leg: bool = Field(default=False, description="True if journey requires transfers between hubs")
    legs: List["TransportOption"] = Field(default_factory=list, description="Sub-legs for multi-hop routes")

    # Transparency breakdown payloads
    fare_model_details: Optional[Dict[str, Any]] = Field(default=None, description="Detailed tariff breakdown for 'Why this fare?'")
    estimated_fare_breakdown: Optional[EstimatedFareDetails] = Field(default=None, description="Structured tariff proof")
    route_details: Optional[Dict[str, Any]] = Field(default=None, description="Route specifics and alternative comparison for 'Why this route?'")

    # Evidence and telemetry
    evidence: Optional[Evidence] = Field(default=None, description="External verifiable evidence")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Backward-compatible accessors
    @property
    def price(self) -> float:
        """Compatibility accessor returning float fare or 0.0 when unavailable."""
        return self.fare if self.fare is not None else 0.0

    @property
    def transport_type(self) -> TransportType:
        return self.mode

    @property
    def departure_time(self) -> str:
        return self.departure

    @property
    def arrival_time(self) -> str:
        return self.arrival

    @property
    def duration_mins(self) -> int:
        return self.duration

    @property
    def is_estimated(self) -> bool:
        return self.estimated

    @property
    def data_timestamp(self) -> str:
        return self.retrieved_at


class LocalMobilityRecommendation(BaseModel):
    """Trade-off recommendation for moving within a locality between itinerary stops."""
    from_location: str
    to_location: str
    distance_km: float
    recommended_mode: TransportType
    price: float
    duration_mins: int
    tradeoff_reasoning: str = Field(
        ..., description="e.g. 'Take the bus because it saves ₹130 with only 3 extra minutes compared to taxi.'"
    )
    alternative_options: List[TransportOption] = Field(default_factory=list)
    evidence: Evidence
