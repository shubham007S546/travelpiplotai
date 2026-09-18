"""Conditional routing logic for LangGraph multi-agent execution."""

from models.travel_state import TravelState
from utils.logging import logger


def route_after_verification(state: TravelState) -> str:
    """
    Decides whether to route to the Finalizer or enter the Re-planner loop.
    Re-planning is limited to 3 cycles to prevent infinite loops.
    """
    v_res = state.get("verification_results")
    replan_count = state.get("replanning_count", 0)
    max_attempts = state.get("max_replanning_attempts", 3)

    if v_res and v_res.passed:
        logger.info("Verification passed! Routing to Finalizer Agent.")
        return "final_agent"

    if replan_count < max_attempts:
        logger.warning(f"Verification failed with {len(v_res.failure_reasons if v_res else [])} issues. Triggering Re-planner (Attempt {replan_count + 1}/{max_attempts}).")
        return "replanner_agent"

    logger.warning("Max replanning attempts reached. Routing to Finalizer with flagged constraints.")
    return "final_agent"
