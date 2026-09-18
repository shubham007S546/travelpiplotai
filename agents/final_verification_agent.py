"""Agent 10/11 — Final Verification Agent."""

from datetime import datetime, timezone
from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState, VerificationResult, VerificationFailure
from verification.final_verifier import FinalVerifier, FinalAuditGateResult
from verification.grounding_checker import GroundingChecker


class FinalVerificationAgent(BaseAgent):
    """Executes the final comprehensive verification gate and audits trust scores."""

    def __init__(self):
        super().__init__(name="Verification Agent")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        tool_calls = [
            "Auditing place resolution and coordinate existence",
            "Verifying road routing and provider consistency",
            "Auditing fare evidence and rate boundaries",
            "Checking budget feasibility and temporal schedules",
            "Calculating explainable confidence and trust breakdown"
        ]

        gate_res: FinalAuditGateResult = FinalVerifier.evaluate(state)
        state["trust_scores"] = gate_res.trust_scores

        failures: List[VerificationFailure] = []
        for reason in gate_res.failure_reasons:
            failures.append(VerificationFailure(
                failure_reason=reason,
                affected_component="verification",
                severity="high",
                recommended_action="Resolve constraint violation or re-verify parameters."
            ))

        v_result = VerificationResult(
            verification_score=gate_res.overall_confidence,
            grounding_score=gate_res.trust_scores.get("route_verification", 90.0),
            constraint_score=gate_res.overall_confidence,
            budget_score=gate_res.trust_scores.get("fare_verification", 85.0),
            temporal_score=gate_res.trust_scores.get("route_verification", 90.0),
            spatial_score=gate_res.trust_scores.get("place_resolution", 95.0),
            overall_confidence=gate_res.overall_confidence,
            passed=gate_res.passed,
            failure_reasons=failures,
            checked_at=datetime.now(timezone.utc).isoformat()
        )
        state["verification_results"] = v_result

        # Synchronize live API audit log and summary
        from utils.api_audit import get_global_audit_log
        audit_log = get_global_audit_log()
        state["api_audit_log"] = audit_log

        src = state.get("resolved_source")
        dst = state.get("resolved_destination")
        is_rural_trip = bool(
            (src and (src.is_rural or src.rural_urban == "rural")) or
            (dst and (dst.is_rural or dst.rural_urban == "rural"))
        )

        state["live_audit_summary"] = {
            "total_api_calls": len(audit_log),
            "cached_calls": len([x for x in audit_log if x.get("cached")]),
            "live_calls": len([x for x in audit_log if not x.get("cached")]),
            "routing_divergence_status": state.get("distance_status", "CONSISTENT"),
            "fare_evidence_strength": gate_res.fare_evidence_strength,
            "fare_verification_status": gate_res.fare_verification_status,
            "tariff_provenance": gate_res.tariff_provenance,
            "rural_travel_mode_active": is_rural_trip,
            "gate_passed": gate_res.passed,
            "overall_confidence": gate_res.overall_confidence
        }

        status_text = "PASS" if gate_res.passed else f"FAIL ({len(failures)} issues detected)"
        summary = (
            f"Final Audit: {status_text} | Confidence: {gate_res.overall_confidence:.1f}% | "
            f"Fare Strength: {gate_res.fare_evidence_strength} ({gate_res.fare_verification_status}) | "
            f"API Queries Logged: {len(audit_log)}"
        )
        return state, summary, tool_calls, (0.98 if gate_res.passed else 0.70)
