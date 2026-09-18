"""Constraint Satisfaction and Multi-Criteria Scoring Engine."""

from typing import Dict, Any, List, Optional
from models.budget import BudgetBreakdown
from models.travel_state import ItineraryDay, VerificationFailure
from models.evidence import Evidence, TIER_RELIABILITY_WEIGHTS


class ConstraintEngine:
    """Configurable multi-criteria constraint scoring engine."""

    DEFAULT_WEIGHTS = {
        "budget": 0.30,
        "temporal": 0.20,
        "spatial": 0.20,
        "preference": 0.15,
        "grounding": 0.15,
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def evaluate(
        self,
        budget_breakdown: Optional[BudgetBreakdown],
        itinerary: List[ItineraryDay],
        evidence_list: List[Evidence],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        failures: List[VerificationFailure] = []

        # 1. Budget Constraint Score
        budget_score = 100.0
        if budget_breakdown:
            if not budget_breakdown.is_feasible:
                budget_score = max(0.0, 100.0 - (budget_breakdown.violation_amount / budget_breakdown.total_budget * 100))
                failures.append(VerificationFailure(
                    failure_reason=f"Budget exceeded by {budget_breakdown.currency} {budget_breakdown.violation_amount:.0f}",
                    affected_component="budget",
                    severity="critical",
                    recommended_action="Downgrade accommodation or replace paid activities with free viewpoints."
                ))
            else:
                # Reward healthy reserve margin (5-15% remaining)
                utilization = budget_breakdown.budget_utilization_pct
                if 70.0 <= utilization <= 95.0:
                    budget_score = 100.0
                elif utilization < 70.0:
                    budget_score = 92.0  # Slightly under-utilized
                else:
                    budget_score = 95.0

        # 2. Temporal Feasibility Score
        temporal_score = 95.0
        for day in itinerary:
            # Check for reasonable day span (e.g. not exceeding 14 active hours)
            if len(day.items) > 6:
                temporal_score -= 5.0
            # Check consecutive item order
            for i in range(len(day.items) - 1):
                curr = day.items[i]
                nxt = day.items[i + 1]
                if curr.end_time > nxt.start_time and curr.end_time != "Flexible":
                    temporal_score -= 10.0
                    failures.append(VerificationFailure(
                        failure_reason=f"Temporal overlap on Day {day.day_number}: '{curr.title}' ends at {curr.end_time} after '{nxt.title}' starts at {nxt.start_time}",
                        affected_component="itinerary",
                        severity="high",
                        recommended_action="Adjust start time or reduce duration."
                    ))

        temporal_score = max(0.0, min(100.0, temporal_score))

        # 3. Spatial Feasibility Score
        spatial_score = 94.0
        for day in itinerary:
            for item in day.items:
                if item.travel_time_from_prev_mins > 90 and item.item_type != "travel":
                    spatial_score -= 8.0
                    failures.append(VerificationFailure(
                        failure_reason=f"High transit time ({item.travel_time_from_prev_mins} mins) to '{item.title}'",
                        affected_component="local_mobility",
                        severity="medium",
                        recommended_action="Group activities closer to stay location."
                    ))
        spatial_score = max(0.0, min(100.0, spatial_score))

        # 4. Preference Satisfaction Score
        pref_score = 90.0
        # If user asked for cheap/budget and options selected are budget
        if user_preferences.get("travel_style") == "budget" and budget_breakdown and budget_breakdown.is_feasible:
            pref_score += 8.0
        pref_score = min(100.0, pref_score)

        # 5. Grounding & Source Reliability Score
        grounding_score = 90.0
        if evidence_list:
            scores = [e.reliability_score * 100.0 for e in evidence_list]
            grounding_score = round(sum(scores) / len(scores), 1)
        else:
            grounding_score = 60.0
            failures.append(VerificationFailure(
                failure_reason="No external factual evidence recorded for plan items",
                affected_component="evidence",
                severity="high",
                recommended_action="Retrieve verified rates from external provider."
            ))

        # Weighted Composite Constraint Score
        composite_score = round(
            (self.weights["budget"] * budget_score) +
            (self.weights["temporal"] * temporal_score) +
            (self.weights["spatial"] * spatial_score) +
            (self.weights["preference"] * pref_score) +
            (self.weights["grounding"] * grounding_score),
            1
        )

        passed = len([f for f in failures if f.severity in ("critical", "high")]) == 0

        return {
            "composite_score": composite_score,
            "budget_score": round(budget_score, 1),
            "temporal_score": round(temporal_score, 1),
            "spatial_score": round(spatial_score, 1),
            "preference_score": round(pref_score, 1),
            "grounding_score": round(grounding_score, 1),
            "passed": passed,
            "failures": failures
        }
