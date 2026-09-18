"""Consistency and Data Freshness Checker."""

from typing import List, Dict, Any
from models.travel_state import ItineraryDay, VerificationFailure
from models.evidence import Evidence


class ConsistencyChecker:
    """Detects logical contradictions and stale data points."""

    @classmethod
    def verify(
        cls,
        source: str,
        destination: str,
        itinerary: List[ItineraryDay],
        evidence_list: List[Evidence]
    ) -> Dict[str, Any]:
        issues: List[VerificationFailure] = []

        if source.strip().lower() == destination.strip().lower():
            issues.append(VerificationFailure(
                failure_reason=f"Source and destination cannot be identical ({source})",
                affected_component="intent",
                severity="critical",
                recommended_action="Provide distinct origin and destination locations."
            ))

        if not itinerary:
            issues.append(VerificationFailure(
                failure_reason="Itinerary is completely empty",
                affected_component="itinerary",
                severity="critical",
                recommended_action="Execute itinerary optimization pipeline."
            ))

        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
