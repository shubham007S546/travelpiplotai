"""Comprehensive Model & Agent Architectural Resilience Tests.

Verifies that agents (PlaceResolutionAgent, RoutingService, TransportAgent,
ItineraryOptimizer, and FinalVerificationAgent) are fundamentally resilient to
typos, composite landmarks, regional dialects, and network API timeouts without
cascading into 0% failure states or dummy free transit.
"""

import pytest
from agents.place_resolution_agent import PlaceResolutionAgent
from agents.intent_agent import IntentAgent
from services.routing_service import RoutingService
from services.transport_verification import TransportVerificationPipeline
from agents.transport_agent import TransportAgent
from optimization.itinerary_optimizer import ItineraryOptimizer
from orchestration.state import create_initial_state
from models.place import ResolvedPlace
from models.transport import TransportType


def test_place_resolution_agent_typos_and_compounds():
    """Verifies that PlaceResolutionAgent decomposes compound entities and heals typos."""
    agent = PlaceResolutionAgent()

    test_cases = [
        # (Input, Expected canonical snippet, Expected district)
        ("Ibaijnath Temple, Kangra", "Baijnath", "Kangra"),
        ("visit hadimba mandir in manali", "Manali", "Kullu"),
        ("delhhi", "Delhi", "New Delhi"),
        ("jaipuur", "Jaipur", "Jaipur"),
        ("remote unknown village xyz, kullu", "Kullu", "Kullu"),
        ("prashar lake, mandi tehsil", "Prashar Lake", "Mandi"),
    ]

    for raw_query, expected_name, expected_district in test_cases:
        resolved = agent._resolve_single_place(raw_query)
        assert resolved.is_valid, f"Failed validity for '{raw_query}'"
        assert resolved.latitude is not None, f"Missing latitude for '{raw_query}'"
        assert resolved.longitude is not None, f"Missing longitude for '{raw_query}'"
        assert resolved.confidence >= 0.88, f"Low confidence {resolved.confidence} for '{raw_query}'"
        assert expected_name.lower() in resolved.canonical_name.lower(), (
            f"Expected '{expected_name}' in canonical '{resolved.canonical_name}' for query '{raw_query}'"
        )
        if expected_district:
            assert expected_district.lower() in (resolved.district or "").lower(), (
                f"Expected district '{expected_district}' in '{resolved.district}' for query '{raw_query}'"
            )


def test_routing_service_resilience_when_apis_down(monkeypatch):
    """Verifies that RoutingService uses Topographic Terrain Winding when live routing fails."""
    # Force requests to fail to simulate total external routing API outage
    import requests
    def mock_post(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Simulated ORS API Outage")
    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Simulated OSRM API Outage")

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(requests, "get", mock_get)

    service = RoutingService()
    # Bhuntar to Baijnath coordinates
    c1 = (31.8797, 77.1517)
    c2 = (32.0531, 76.6493)

    res = service.calculate_route(c1, c2)
    assert res is not None
    assert res["status"] == "CONSISTENT"
    assert res["verified"] is True
    assert res["distance_km"] is not None
    assert res["distance_km"] > 30.0, f"Expected realistic winding distance, got {res['distance_km']}"
    assert res["duration_mins"] is not None
    assert res["duration_mins"] > 60


def test_transport_pipeline_guaranteed_options():
    """Verifies that TransportVerificationPipeline and TransportAgent never return empty options."""
    agent = TransportAgent()

    # Test state with compound destination
    p1 = ResolvedPlace(input_name="Bhuntar", canonical_name="Bhuntar", latitude=31.8797, longitude=77.1517)
    p2 = ResolvedPlace(input_name="Ibaijnath Temple, Kangra", canonical_name="Baijnath Temple", latitude=32.0531, longitude=76.6493)

    state = create_initial_state("Travel from Bhuntar to Ibaijnath Temple, Kangra for 2 days on 3000 budget")
    state["resolved_source"] = p1
    state["resolved_destination"] = p2

    res_state = agent.execute(state)

    outbound = res_state.get("selected_outbound_transport")
    return_t = res_state.get("selected_return_transport")

    assert outbound is not None, "Selected outbound transport must not be None"
    assert return_t is not None, "Selected return transport must not be None"
    assert outbound.price is not None and outbound.price > 0.0, f"Invalid outbound fare {outbound.price}"
    assert return_t.price is not None and return_t.price > 0.0, f"Invalid return fare {return_t.price}"
    assert outbound.provider, "Missing outbound provider"
    assert "free" not in outbound.provider.lower()


def test_itinerary_optimizer_never_free_intercity_transit():
    """Verifies that Day 1 and Return transit in the compiled itinerary never show 0 or Free."""
    days = ItineraryOptimizer.build_itinerary(
        duration_days=2,
        source="Bhuntar",
        destination="Baijnath Temple",
        outbound_transport=None,  # Intentionally None to test defensive fallback
        return_transport=None,    # Intentionally None to test defensive fallback
        stay=None,
        activities=[],
        food_list=[],
        currency="INR"
    )

    assert len(days) == 2
    day1_items = days[0].items
    transit_out = next((i for i in day1_items if "transit" in i.id), None)
    assert transit_out is not None, "Day 1 must contain an outbound transit block"
    assert transit_out.estimated_cost > 0.0, f"Outbound transit cannot be 0.0; got {transit_out.estimated_cost}"
    assert "free" not in transit_out.notes.lower()

    day2_items = days[1].items
    transit_ret = next((i for i in day2_items if "transit" in i.id), None)
    assert transit_ret is not None, "Last day must contain a return transit block"
    assert transit_ret.estimated_cost > 0.0, f"Return transit cannot be 0.0; got {transit_ret.estimated_cost}"


def test_end_to_end_resilient_trip_execution():
    """End-to-end integration test for the exact query: Bhuntar -> Ibaijnath Temple, Kangra."""
    query = "I have ₹3,000. Travel from Bhuntar to Ibaijnath Temple, Kangra for 2 days"
    state = create_initial_state(query)

    # 1. Intent Extraction
    intent_agent = IntentAgent()
    state = intent_agent.execute(state)
    assert state.get("budget") == 3000.0

    # 2. Resilient Place Resolution
    place_agent = PlaceResolutionAgent()
    state = place_agent.execute(state)
    src = state.get("resolved_source")
    dst = state.get("resolved_destination")
    assert src and src.is_valid
    assert dst and dst.is_valid
    assert dst.latitude is not None
    assert "baijnath" in dst.canonical_name.lower() or "kangra" in dst.canonical_name.lower()

    # 3. Transport Agent
    trans_agent = TransportAgent()
    state = trans_agent.execute(state)
    assert state.get("selected_outbound_transport") is not None
    assert state["selected_outbound_transport"].price > 0.0

    # 4. Stay, Food, Activity, Route Verification, Budget, Itinerary, and Final Verification
    from agents.stay_agent import StayAgent
    from agents.food_agent import FoodAgent
    from agents.activity_agent import ActivityAgent
    from agents.route_verification_agent import RouteVerificationAgent
    from agents.budget_agent import BudgetAgent
    from agents.itinerary_agent import ItineraryAgent
    from agents.final_verification_agent import FinalVerificationAgent

    state = StayAgent().execute(state)
    state = FoodAgent().execute(state)
    state = ActivityAgent().execute(state)
    state = RouteVerificationAgent().execute(state)
    state = BudgetAgent().execute(state)
    state = ItineraryAgent().execute(state)
    state = FinalVerificationAgent().execute(state)

    trust = state.get("trust_scores", {})
    assert trust.get("place_resolution", 0) >= 90.0, f"Place resolution score dropped: {trust.get('place_resolution')}"
    assert trust.get("route_verification", 0) >= 90.0, f"Route verification score dropped: {trust.get('route_verification')}"
    assert trust.get("overall_confidence", 0) >= 88.0, f"Overall confidence dropped: {trust.get('overall_confidence')}"
    assert state.get("verification_results").passed is True, "Final verification gate must pass"
