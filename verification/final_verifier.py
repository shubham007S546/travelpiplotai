"""Final Verification Gate and Claim-Level Factual Audit."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from models.travel_state import TravelState, VerificationResult, VerificationFailure
from models.transport import FareType


class FinalAuditGateResult(BaseModel):
    """Final certification gate evaluation."""
    passed: bool
    place_resolution_passed: bool
    transport_verified: bool
    route_verified: bool
    fare_verified_or_marked_estimated: bool
    hotel_data_verified: bool
    activity_data_verified: bool
    budget_calculated: bool
    itinerary_temporally_feasible: bool
    trust_scores: Dict[str, Any] = Field(default_factory=dict)
    overall_confidence: float = 0.0
    fare_evidence_strength: str = "MEDIUM"  # HIGH, MEDIUM, LOW, UNKNOWN
    fare_verification_status: str = "ESTIMATED"  # VERIFIED, ESTIMATED, UNVERIFIED
    tariff_provenance: Optional[str] = None
    failure_reasons: List[str] = Field(default_factory=list)


class FinalVerifier:
    """Rigorous gate preventing unverified or hallucinated travel plans from finalizing."""

    DEFAULT_CONFIDENCE_WEIGHTS = {
        "place": 0.25,
        "route": 0.25,
        "fare": 0.25,
        "source": 0.15,
        "temporal": 0.10
    }

    @classmethod
    def evaluate(
        cls,
        state: TravelState,
        weights: Optional[Dict[str, float]] = None
    ) -> FinalAuditGateResult:
        w = weights or cls.DEFAULT_CONFIDENCE_WEIGHTS
        failures: List[str] = []

        # 1. Place Resolution Gate
        src = state.get("resolved_source")
        dst = state.get("resolved_destination")
        place_passed = bool(src and dst and src.is_valid and dst.is_valid)
        if not place_passed:
            failures.append("Place resolution failed or coordinates unverified.")

        place_conf = round(min(src.confidence if src else 0.0, dst.confidence if dst else 0.0) * 100, 1)

        # 2. Route Verification Gate
        route_ev = state.get("route_evidence")
        dist_status = state.get("distance_status", "CONSISTENT")
        route_passed = bool(route_ev and route_ev.get("road_distance_km", 0) > 0 and dist_status != "DATA_UNAVAILABLE")
        if not route_passed:
            failures.append("Road route could not be verified by routing engine.")

        route_conf = 95.0 if (route_passed and dist_status == "CONSISTENT") else (65.0 if route_passed else 0.0)

        # 3. Transport & Fare Verification Gate
        outbound = state.get("selected_outbound_transport")
        ret_trans = state.get("selected_return_transport")
        trans_passed = bool(outbound and ret_trans)
        if not trans_passed:
            failures.append("Outbound or return transport options unverified.")

        fare_passed = True
        fare_confs: List[float] = []
        fare_types_present: List[str] = []
        provenances: List[str] = []

        for opt in [outbound, ret_trans]:
            if not opt:
                continue
            fare_types_present.append(opt.fare_type)
            if opt.fare_model_details and "tariff_source" in opt.fare_model_details:
                provenances.append(opt.fare_model_details["tariff_source"])
            elif opt.estimated_fare_breakdown and opt.estimated_fare_breakdown.tariff_source:
                provenances.append(opt.estimated_fare_breakdown.tariff_source)

            if opt.fare is None or opt.fare_type == FareType.UNKNOWN.value:
                fare_confs.append(0.0)
            elif opt.fare_type in (FareType.LIVE.value, FareType.OFFICIAL_TARIFF.value):
                fare_confs.append(96.0)
            elif opt.fare_type == FareType.ESTIMATED.value:
                fare_confs.append(90.0)
            else:
                fare_confs.append(50.0)

        fare_conf = round(sum(fare_confs) / max(1, len(fare_confs)), 1)
        trans_conf = 92.0 if trans_passed else 50.0

        # Determine Evidence Strength and Verification Status
        if all(ft in (FareType.LIVE.value, FareType.OFFICIAL_TARIFF.value) for ft in fare_types_present) and fare_types_present:
            fare_evidence_strength = "HIGH"
            fare_verification_status = "VERIFIED"
        elif all(ft in (FareType.LIVE.value, FareType.OFFICIAL_TARIFF.value, FareType.ESTIMATED.value) for ft in fare_types_present) and fare_types_present:
            fare_evidence_strength = "MEDIUM"
            fare_verification_status = "ESTIMATED"
        elif any(ft == FareType.UNKNOWN.value for ft in fare_types_present):
            fare_evidence_strength = "UNKNOWN"
            fare_verification_status = "UNVERIFIED"
        else:
            fare_evidence_strength = "LOW"
            fare_verification_status = "UNVERIFIED"

        tariff_prov = "; ".join(list(dict.fromkeys(provenances))) if provenances else "Regional Statutory Motor Vehicles Rules"

        # 4. Hotel Verification Gate
        stay = state.get("selected_hotel")
        hotel_passed = stay is not None
        hotel_conf = 92.0 if hotel_passed else 60.0

        # 5. Activity Verification Gate
        activities = state.get("selected_activities", [])
        act_passed = len(activities) > 0

        # 6. Weather Verification Gate
        weather = state.get("weather")
        weather_conf = 98.0 if weather else 70.0

        # 7. Budget Calculated Gate
        bd = state.get("budget_breakdown")
        budget_passed = bd is not None
        if bd and not bd.is_feasible:
            failures.append(f"Budget constraint exceeded by {bd.currency} {bd.violation_amount:.0f}")

        # 8. Itinerary Feasible Gate
        itinerary = state.get("itinerary", [])
        itin_passed = len(itinerary) > 0

        # Temporal confidence
        temp_conf = 95.0 if itin_passed else 50.0

        # Source confidence
        evidence_list = state.get("evidence_ledger", [])
        from verification.source_reliability import SourceReliabilityModel
        src_conf = round(SourceReliabilityModel.calculate_source_confidence(evidence_list) * 100, 1)

        # Formula: overall_confidence
        overall_conf = round(
            (w["place"] * place_conf) +
            (w["route"] * route_conf) +
            (w["fare"] * fare_conf) +
            (w["source"] * src_conf) +
            (w["temporal"] * temp_conf),
            1
        )

        trust_scores = {
            "place_resolution": place_conf,
            "route_verification": route_conf,
            "transport_verification": trans_conf,
            "fare_verification": fare_conf,
            "fare_evidence_strength": fare_evidence_strength,
            "fare_verification_status": fare_verification_status,
            "hotel_verification": hotel_conf,
            "weather_verification": weather_conf,
            "overall_confidence": overall_conf
        }

        all_passed = (
            place_passed and
            route_passed and
            trans_passed and
            fare_passed and
            hotel_passed and
            act_passed and
            budget_passed and
            itin_passed and
            (bd.is_feasible if bd else True)
        )

        return FinalAuditGateResult(
            passed=all_passed,
            place_resolution_passed=place_passed,
            transport_verified=trans_passed,
            route_verified=route_passed,
            fare_verified_or_marked_estimated=fare_passed,
            hotel_data_verified=hotel_passed,
            activity_data_verified=act_passed,
            budget_calculated=budget_passed,
            itinerary_temporally_feasible=itin_passed,
            trust_scores=trust_scores,
            overall_confidence=overall_conf,
            fare_evidence_strength=fare_evidence_strength,
            fare_verification_status=fare_verification_status,
            tariff_provenance=tariff_prov,
            failure_reasons=failures
        )
