"""Base Agent class providing execution telemetry and structured logging."""

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List
from models.travel_state import TravelState, AgentTelemetry
from utils.logging import logger


class BaseAgent(ABC):
    """Abstract base agent providing standard telemetry and error boundary."""

    def __init__(self, name: str):
        self.name = name

    def execute(self, state: TravelState) -> TravelState:
        """Standard wrapper capturing execution latency, status, and telemetry."""
        start_ts = datetime.now(timezone.utc).isoformat()
        t0 = time.time()
        tool_calls: List[str] = []
        errors: List[str] = []
        status = "completed"
        output_summary = ""
        confidence = 1.0

        logger.info(f"Agent [{self.name}] starting execution...")
        try:
            state, output_summary, tool_calls, confidence = self._process(state)
        except Exception as e:
            status = "failed"
            errors.append(str(e))
            output_summary = f"Execution error: {str(e)}"
            logger.error(f"Agent [{self.name}] encountered error: {e}", exc_info=True)

        duration_ms = round((time.time() - t0) * 1000, 2)
        end_ts = datetime.now(timezone.utc).isoformat()

        telemetry = AgentTelemetry(
            agent_name=self.name,
            status=status,
            start_time=start_ts,
            end_time=end_ts,
            duration_ms=duration_ms,
            input_summary=self._summarize_input(state),
            tool_calls=tool_calls,
            output_summary=output_summary,
            errors=errors,
            confidence=confidence
        )

        logs = list(state.get("agent_logs", []))
        logs.append(telemetry)
        state["agent_logs"] = logs

        logger.info(f"Agent [{self.name}] finished in {duration_ms}ms ({status}).")
        return state

    @abstractmethod
    def _process(self, state: TravelState) -> tuple[TravelState, str, List[str], float]:
        """Returns (updated_state, output_summary, tool_calls_list, confidence_float)."""
        pass

    def _summarize_input(self, state: TravelState) -> str:
        src = state.get("source", "Unknown")
        dst = state.get("destination", "Unknown")
        budget = state.get("budget", 0)
        return f"Origin: {src} | Dest: {dst} | Budget: {state.get('currency', 'INR')} {budget}"
