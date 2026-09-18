"""LangGraph State and Reducer definitions."""

from typing import Dict, Any
from models.travel_state import TravelState


def create_initial_state(user_query: str = "") -> TravelState:
    """Initializes empty typed state with clean defaults."""
    return TravelState(
        user_query=user_query,
        source="Mandi",
        destination="Shimla",
        start_date="2026-10-01",
        end_date="2026-10-02",
        duration_days=2,
        travelers=1,
        budget=3000.0,
        currency="INR",
        travel_style="budget",
        transport_preference="cheapest practical",
        accommodation_preference="budget",
        food_preference="local",
        interests=["viewpoints", "heritage", "local markets"],
        inferred_fields=[],
        outbound_transport_options=[],
        return_transport_options=[],
        selected_outbound_transport=None,
        selected_return_transport=None,
        hotel_options=[],
        selected_hotel=None,
        food_options=[],
        selected_food=[],
        activity_options=[],
        selected_activities=[],
        local_mobility_options=[],
        essential_services=[],
        weather=None,
        itinerary=[],
        budget_breakdown=None,
        evidence_ledger=[],
        verification_results=None,
        api_audit_log=[],
        live_audit_summary={},
        disruption_alerts=[],
        has_disruption_risk=False,
        recommended_reroute=None,
        replanning_count=0,
        max_replanning_attempts=3,
        agent_logs=[],
        final_response="",
        execution_status="in_progress"
    )

