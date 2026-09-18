"""Comprehensive Integration Test for Multi-API Quotas, Ground Truth Services, and Re-planning."""

import pytest
import os
from dotenv import load_dotenv

load_dotenv()

from services.serpapi_service import SerpApiService
from services.youtube_service import YouTubeTravelService
from services.rag_service import TravelRAGService
from services.pdf_service import generate_travel_pass_pdf
from orchestration.state import create_initial_state
from agents.stay_agent import StayAgent
from optimization.budget_optimizer import BudgetOptimizer
from models.activity import ActivityOption, ActivityCategory
from models.evidence import Evidence, SourceTier


def test_serpapi_service_google_maps():
    serp = SerpApiService()
    if serp.is_available():
        attrs = serp.search_google_maps_attractions("Jaipur", limit=5)
        assert len(attrs) > 0
        assert "name" in attrs[0]
        assert "category" in attrs[0]
        assert "image_url" in attrs[0]

        food = serp.search_google_maps_food("Mandi", dish_or_cuisine="kachori", limit=3)
        assert len(food) > 0
        assert "dish" in food[0]
        assert "famous_at" in food[0]

        homestays = serp.search_budget_homestays("Jaipur", limit=3)
        assert len(homestays) > 0
        for h in homestays:
            assert h.price_per_night <= 1200.0


def test_youtube_travel_vlogs_and_timeline():
    yt = YouTubeTravelService()
    if yt.is_available():
        vlogs = yt.search_travel_vlogs("Bhuntar", "Bijli Mahadev", max_results=3)
        assert len(vlogs) > 0
        v = vlogs[0]
        assert "title" in v
        assert "video_url" in v
        assert "freshness_badge" in v
        assert "fare_note" in v
        assert "thumbnail_url" in v


def test_rag_famous_places_top_10_and_images():
    rag = TravelRAGService()
    places = rag.get_famous_places("Jaipur")
    assert len(places) >= 5
    for p in places:
        assert "name" in p
        assert "image_url" in p
        assert p["image_url"].startswith("http")


def test_rag_regional_food_guide_mandi_kachori():
    rag = TravelRAGService()
    food = rag.get_regional_food_guide("Mandi")
    assert len(food) >= 3
    dishes = [f["dish"].lower() for f in food]
    # Verify Mandi Kachori or Siddu is present
    assert any("kachori" in d or "siddu" in d for d in dishes)


def test_stay_agent_budget_homestays_under_1200():
    state = create_initial_state("Travel from Delhi to Jaipur for 2 days on 3000 budget")
    agent = StayAgent()
    res_state = agent.execute(state)
    hotel_options = res_state.get("hotel_options", [])
    assert len(hotel_options) > 0

    # For budget traveler, the top recommended stay must be under ₹1,200
    top_stay = hotel_options[0]
    assert top_stay.price_per_night is not None
    assert top_stay.price_per_night <= 1200.0, f"Expected budget stay under 1200, got {top_stay.price_per_night}"


def test_pdf_travel_pass_generation():
    state = create_initial_state("Travel from Bhuntar to Bijli Mahadev for 2 days on 3000 budget")
    pdf_bytes = generate_travel_pass_pdf(state)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_budget_replanning_deterministic_arithmetic():
    state = create_initial_state("Travel from Delhi to Jaipur for 2 days on 4000 budget")
    agent = StayAgent()
    state = agent.execute(state)

    acts = [
        ActivityOption(
            id="act-1",
            name="Amber Palace",
            category=ActivityCategory.HERITAGE,
            location="Jaipur",
            cost=100.0,
            rating=4.8,
            opening_time="08:00",
            closing_time="17:30",
            duration_mins=90,
            distance_from_prev_km=11.0,
            evidence=Evidence(claim="test", source="test", source_type="test", confidence=1.0, tier=SourceTier.TIER_1_OFFICIAL)
        )
    ]
    bd1 = BudgetOptimizer.calculate_cost(
        budget=4000.0,
        outbound_transport=state.get("selected_outbound_transport"),
        return_transport=state.get("selected_return_transport"),
        stay=state.get("selected_hotel"),
        food_list=[],
        activity_list=acts,
        local_transit_cost=50.0,
        travelers=1,
        nights=1,
        currency="INR"
    )

    # Add a second activity costing 200
    acts.append(
        ActivityOption(
            id="act-2",
            name="City Palace",
            category=ActivityCategory.HERITAGE,
            location="Jaipur",
            cost=200.0,
            rating=4.6,
            opening_time="09:30",
            closing_time="17:00",
            duration_mins=90,
            distance_from_prev_km=2.0,
            evidence=Evidence(claim="test", source="test", source_type="test", confidence=1.0, tier=SourceTier.TIER_1_OFFICIAL)
        )
    )
    bd2 = BudgetOptimizer.calculate_cost(
        budget=4000.0,
        outbound_transport=state.get("selected_outbound_transport"),
        return_transport=state.get("selected_return_transport"),
        stay=state.get("selected_hotel"),
        food_list=[],
        activity_list=acts,
        local_transit_cost=50.0,
        travelers=1,
        nights=1,
        currency="INR"
    )

    assert bd2.activity_cost == bd1.activity_cost + 200.0
    assert bd2.total_cost == bd1.total_cost + 200.0
