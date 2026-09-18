"""Data Consistency Agent — Audits spatio-temporal coherence and routing consistency."""

from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState
from verification.consistency_checker import ConsistencyChecker
from verification.spatial_checker import SpatialChecker
from verification.temporal_checker import TemporalChecker


class DataConsistencyAgent(BaseAgent):
    """Audits spatio-temporal coherence, prevents overlapping events, and checks cross-provider alignment."""

    def __init__(self):
        super().__init__(name="Data Consistency Agent")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        tool_calls = [
            "Auditing itinerary chronological consistency",
            "Validating spatial transitions and speeds",
            "Checking distance and geocoding consistency"
        ]

        itinerary = state.get("itinerary", [])
        src = state.get("source", "")
        dst = state.get("destination", "")
        evidence = state.get("evidence_ledger", [])

        # 1. Temporal Check
        temp_res = TemporalChecker.verify(itinerary)

        # 2. Spatial Check
        spat_res = SpatialChecker.verify(itinerary)

        # 3. Contradiction Check
        cons_res = ConsistencyChecker.verify(src, dst, itinerary, evidence)

        issues = temp_res["issues"] + spat_res["issues"] + cons_res["issues"]

        # Check route conflict
        dist_status = state.get("distance_status", "CONSISTENT")
        if dist_status == "CONFLICT":
            issues.append(f"Routing distance conflict ({state.get('distance_difference_pct', 0.0):.1f}% divergence)")

        passed = len(issues) == 0

        summary = f"Consistency audit: {'PASS (100% Spatio-Temporal Alignment)' if passed else f'FAIL ({len(issues)} issues detected)'}"
        confidence = 0.98 if passed else 0.70
        return state, summary, tool_calls, confidence
