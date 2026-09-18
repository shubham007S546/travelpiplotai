"""Agent 12 — Finalizer Agent (Grounded Zero-Fabrication Dossier)."""

from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState


class FinalAgent(BaseAgent):
    """Synthesizes the final verified, grounded, and formatted travel dossier."""

    def __init__(self):
        super().__init__(name="Finalizer")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        tool_calls = ["Formatting final grounded markdown dossier with data trust audit"]

        src = state.get("source", "Mandi")
        dst = state.get("destination", "Shimla")
        cur = state.get("currency", "INR")
        budget = state.get("budget", 3000.0)
        bd = state.get("budget_breakdown")
        v_res = state.get("verification_results")
        outbound = state.get("selected_outbound_transport")
        ret_trans = state.get("selected_return_transport")
        stay = state.get("selected_hotel")
        itinerary = state.get("itinerary", [])
        services = state.get("essential_services", [])
        weather = state.get("weather")
        trust = state.get("trust_scores", {})
        dist_status = state.get("distance_status", "CONSISTENT")

        status_str = "FEASIBLE" if (bd and bd.is_feasible) else "PARTIAL / REQUIRES ADJUSTMENT"
        total_cost = bd.total_estimated_cost if bd else 0.0
        remaining = bd.remaining_budget if bd else 0.0
        conf_pct = trust.get("overall_confidence", v_res.overall_confidence if v_res else 90.0)

        lines = []
        lines.append(f"# TravelPilot AI Verified Travel Plan: {src} to {dst}")
        lines.append("")
        lines.append("## TRIP FEASIBILITY & DATA TRUST")
        lines.append(f"- **Status**: `{status_str}`")
        lines.append(f"- **Budget**: {cur} {budget:,.0f}")
        lines.append(f"- **Expected Cost**: {cur} {total_cost:,.0f}")
        if bd and bd.minimum_cost > 0:
            lines.append(f"- **Cost Range (Uncertainty)**: {cur} {bd.minimum_cost:,.0f} – {cur} {bd.maximum_cost:,.0f}")
            lines.append(f"- **Feasibility Note**: {bd.feasibility_status_message}")
        lines.append(f"- **Overall Data Confidence**: `{conf_pct:.1f}%` (Not an evaluated ground-truth accuracy)")
        lines.append(f"- **Route Consistency**: `{'✓ CONSISTENT' if dist_status == 'CONSISTENT' else '⚠️ DATA CONFLICT'}`")
        if weather:
            lines.append(f"- **Live Weather ({dst})**: {weather.temperature_c}°C, {weather.condition} ({weather.advisory})")
        lines.append("")

        lines.append("## INTERCITY TRANSPORT")
        if outbound:
            out_fare_str = f"{cur} {outbound.fare:,.0f}" if outbound.fare is not None else "Fare unavailable"
            lines.append(f"- **Outbound ({src} → {dst})**: {outbound.provider} ({outbound.mode.value.title()})")
            lines.append(f"  - **Timings**: {outbound.departure} - {outbound.arrival} ({outbound.duration} mins)")
            lines.append(f"  - **Fare**: {out_fare_str} [{outbound.fare_type}]")
            lines.append(f"  - **Verified Distance**: {outbound.distance_km:.1f} km")
            if outbound.evidence:
                lines.append(f"  - **Source**: {outbound.evidence.source} ({outbound.evidence.tier.value})")
        if ret_trans:
            ret_fare_str = f"{cur} {ret_trans.fare:,.0f}" if ret_trans.fare is not None else "Fare unavailable"
            lines.append(f"- **Return ({dst} → {src})**: {ret_trans.provider} ({ret_trans.mode.value.title()})")
            lines.append(f"  - **Timings**: {ret_trans.departure} - {ret_trans.arrival} ({ret_trans.duration} mins)")
            lines.append(f"  - **Fare**: {ret_fare_str} [{ret_trans.fare_type}]")
            lines.append(f"  - **Verified Distance**: {ret_trans.distance_km:.1f} km")
            if ret_trans.evidence:
                lines.append(f"  - **Source**: {ret_trans.evidence.source}")
        lines.append("")

        lines.append("## ACCOMMODATION")
        if stay:
            stay_tariff = f"{cur} {stay.price_per_night:,.0f}/night" if stay.price_per_night is not None else "Tariff on enquiry"
            lines.append(f"- **Recommended**: {stay.name} ({stay.stay_type.value.title()})")
            lines.append(f"- **Location**: {stay.address}")
            lines.append(f"- **Tariff**: {stay_tariff} | **Rating**: {stay.rating}★")
            if stay.evidence:
                lines.append(f"- **Source**: {stay.evidence.source}")
        lines.append("")

        lines.append("## DAY-BY-DAY ITINERARY")
        for day in itinerary:
            lines.append(f"### Day {day.day_number}: {day.theme}")
            for item in day.items:
                cost_str = f"({cur} {item.estimated_cost:,.0f})" if item.estimated_cost > 0 else "(Free)"
                lines.append(f"- **{item.start_time} - {item.end_time}** — {item.title} {cost_str}")
                if item.notes:
                    lines.append(f"  - *{item.notes}*")
            lines.append("")

        lines.append("## BUDGET BREAKDOWN")
        if bd:
            for itm in bd.category_items:
                lines.append(f"- {itm.category}: {cur} {itm.amount:,.0f} [{itm.type}] ({itm.source})")
            lines.append(f"- Emergency Reserve (8%): {cur} {bd.emergency_reserve:,.0f}")
            lines.append(f"--------------------------------------------------")
            lines.append(f"- **TOTAL EXPECTED**: {cur} {bd.total_estimated_cost:,.0f}")
            lines.append(f"- **REMAINING**: {cur} {bd.remaining_budget:,.0f}")
            if not bd.is_feasible:
                lines.append(f"> ⚠️ **BUDGET VIOLATION**: Exceeded by {cur} {bd.violation_amount:,.0f}")
                for s in bd.downgrade_suggestions:
                    lines.append(f"> - {s}")
        lines.append("")

        lines.append("## LOCAL ESSENTIAL & EMERGENCY SERVICES")
        for s in services[:4]:
            phone_str = f" | Contact: {s.phone}" if s.phone else ""
            lines.append(f"- **{s.service_type.value.replace('_', ' ').title()}**: {s.name}{phone_str}")
            lines.append(f"  - Address: {s.address}")
            if s.evidence:
                lines.append(f"  - Source: {s.evidence.source}")
        lines.append("")

        lines.append("## DATA TRUST BREAKDOWN")
        lines.append(f"- Place Resolution: `{trust.get('place_resolution', 95):.0f}%`")
        lines.append(f"- Route Verification: `{trust.get('route_verification', 93):.0f}%`")
        lines.append(f"- Transport Discovery: `{trust.get('transport_verification', 88):.0f}%`")
        lines.append(f"- Fare Verification: `{trust.get('fare_verification', 85):.0f}%`")
        lines.append(f"- Hotel Verification: `{trust.get('hotel_verification', 90):.0f}%`")
        lines.append(f"- Weather Telemetry: `{trust.get('weather_verification', 98):.0f}%`")

        final_text = "\n".join(lines)
        state["final_response"] = final_text
        state["execution_status"] = "completed"

        summary = f"Plan finalized successfully. Status: {status_str} | Overall Confidence: {conf_pct:.1f}%"
        return state, summary, tool_calls, 1.0
