"""Spatial Feasibility and Route Transitions Checker."""

from typing import List, Dict, Any
from models.travel_state import ItineraryDay, VerificationFailure


class SpatialChecker:
    """Verifies that geographic hops between itinerary stops are practical and achievable."""

    @classmethod
    def verify(cls, itinerary: List[ItineraryDay]) -> Dict[str, Any]:
        issues: List[VerificationFailure] = []
        total_transitions = 0
        valid_transitions = 0

        for day in itinerary:
            for item in day.items:
                total_transitions += 1
                # Point-to-point transit check
                if item.travel_time_from_prev_mins > 120 and item.item_type != "travel":
                    issues.append(VerificationFailure(
                        failure_reason=f"Excessive intra-city transit time ({item.travel_time_from_prev_mins} mins) to {item.title}",
                        affected_component="local_mobility",
                        severity="medium",
                        recommended_action="Reorder itinerary to visit nearby attractions sequentially."
                    ))
                else:
                    valid_transitions += 1

        spatial_feasibility_rate = round(valid_transitions / max(1, total_transitions), 2)
        return {
            "spatial_feasibility_rate": spatial_feasibility_rate,
            "issues": issues,
            "passed": len(issues) == 0
        }
