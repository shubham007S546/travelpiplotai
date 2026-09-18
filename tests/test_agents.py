"""Integration test for full LangGraph multi-agent execution pipeline."""

import pytest
from orchestration.graph import travel_pipeline
from orchestration.state import create_initial_state


def test_full_pipeline_mandi_shimla():
    """Verifies that the entire 12-agent graph executes end-to-end without crashing."""
    query = "I have ₹3000 and want to travel from Mandi to Shimla for 2 days alone on a budget."
    initial_state = create_initial_state(user_query=query)

    result = travel_pipeline.invoke(initial_state)

    assert result["execution_status"] == "completed"
    assert result["source"] == "Mandi"
    assert result["destination"] == "Shimla"
    assert result["budget"] == 3000.0
    assert result["travelers"] == 1
    assert result["duration_days"] == 2

    # Check that key outputs were generated
    assert result["selected_outbound_transport"] is not None
    assert result["selected_return_transport"] is not None
    assert result["selected_hotel"] is not None
    assert len(result["itinerary"]) == 2
    assert result["budget_breakdown"] is not None
    assert result["budget_breakdown"].is_feasible is True

    # Check evidence & verification
    assert len(result["evidence_ledger"]) >= 5
    assert result["verification_results"] is not None
    assert result["verification_results"].passed is True
    assert result["verification_results"].verification_score > 80.0

    # Check agent telemetry
    agent_names_logged = [log.agent_name for log in result["agent_logs"]]
    assert "Intent Agent" in agent_names_logged
    assert "Transport Agent" in agent_names_logged
    assert "Stay Agent" in agent_names_logged
    assert "Budget Optimizer" in agent_names_logged
    assert "Itinerary Optimizer" in agent_names_logged
    assert "Verification Agent" in agent_names_logged
    assert "Finalizer" in agent_names_logged
