"""Agent 11 — Re-Planner Agent."""

from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState
from optimization.budget_optimizer import BudgetOptimizer
from optimization.itinerary_optimizer import ItineraryOptimizer
from utils.logging import logger


class ReplannerAgent(BaseAgent):
    """Dynamic plan repair agent resolving budget and constraint violations."""

    def __init__(self):
        super().__init__(name="Re-Planner")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        replan_count = state.get("replanning_count", 0) + 1
        state["replanning_count"] = replan_count

        v_res = state.get("verification_results")
        tool_calls = [f"Initiating plan repair cycle {replan_count} of 3"]

        budget = state.get("budget", 3000.0)
        travelers = state.get("travelers", 1)
        nights = max(1, state.get("duration_days", 2) - 1)
        currency = state.get("currency", "INR")

        outbound_opts = state.get("outbound_transport_options", [])
        return_opts = state.get("return_transport_options", [])
        stay_opts = state.get("hotel_options", [])
        food_opts = state.get("food_options", [])
        act_opts = state.get("activity_options", [])

        # Execute deterministic plan repair
        tool_calls.append("Executing greedy budget repair and alternative selection")
        (
            repaired_out,
            repaired_ret,
            repaired_stay,
            repaired_food,
            repaired_acts,
            local_cost,
            repaired_bd
        ) = BudgetOptimizer.repair_budget(
            budget=budget,
            outbound_options=outbound_opts,
            return_options=return_opts,
            stay_options=stay_opts,
            food_options=food_opts,
            activity_options=act_opts,
            travelers=travelers,
            nights=nights,
            currency=currency
        )

        state["selected_outbound_transport"] = repaired_out
        state["selected_return_transport"] = repaired_ret
        state["selected_hotel"] = repaired_stay
        state["selected_food"] = repaired_food
        state["selected_activities"] = repaired_acts
        state["budget_breakdown"] = repaired_bd

        # Re-build timetable with repaired elements
        tool_calls.append("Re-scheduling chronological itinerary with repaired selections")
        repaired_itinerary = ItineraryOptimizer.build_itinerary(
            duration_days=state.get("duration_days", 2),
            source=state.get("source", "Mandi"),
            destination=state.get("destination", "Shimla"),
            outbound_transport=repaired_out,
            return_transport=repaired_ret,
            stay=repaired_stay,
            food_list=repaired_food,
            activities=repaired_acts,
            currency=currency
        )
        state["itinerary"] = repaired_itinerary

        modifications = []
        if repaired_stay:
            price_str = f"₹{repaired_stay.price_per_night:.0f}" if repaired_stay.price_per_night is not None else "Price unlisted"
            modifications.append(f"Stay adjusted to '{repaired_stay.name}' ({price_str})")
        if repaired_bd.downgrade_suggestions:
            modifications.extend(repaired_bd.downgrade_suggestions)

        summary = (
            f"Replanning cycle {replan_count} complete. "
            f"New estimated cost: {currency} {repaired_bd.total_estimated_cost:.0f} (Remaining: {currency} {repaired_bd.remaining_budget:.0f}). "
            f"Modifications applied: {'; '.join(modifications[:2])}"
        )
        return state, summary, tool_calls, 0.90
