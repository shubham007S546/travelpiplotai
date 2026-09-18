"""Unit tests for multi-criteria constraint scoring."""

from models.budget import BudgetBreakdown
from optimization.constraint_engine import ConstraintEngine
from models.evidence import Evidence, SourceTier


def test_constraint_engine_passing_case():
    """Verifies that compliant budget and grounded evidence produce a passing audit."""
    engine = ConstraintEngine()
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

    evidence = [
        Evidence(
            claim="Bus fare is ₹240",
            source="HRTC",
            source_type="Official API",
            tier=SourceTier.TIER_1_OFFICIAL,
            confidence=0.98
        ),
        Evidence(
            claim="Homestay room is ₹850",
            source="HP Tourism",
            source_type="Govt Portal",
            tier=SourceTier.TIER_1_OFFICIAL,
            confidence=0.95
        )
    ]

    res = engine.evaluate(
        budget_breakdown=bd,
        itinerary=[],
        evidence_list=evidence,
        user_preferences={"travel_style": "budget"}
    )

    assert res["passed"] is True
    assert res["composite_score"] >= 80.0
    assert res["budget_score"] == 100.0


def test_constraint_engine_failing_case():
    """Verifies that budget violations trigger critical failure flags."""
    engine = ConstraintEngine()
    bd = BudgetBreakdown.compute(
        total_budget=1000.0,
        intercity_transport=800.0,
        stay=850.0,
        food=440.0,
        activities=50.0,
        local_mobility=50.0,
        emergency_pct=0.08,
        currency="INR"
    )

    res = engine.evaluate(
        budget_breakdown=bd,
        itinerary=[],
        evidence_list=[],
        user_preferences={"travel_style": "budget"}
    )

    assert res["passed"] is False
    assert len(res["failures"]) > 0
    assert any(f.affected_component == "budget" for f in res["failures"])
