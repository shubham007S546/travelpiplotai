from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ResolvedPlace(BaseModel):
    """Represents a validated, geocoded real-world location."""
    input_name: str = Field(..., description="Original user input location query")
    normalized_name: Optional[str] = Field(default=None, description="Normalized lowercase trimmed query")
    canonical_name: str = Field(..., description="Standardized official place name")
    latitude: Optional[float] = Field(default=None, description="Geographic latitude")
    longitude: Optional[float] = Field(default=None, description="Geographic longitude")
    city: Optional[str] = Field(default=None, description="City or urban local body name")
    district: Optional[str] = Field(default=None, description="Administrative district / county")
    state: Optional[str] = Field(default=None, description="State or province")
    country: Optional[str] = Field(default="India", description="Country name")
    place_id: Optional[str] = Field(default=None, description="OSM ID, geocode ID, or official place ID")
    provider_place_id: Optional[str] = Field(default=None, description="Raw provider place identifier")
    provider: str = Field(default="Open-Meteo / Nominatim", description="External geocoding service")
    source: str = Field(default="Open-Meteo / Nominatim Geocoding", description="Provider source description")
    source_url: Optional[str] = Field(default="https://geocoding-api.open-meteo.com", description="Verification URL")
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of resolution"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Resolution confidence score")
    ambiguity: bool = Field(default=False, description="True if multiple candidate locations matched")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Candidate locations if ambiguous")
    is_rural: bool = Field(default=False, description="True if location is a village, hamlet, or small locality")
    rural_urban: Optional[str] = Field(default=None, description="'rural' or 'urban'")
    place_type: str = Field(default="locality", description="village, town, city, suburb, hamlet, locality, temple, peak")
    is_trek_destination: bool = Field(default=False, description="True if destination requires hiking/trekking from road-head")
    road_head_hub: Optional[str] = Field(default=None, description="Nearest road-head transit hub where vehicles stop")
    trek_distance_km: Optional[float] = Field(default=None, description="Distance of mountain trail/trek in km from road-head")

    def model_post_init(self, __context: Any) -> None:
        if not self.normalized_name and self.input_name:
            self.normalized_name = self.input_name.strip().lower()
        if not self.provider_place_id and self.place_id:
            self.provider_place_id = str(self.place_id)
        if not self.place_id and self.provider_place_id:
            self.place_id = str(self.provider_place_id)
        if not self.provider and self.source:
            self.provider = self.source
        if self.rural_urban is None:
            self.rural_urban = "rural" if self.is_rural else "urban"
        elif self.rural_urban == "rural":
            self.is_rural = True
        elif self.rural_urban == "urban":
            self.is_rural = False

    @property
    def is_valid(self) -> bool:
        """Validates that coordinates exist and confidence passes minimum threshold."""
        return (
            self.latitude is not None and
            self.longitude is not None and
            self.confidence >= 0.85
        )

    def display_label(self) -> str:
        parts = [self.canonical_name]
        if self.district and self.district.lower() != self.canonical_name.lower():
            parts.append(self.district)
        if self.state:
            parts.append(self.state)
        return ", ".join(parts)

