"""Automated Test Suite for Concurrent Discovery Engine & Proactive Disruption Agent."""

import pytest
from orchestration.state import create_initial_state
from orchestration.graph import travel_pipeline
from orchestration.concurrent_discovery import concurrent_discovery_engine
from agents.trip_disruption_agent import TripDisruptionAgent
from models.travel_state import WeatherForecast


def test_concurrent_discovery_engine_execution():
    """Verifies that all 5 domains run concurrently and merge state safely."""
    state = create_initial_state("Travel from Mandi to Shimla for 2 days on 3000 budget")
    state["source"] = "Mandi"
    state["destination"] = "Shimla"

    out_state = concurrent_discovery_engine.execute(state)

    # 1. Transport domain outputs
    assert len(out_state.get("outbound_transport_options", [])) > 0
    assert out_state.get("selected_outbound_transport") is not None

    # 2. Stay domain outputs
    assert len(out_state.get("hotel_options", [])) > 0
    assert out_state.get("selected_hotel") is not None

    # 3. Food domain outputs
    assert len(out_state.get("food_options", [])) > 0
    assert len(out_state.get("selected_food", [])) > 0

    # 4. Activity domain outputs
    assert len(out_state.get("activity_options", [])) > 0
    assert len(out_state.get("selected_activities", [])) > 0

    # 5. Safety domain outputs
    assert len(out_state.get("essential_services", [])) > 0
    assert out_state.get("weather") is not None

    # Verify all 5 child agents logged their individual telemetry
    logged_names = {log.agent_name for log in out_state.get("agent_logs", [])}
    assert "Transport Agent" in logged_names
    assert "Stay Agent" in logged_names
    assert "Food Agent" in logged_names
    assert "Activity Agent" in logged_names
    assert "Safety & Services Agent" in logged_names


def test_trip_disruption_agent_heavy_rain():
    """Verifies that heavy downpours trigger proactive safety alerts."""
    state = create_initial_state("Mandi to Shimla")
    state["source"] = "Mandi"
    state["destination"] = "Shimla"
    state["weather"] = WeatherForecast(
        location="Shimla",
        temperature_c=18.0,
        apparent_temp_c=17.0,
        condition="Heavy Thunderstorm & Downpour",
        precipitation_chance_pct=90,
        precipitation_mm=38.5,
        weather_code=95,
        advisory="Torrential rainfall advisory",
        clothing_recommendation="Waterproof rain jacket and boots"
    )

    agent = TripDisruptionAgent()
    out_state = agent.execute(state)

    assert out_state["has_disruption_risk"] is True
    assert len(out_state["disruption_alerts"]) >= 1
    storm_alert = next((a for a in out_state["disruption_alerts"] if a["type"] == "WEATHER_RAIN_STORM"), None)
    assert storm_alert is not None
    assert storm_alert["severity"] == "HIGH"
    assert "38.5mm" in storm_alert["description"]


def test_trip_disruption_agent_mountain_corridor_bypass():
    """Verifies that mountain corridor hazard detection suggests verified detours."""
    state = create_initial_state("Mandi to Manali")
    state["source"] = "Mandi"
    state["destination"] = "Manali"
    state["weather"] = WeatherForecast(
        location="Manali",
        temperature_c=14.0,
        apparent_temp_c=13.0,
        condition="Showers",
        precipitation_chance_pct=65,
        precipitation_mm=16.0,
        weather_code=81,
        advisory="Rainy conditions",
        clothing_recommendation="Rainwear"
    )

    agent = TripDisruptionAgent()
    out_state = agent.execute(state)

    assert out_state["has_disruption_risk"] is True
    assert out_state["recommended_reroute"] is not None
    assert "Kataula" in out_state["recommended_reroute"] or "Kamand" in out_state["recommended_reroute"]


def test_end_to_end_parallel_graph_execution():
    """Verifies full LangGraph workflow execution with parallel fan-out and disruption agent."""
    state = create_initial_state("Quick 1 day trip from Mandi to Shimla with ₹2000 budget")
    state["source"] = "Mandi"
    state["destination"] = "Shimla"
    state["duration_days"] = 1
    state["budget"] = 2000.0

    result = travel_pipeline.invoke(state)

    assert result["execution_status"] == "completed"
    assert result["selected_outbound_transport"] is not None
    assert result["budget_breakdown"] is not None
    assert "disruption_alerts" in result

    # Check that both concurrent discovery agents and disruption agent are present in logs
    logged_agents = [log.agent_name for log in result["agent_logs"]]
    assert "Intent Agent" in logged_agents
    assert "Place Resolution Agent" in logged_agents
    assert "Transport Agent" in logged_agents
    assert "Stay Agent" in logged_agents
    assert "Trip Disruption Agent" in logged_agents
    assert "Budget Optimizer" in logged_agents
    assert "Itinerary Optimizer" in logged_agents
    assert "Verification Agent" in logged_agents
    assert "Finalizer" in logged_agents
