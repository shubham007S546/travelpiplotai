"""Unit tests for deterministic budget optimization and financial breakdown."""

import pytest
from models.budget import BudgetBreakdown
from optimization.budget_optimizer import BudgetOptimizer
from services.mock_providers import MockTransportProvider, MockStayProvider, MockFoodProvider, MockActivityProvider


def test_budget_breakdown_arithmetic():
    """Verifies pure Python budget arithmetic and emergency reserve calculations."""
    bd = BudgetBreakdown.compute(
        total_budget=3000.0,
        intercity_transport=480.0,
        stay=850.0,
        food=440.0,
        activities=50.0,
        local_mobility=50.0,
        emergency_pct=0.08,
        currency="INR"
    )
    # Emergency reserve = 3000 * 0.08 = 240
    assert bd.emergency_reserve == 240.0
    # Total = 480 + 850 + 440 + 50 + 50 + 240 = 2110
    assert bd.total_estimated_cost == 2110.0
    assert bd.remaining_budget == 890.0
    assert bd.is_feasible is True
    assert bd.violation_amount == 0.0


def test_budget_violation_detection():
    """Verifies that exceeding the allocated budget flags infeasibility and calculates violation."""
    bd = BudgetBreakdown.compute(
        total_budget=1000.0,
        intercity_transport=800.0,
        stay=850.0,
        food=300.0,
        activities=50.0,
        local_mobility=50.0,
        emergency_pct=0.08,
        currency="INR"
    )
    assert bd.is_feasible is False
    assert bd.violation_amount > 0.0
    assert bd.remaining_budget < 0.0


def test_budget_repair_downgrades():
    """Verifies that the greedy repair engine downgrades stays and activities when budget is tight."""
    trans_prov = MockTransportProvider()
    stay_prov = MockStayProvider()
    food_prov = MockFoodProvider()
    act_prov = MockActivityProvider()

    out_opts = trans_prov.search_intercity("Mandi", "Shimla", "2026-10-01", 1)
    ret_opts = trans_prov.search_intercity("Shimla", "Mandi", "2026-10-02", 1)
    stay_opts = stay_prov.search_stays("Shimla", "2026-10-01", "2026-10-02", 1, "budget")
    food_opts = food_prov.search_food("Shimla", "Central", "local", "cheap")
    act_opts = act_prov.search_activities("Shimla", ["heritage"], 3000)

    # Test repair on a realistic low budget
    repaired_out, repaired_ret, repaired_stay, repaired_food, repaired_acts, local_cost, bd = BudgetOptimizer.repair_budget(
        budget=2000.0,
        outbound_options=out_opts,
        return_options=ret_opts,
        stay_options=stay_opts,
        food_options=food_opts,
        activity_options=act_opts,
        travelers=1,
        nights=1,
        currency="INR"
    )

    assert repaired_out is not None
    assert repaired_stay is not None
    # Cheapest stay in mock is Dormitory at 450
    assert repaired_stay.price_per_night == 450.0
    assert bd.total_estimated_cost <= 2000.0
    assert bd.is_feasible is True
