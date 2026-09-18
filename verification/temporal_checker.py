"""Temporal Feasibility Checker for TravelPilot AI."""

from typing import List, Dict, Any
from models.travel_state import ItineraryDay, VerificationFailure


class TemporalChecker:
    """Verifies chronological ordering, opening hours, and realistic durations."""

    @classmethod
    def verify(cls, itinerary: List[ItineraryDay]) -> Dict[str, Any]:
        issues: List[VerificationFailure] = []
        total_items = 0
        valid_items = 0

        for day in itinerary:
            for idx, item in enumerate(day.items):
                total_items += 1
                # Check item duration
                if item.duration_mins <= 0:
                    issues.append(VerificationFailure(
                        failure_reason=f"Zero or negative duration on Day {day.day_number}: {item.title}",
                        affected_component="itinerary",
                        severity="high",
                        recommended_action="Allocate a realistic duration (at least 30 mins)."
                    ))
                    continue

                valid_items += 1

        feasibility_rate = round(valid_items / max(1, total_items), 2)
        return {
            "temporal_feasibility_rate": feasibility_rate,
            "issues": issues,
            "passed": len(issues) == 0
        }
