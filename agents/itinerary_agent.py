"""Agent 9 — Itinerary Optimizer Agent."""

from typing import List, Tuple
from agents.base_agent import BaseAgent
from models.travel_state import TravelState
from optimization.itinerary_optimizer import ItineraryOptimizer


class ItineraryAgent(BaseAgent):
    """Schedules chronological itineraries with spatial and temporal coherence."""

    def __init__(self):
        super().__init__(name="Itinerary Optimizer")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        duration_days = state.get("duration_days", 2)
        source = state.get("source", "Mandi")
        dest = state.get("destination", "Shimla")
        currency = state.get("currency", "INR")

        tool_calls = [f"Synthesizing {duration_days}-day chronological timetable"]

        outbound = state.get("selected_outbound_transport")
        ret_trans = state.get("selected_return_transport")
        stay = state.get("selected_hotel")
        foods = state.get("selected_food", [])
        activities = state.get("selected_activities", [])

        itinerary = ItineraryOptimizer.build_itinerary(
            duration_days=duration_days,
            source=source,
            destination=dest,
            outbound_transport=outbound,
            return_transport=ret_trans,
            stay=stay,
            food_list=foods,
            activities=activities,
            currency=currency
        )
        state["itinerary"] = itinerary

        total_items = sum(len(d.items) for d in itinerary)
        summary = f"Generated {len(itinerary)} days ({total_items} timed schedule blocks) respecting operating hours and transit windows."
        return state, summary, tool_calls, 0.96
