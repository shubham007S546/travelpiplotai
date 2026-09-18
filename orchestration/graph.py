"""LangGraph StateGraph assembly for TravelPilot AI with Zero-Fabrication Architecture."""

from langgraph.graph import StateGraph, START, END
from models.travel_state import TravelState
from agents.intent_agent import IntentAgent
from agents.place_resolution_agent import PlaceResolutionAgent
from agents.transport_agent import TransportAgent
from agents.stay_agent import StayAgent
from agents.food_agent import FoodAgent
from agents.activity_agent import ActivityAgent
from agents.route_verification_agent import RouteVerificationAgent
from agents.fare_verification_agent import FareVerificationAgent
from agents.local_mobility_agent import LocalMobilityAgent
from agents.safety_agent import SafetyAgent
from agents.budget_agent import BudgetAgent
from agents.itinerary_agent import ItineraryAgent
from agents.data_consistency_agent import DataConsistencyAgent
from agents.trip_disruption_agent import TripDisruptionAgent
from agents.final_verification_agent import FinalVerificationAgent
from agents.replanner_agent import ReplannerAgent
from agents.final_agent import FinalAgent
from orchestration.routing import route_after_verification
from orchestration.concurrent_discovery import concurrent_discovery_engine


def build_travel_graph() -> StateGraph:
    """Instantiates and links all verified agents in the high-speed LangGraph execution flow."""

    intent_agent = IntentAgent()
    place_agent = PlaceResolutionAgent()
    transport_agent = TransportAgent()
    stay_agent = StayAgent()
    food_agent = FoodAgent()
    activity_agent = ActivityAgent()
    route_ver_agent = RouteVerificationAgent()
    fare_ver_agent = FareVerificationAgent()
    local_mobility_agent = LocalMobilityAgent()
    safety_agent = SafetyAgent()
    disruption_agent = TripDisruptionAgent()
    budget_agent = BudgetAgent()
    itinerary_agent = ItineraryAgent()
    consistency_agent = DataConsistencyAgent()
    final_ver_agent = FinalVerificationAgent()
    replanner_agent = ReplannerAgent()
    final_agent = FinalAgent()

    workflow = StateGraph(TravelState)

    # Register Nodes
    workflow.add_node("intent_agent", intent_agent.execute)
    workflow.add_node("place_resolution_agent", place_agent.execute)
    workflow.add_node("concurrent_discovery", concurrent_discovery_engine.execute)
    workflow.add_node("transport_agent", transport_agent.execute)
    workflow.add_node("stay_agent", stay_agent.execute)
    workflow.add_node("food_agent", food_agent.execute)
    workflow.add_node("activity_agent", activity_agent.execute)
    workflow.add_node("safety_agent", safety_agent.execute)
    workflow.add_node("route_verification_agent", route_ver_agent.execute)
    workflow.add_node("fare_verification_agent", fare_ver_agent.execute)
    workflow.add_node("local_mobility_agent", local_mobility_agent.execute)
    workflow.add_node("trip_disruption_agent", disruption_agent.execute)
    workflow.add_node("budget_agent", budget_agent.execute)
    workflow.add_node("itinerary_agent", itinerary_agent.execute)
    workflow.add_node("data_consistency_agent", consistency_agent.execute)
    workflow.add_node("final_verification_agent", final_ver_agent.execute)
    workflow.add_node("replanner_agent", replanner_agent.execute)
    workflow.add_node("final_agent", final_agent.execute)

    # High-Speed Parallel Fan-Out Execution Flow
    workflow.add_edge(START, "intent_agent")
    workflow.add_edge("intent_agent", "place_resolution_agent")
    workflow.add_edge("place_resolution_agent", "concurrent_discovery")
    workflow.add_edge("concurrent_discovery", "route_verification_agent")
    workflow.add_edge("route_verification_agent", "fare_verification_agent")
    workflow.add_edge("fare_verification_agent", "local_mobility_agent")
    workflow.add_edge("local_mobility_agent", "trip_disruption_agent")
    workflow.add_edge("trip_disruption_agent", "budget_agent")
    workflow.add_edge("budget_agent", "itinerary_agent")
    workflow.add_edge("itinerary_agent", "data_consistency_agent")
    workflow.add_edge("data_consistency_agent", "final_verification_agent")

    # Conditional Branching
    workflow.add_conditional_edges(
        "final_verification_agent",
        route_after_verification,
        {
            "final_agent": "final_agent",
            "replanner_agent": "replanner_agent"
        }
    )

    # Re-planner loop back to verification
    workflow.add_edge("replanner_agent", "final_verification_agent")
    workflow.add_edge("final_agent", END)

    return workflow.compile()


# Compiled singleton graph
travel_pipeline = build_travel_graph()
