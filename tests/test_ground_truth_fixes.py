"""Automated test suite verifying the ground-truth fixes for local/regional travel."""

import pytest
from orchestration.state import create_initial_state
from agents.intent_agent import IntentAgent
from agents.place_resolution_agent import PlaceResolutionAgent
from agents.stay_agent import StayAgent
from services.transport_verification import TransportVerificationPipeline
from verification.fare_distance_validator import FareDistanceValidator
from services.youtube_service import YouTubeTravelService
from services.rag_service import TravelRAGService
from optimization.budget_optimizer import BudgetOptimizer
from models.transport import TransportOption, TransportType


def test_intent_parsing_and_camping():
    query = "I have 3000 rupees. I put the place bhutar to bijli mahadev temple with bus to kullu then bijli mahadev and trek 2-3 km, we want camp and rent tent"
    intent_agent = IntentAgent()
    state = create_initial_state(user_query=query)
    state, _, _, _ = intent_agent._process(state)
    assert state["source"].lower() in ("bhutar", "bhuntar")
    assert "bijli mahadev" in state["destination"].lower()
    assert "camping" in state["accommodation_preference"].lower()
    assert "trekking" in state["interests"]


def test_place_resolution_and_trek_detection():
    place_agent = PlaceResolutionAgent()
    state = create_initial_state(user_query="bhutar to bijli mahadev")
    state["source"] = "Bhutar"
    state["destination"] = "Bijli Mahadev Temple"
    state, _, _, _ = place_agent._process(state)
    src = state["resolved_source"]
    dst = state["resolved_destination"]

    assert src.canonical_name == "Bhuntar"
    assert src.state == "Himachal Pradesh"
    assert dst.canonical_name == "Bijli Mahadev Temple"
    assert dst.is_trek_destination is True
    assert dst.road_head_hub == "Chansari"


def test_grounded_multi_leg_fares():
    trans_pipeline = TransportVerificationPipeline()
    place_agent = PlaceResolutionAgent()
    src = place_agent._resolve_single_place("Bhuntar")
    dst = place_agent._resolve_single_place("Bijli Mahadev Temple")

    out_opts, _, msgs = trans_pipeline.discover_and_verify_transport(src, dst, "2026-10-01", 1)
    multi_bus = next((o for o in out_opts if o.is_multi_leg), None)

    assert multi_bus is not None
    assert len(multi_bus.legs) == 3
    assert multi_bus.legs[0].fare == 30.0  # Bhuntar to Kullu Bus Stand
    assert multi_bus.legs[1].fare == 50.0  # Kullu to Chansari
    assert multi_bus.legs[2].fare == 0.0   # Chansari to Bijli Mahadev Trek
    assert multi_bus.price == 80.0         # Total ₹80


def test_camping_stay_options():
    stay_agent = StayAgent()
    place_agent = PlaceResolutionAgent()
    dst = place_agent._resolve_single_place("Bijli Mahadev Temple")
    state = create_initial_state(user_query="trip")
    state["resolved_destination"] = dst
    state["destination"] = "Bijli Mahadev Temple"
    state["accommodation_preference"] = "camping"

    state, _, _, _ = stay_agent._process(state)
    sel_stay = state["selected_hotel"]

    assert sel_stay is not None
    assert sel_stay.is_camping is True
    assert len(sel_stay.gear_included) > 0
    assert sel_stay.price_per_night in (450.0, 600.0)


def test_distance_method_rethink_loop():
    anomalous_bus = TransportOption(
        id="test-anon-bus",
        mode=TransportType.BUS,
        provider="HRTC Stage Carriage",
        origin="Mandi",
        destination="Sundernagar",
        departure="08:00",
        arrival="08:50",
        duration=50,
        distance_km=25.0,
        fare=550.0,
        currency="INR"
    )
    corrected, did_rethink, reason = FareDistanceValidator.cross_verify_and_rethink(anomalous_bus)
    assert did_rethink is True
    assert corrected.fare < 80.0
    assert corrected.fare_type == "ESTIMATED"


def test_youtube_travel_freshness():
    yt = YouTubeTravelService()
    if yt.is_available():
        vlogs = yt.search_travel_vlogs("Bhuntar", "Bijli Mahadev", max_results=2)
        assert len(vlogs) > 0
        assert "freshness_badge" in vlogs[0]
        assert "fare_note" in vlogs[0]


def test_famous_places_and_dynamic_budget_replanning():
    rag = TravelRAGService()
    places = rag.get_famous_places("Kullu")
    assert any("Hadimba" in p["name"] for p in places)
    hadimba = next(p for p in places if "Hadimba" in p["name"])

    # Test deterministic budget calculation change
    bd1 = BudgetOptimizer.calculate_cost(
        budget=3000.0,
        outbound_transport=None,
        return_transport=None,
        stay=None,
        food_list=[],
        activity_list=[],
        local_transit_cost=35.0,
        travelers=1,
        nights=1,
        currency="INR"
    )

    from models.activity import ActivityOption, ActivityCategory
    from models.evidence import Evidence, SourceTier
    new_act = ActivityOption(
        id="hadimba-act",
        name=hadimba["name"],
        category=ActivityCategory.TEMPLE,
        location=hadimba["name"],
        cost=hadimba["cost"],
        evidence=Evidence(claim="test", value=0.0, source="test", source_type="test", confidence=1.0, tier=SourceTier.TIER_1_OFFICIAL)
    )

    bd2 = BudgetOptimizer.calculate_cost(
        budget=3000.0,
        outbound_transport=None,
        return_transport=None,
        stay=None,
        food_list=[],
        activity_list=[new_act],
        local_transit_cost=35.0 + hadimba.get("transit_cost", 60.0),
        travelers=1,
        nights=1,
        currency="INR"
    )

    assert bd2.total_estimated_cost > bd1.total_estimated_cost


def test_small_route_mobility_pungh_to_murari_devi():
    """Verify small route (<35 km) resolution, road distance, and local transit synthesis."""
    place_agent = PlaceResolutionAgent()
    src = place_agent._resolve_single_place("pungh sundernagar")
    dst = place_agent._resolve_single_place("murari devi")

    assert src is not None
    assert src.latitude is not None and src.longitude is not None
    assert "Sundernagar" in src.canonical_name or "Pungh" in src.canonical_name

    assert dst is not None
    assert dst.latitude is not None and dst.longitude is not None
    assert "Murari Devi" in dst.canonical_name
    assert dst.is_trek_destination is True

    trans_pipeline = TransportVerificationPipeline()
    out_opts, route, msgs = trans_pipeline.discover_and_verify_transport(src, dst, "2026-10-01", 1)

    assert route is not None
    assert 10.0 <= route.road_distance_km <= 25.0
    assert route.distance_status in ("CONSISTENT", "VERIFIED")

    # Verify that local transit options are synthesized
    assert len(out_opts) >= 3
    modes = [o.mode for o in out_opts]
    assert TransportType.SHARED_TAXI in modes
    assert TransportType.BUS in modes
    assert TransportType.TAXI in modes

    # Verify return transit options
    ret_opts, ret_route, _ = trans_pipeline.discover_and_verify_transport(dst, src, "2026-10-02", 1)
    assert len(ret_opts) >= 2

