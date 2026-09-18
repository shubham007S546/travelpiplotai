"""Agent 10 — Verification Agent."""

from datetime import datetime, timezone
from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState, VerificationResult
from optimization.constraint_engine import ConstraintEngine
from verification.grounding_checker import GroundingChecker
from verification.temporal_checker import TemporalChecker
from verification.spatial_checker import SpatialChecker
from verification.consistency_checker import ConsistencyChecker


class VerificationAgent(BaseAgent):
    """Rigorous audit agent evaluating grounding, budget compliance, and spatio-temporal viability."""

    def __init__(self):
        super().__init__(name="Verification Agent")
        self.constraint_engine = ConstraintEngine()

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        tool_calls = [
            "Auditing budget constraints",
            "Validating chronological timeline & operating hours",
            "Evaluating spatial hops and transition speeds",
            "Calculating Grounded Claim Rate (GCR) and Source Reliability",
            "Scanning for data contradictions"
        ]

        budget_bd = state.get("budget_breakdown")
        itinerary = state.get("itinerary", [])
        evidence_list = state.get("evidence_ledger", [])
        source = state.get("source", "")
        dest = state.get("destination", "")

        total_recs = 2 + (1 if state.get("selected_hotel") else 0) + len(state.get("selected_activities", [])) + len(state.get("selected_food", []))

        # 1. Constraint Engine Multi-Criteria Evaluation
        eval_res = self.constraint_engine.evaluate(
            budget_breakdown=budget_bd,
            itinerary=itinerary,
            evidence_list=evidence_list,
            user_preferences={"travel_style": state.get("travel_style", "budget")}
        )

        # 2. Grounding Audit
        grounding_audit = GroundingChecker.audit(evidence_list, total_recs)

        # 3. Temporal & Spatial Audits
        temp_res = TemporalChecker.verify(itinerary)
        spat_res = SpatialChecker.verify(itinerary)
        cons_res = ConsistencyChecker.verify(source, dest, itinerary, evidence_list)

        all_failures = list(eval_res["failures"])
        all_failures.extend(temp_res["issues"])
        all_failures.extend(spat_res["issues"])
        all_failures.extend(cons_res["issues"])

        # Determine overall pass/fail status
        passed = (
            eval_res["passed"] and
            temp_res["passed"] and
            spat_res["passed"] and
            cons_res["passed"] and
            (budget_bd.is_feasible if budget_bd else True)
        )

        overall_conf = round(
            (eval_res["composite_score"] * 0.5) +
            (grounding_audit["source_reliability_score"] * 100 * 0.3) +
            (100.0 if passed else 60.0) * 0.2,
            1
        )

        v_result = VerificationResult(
            verification_score=eval_res["composite_score"],
            grounding_score=eval_res["grounding_score"],
            constraint_score=eval_res["composite_score"],
            budget_score=eval_res["budget_score"],
            temporal_score=eval_res["temporal_score"],
            spatial_score=eval_res["spatial_score"],
            overall_confidence=overall_conf,
            passed=passed,
            failure_reasons=all_failures,
            checked_at=datetime.now(timezone.utc).isoformat()
        )
        state["verification_results"] = v_result

        status_text = "PASS" if passed else f"FAIL ({len(all_failures)} issues detected)"
        summary = (
            f"Audit Status: {status_text} | Verification: {v_result.verification_score:.1f}% | "
            f"Grounding: {v_result.grounding_score:.1f}% | Confidence: {v_result.overall_confidence:.1f}%"
        )
        return state, summary, tool_calls, (0.98 if passed else 0.70)
