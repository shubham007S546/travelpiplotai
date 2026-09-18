"""TravelState definition and telemetry models for LangGraph multi-agent flow."""

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from models.evidence import Evidence
from models.place import ResolvedPlace
from models.transport import TransportOption, LocalMobilityRecommendation
from models.accommodation import StayOption
from models.activity import ActivityOption, FoodOption, EssentialService
from models.budget import BudgetBreakdown
from models.ground_reality import GroundRealityCheck


class AgentTelemetry(BaseModel):
    """Execution telemetry captured for each agent in the graph."""
    agent_name: str
    status: str = Field(default="completed", description="completed / warning / failed")
    start_time: str
    end_time: str
    duration_ms: float
    input_summary: str
    tool_calls: List[str] = Field(default_factory=list)
    output_summary: str
    errors: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class VerificationFailure(BaseModel):
    """Structured record of a single constraint failure."""
    failure_reason: str
    affected_component: str
    severity: str = Field(default="high", description="critical / high / medium / low")
    recommended_action: str


class VerificationResult(BaseModel):
    """Comprehensive multi-dimensional evaluation results."""
    verification_score: float = Field(default=100.0, ge=0.0, le=100.0)
    grounding_score: float = Field(default=100.0, ge=0.0, le=100.0)
    constraint_score: float = Field(default=100.0, ge=0.0, le=100.0)
    budget_score: float = Field(default=100.0, ge=0.0, le=100.0)
    temporal_score: float = Field(default=100.0, ge=0.0, le=100.0)
    spatial_score: float = Field(default=100.0, ge=0.0, le=100.0)
    overall_confidence: float = Field(default=95.0, ge=0.0, le=100.0)
    passed: bool = Field(default=True)
    failure_reasons: List[VerificationFailure] = Field(default_factory=list)
    checked_at: str = Field(default="")


class ItineraryItem(BaseModel):
    """A scheduled event block in the daily itinerary."""
    id: str
    day_number: int
    start_time: str = Field(..., description="HH:MM (24h)")
    end_time: str = Field(..., description="HH:MM (24h)")
    title: str
    item_type: str = Field(..., description="travel / checkin / dining / attraction / local_transit / leisure")
    location: str
    duration_mins: int
    travel_time_from_prev_mins: int = 0
    transport_mode: Optional[str] = None
    estimated_cost: float = Field(default=0.0, ge=0.0)
    currency: str = Field(default="INR")
    notes: Optional[str] = None
    evidence: Optional[Evidence] = None


class ItineraryDay(BaseModel):
    """Day schedule in the trip."""
    day_number: int
    date_str: str = ""
    theme: str = ""
    items: List[ItineraryItem] = Field(default_factory=list)
    daily_cost: float = 0.0


class WeatherForecast(BaseModel):
    """Destination weather summary."""
    location: str
    temperature_c: float = 20.0
    apparent_temp_c: float = 20.0
    condition: str = "Pleasant"
    precipitation_chance_pct: int = 10
    precipitation_mm: float = 0.0
    advisory: str = "Normal outdoor travel conditions"
    clothing_recommendation: str = "Normal comfortable clothing recommended"
    forecast_time: str = Field(default="", description="Forecast timestamp")
    weather_code: int = Field(default=0, description="WMO weather interpretation code")
    wind_speed: float = Field(default=0.0, description="Wind speed in km/h")
    wind_speed_kmh: float = Field(default=0.0, description="Wind speed in km/h")
    source: str = Field(default="Open-Meteo Live API", description="Weather provider")
    retrieved_at: str = Field(default="", description="Timestamp of retrieval")


class TravelState(TypedDict, total=False):
    """Strongly typed shared LangGraph state passed through all agents."""
    # User Input & Intent
    user_query: str
    source: str
    destination: str
    start_date: str
    end_date: str
    duration_days: int
    travelers: int
    budget: float
    currency: str
    travel_style: str
    transport_preference: str
    accommodation_preference: str
    food_preference: str
    interests: List[str]
    inferred_fields: List[str]

    # Grounded Place Resolution
    resolved_source: Optional[ResolvedPlace]
    resolved_destination: Optional[ResolvedPlace]
    rural_travel_mode: bool
    ambiguity_detected: bool
    place_selection_required: bool
    place_alternatives: Dict[str, List[Dict[str, Any]]]

    # Route & Distance Verification
    route_evidence: Optional[Dict[str, Any]]
    distance_status: str  # "CONSISTENT" or "CONFLICT"
    distance_difference_pct: float
    conflict_details: Optional[Dict[str, Any]]

    # Data Trust Breakdown
    trust_scores: Dict[str, float]  # place, route, transport, fare, hotel, weather, overall

    # External Data Options
    outbound_transport_options: List[TransportOption]
    return_transport_options: List[TransportOption]
    selected_outbound_transport: Optional[TransportOption]
    selected_return_transport: Optional[TransportOption]

    hotel_options: List[StayOption]
    selected_hotel: Optional[StayOption]

    food_options: List[FoodOption]
    selected_food: List[FoodOption]

    activity_options: List[ActivityOption]
    selected_activities: List[ActivityOption]

    local_mobility_options: List[LocalMobilityRecommendation]
    essential_services: List[EssentialService]
    weather: Optional[WeatherForecast]
    ground_reality: Optional[GroundRealityCheck]

    # Optimizations & Itinerary
    itinerary: List[ItineraryDay]
    budget_breakdown: Optional[BudgetBreakdown]

    # Evidence & Verification
    evidence_ledger: List[Evidence]
    verification_results: Optional[VerificationResult]

    # Live Data Audit Pipeline Telemetry (Section 11)
    api_audit_log: List[Dict[str, Any]]
    live_audit_summary: Dict[str, Any]

    # Proactive Trip Disruption & Hazard Alerts
    disruption_alerts: List[Dict[str, Any]]
    has_disruption_risk: bool
    recommended_reroute: Optional[str]

    # Replanning & Observability
    replanning_count: int
    max_replanning_attempts: int
    agent_logs: List[AgentTelemetry]
    final_response: str
    execution_status: str  # "in_progress", "completed", "failed", "replanning"

