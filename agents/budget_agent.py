"""Agent 8 — Budget Optimizer Agent."""

from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState
from optimization.budget_optimizer import BudgetOptimizer


class BudgetAgent(BaseAgent):
    """Calculates financial allocations and audits hard budget constraints."""

    def __init__(self):
        super().__init__(name="Budget Optimizer")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        budget = state.get("budget", 3000.0)
        currency = state.get("currency", "INR")
        travelers = state.get("travelers", 1)
        nights = max(1, state.get("duration_days", 2) - 1)

        tool_calls = ["Executing pure-Python deterministic budget math"]

        outbound = state.get("selected_outbound_transport")
        ret_trans = state.get("selected_return_transport")
        stay = state.get("selected_hotel")
        foods = state.get("selected_food", [])
        activities = state.get("selected_activities", [])

        # Local mobility cost estimate
        local_recs = state.get("local_mobility_options", [])
        local_cost = sum(r.price for r in local_recs) if local_recs else 50.0

        breakdown = BudgetOptimizer.calculate_cost(
            budget=budget,
            outbound_transport=outbound,
            return_transport=ret_trans,
            stay=stay,
            food_list=foods,
            activity_list=activities,
            local_transit_cost=local_cost,
            travelers=travelers,
            nights=nights,
            currency=currency
        )
        state["budget_breakdown"] = breakdown

        status_str = "FEASIBLE" if breakdown.is_feasible else f"VIOLATION (+{currency} {breakdown.violation_amount:.0f})"
        summary = (
            f"Budget: {currency} {budget:.0f} | Estimated Cost: {currency} {breakdown.total_estimated_cost:.0f} | "
            f"Remaining: {currency} {breakdown.remaining_budget:.0f} | Status: {status_str}"
        )
        confidence = 1.0 if breakdown.is_feasible else 0.7
        return state, summary, tool_calls, confidence
