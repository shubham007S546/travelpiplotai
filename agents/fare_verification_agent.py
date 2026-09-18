"""Fare Verification Agent — Validates tariffs, outlier rates, and fare models."""

from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState
from models.transport import TransportOption, FareType
from verification.fare_distance_validator import FareDistanceValidator, AnomalyReport


class FareVerificationAgent(BaseAgent):
    """Audits fares against published tariffs and filters rate anomalies."""

    def __init__(self):
        super().__init__(name="Fare Verification Agent")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        tool_calls = ["Auditing fare rates against published tariffs and rate-cards"]

        outbound = state.get("selected_outbound_transport")
        ret_trans = state.get("selected_return_transport")

        flags: List[str] = []
        verified_count = 0
        total_fares = 0

        for opt_key, opt in [("selected_outbound_transport", outbound), ("selected_return_transport", ret_trans)]:
            if not opt:
                continue
            total_fares += 1

            # Execute Distance Cross-Verification & Rethink Loop
            corrected_opt, did_rethink, rethink_reason = FareDistanceValidator.cross_verify_and_rethink(opt)
            if did_rethink:
                state[opt_key] = corrected_opt
                opt = corrected_opt
                flags.append(rethink_reason)

            if opt.fare is None or opt.fare_type == FareType.UNKNOWN.value:
                flags.append(f"{opt.provider}: Fare unavailable (marked UNKNOWN without fabrication)")
            elif opt.fare_type in (FareType.LIVE.value, FareType.OFFICIAL_TARIFF.value):
                verified_count += 1
            elif opt.fare_type == FareType.ESTIMATED.value:
                # Check effective rate consistency
                anomalies = FareDistanceValidator.validate_transport_option(opt)
                rate_warnings = [a.message for a in anomalies if a.anomaly_type == "RATE_INCONSISTENCY"]
                if rate_warnings:
                    flags.extend(rate_warnings)
                else:
                    verified_count += 1

        fare_score = round((verified_count / max(1, total_fares)) * 100, 1)
        trust = state.get("trust_scores", {})
        trust["fare_verification"] = max(50.0, min(100.0, fare_score))
        state["trust_scores"] = trust

        flag_str = f" | Flags: {'; '.join(flags)}" if flags else ""
        summary = f"Fare audit: {verified_count}/{total_fares} fares verified against tariff models ({fare_score:.0f}% confidence){flag_str}"
        confidence = 0.90 if not flags else 0.75
        return state, summary, tool_calls, confidence
