"""FastAPI Serverless Application for TravelPilot AI Vercel Deployment."""

import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.state import create_initial_state
from orchestration.graph import travel_pipeline
from agents.place_resolution_agent import PlaceResolutionAgent

app = FastAPI(
    title="TravelPilot AI Serverless API",
    description="Constraint-Aware Multi-Agent Travel Planning & Verification System",
    version="2.0.0"
)

# Enable CORS for cross-origin web requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

place_agent = PlaceResolutionAgent()


def _serialize(val: Any) -> Any:
    """Recursively converts Pydantic models and complex types into JSON-serializable dictionaries."""
    if hasattr(val, "model_dump"):
        return val.model_dump()
    if isinstance(val, dict):
        return {k: _serialize(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [_serialize(item) for item in val]
    return val


class PlanRequest(BaseModel):
    query: str = Field(..., description="Natural language travel query or prompt")
    source: Optional[str] = Field(default=None, description="Optional manual origin override")
    destination: Optional[str] = Field(default=None, description="Optional manual destination override")
    budget: Optional[float] = Field(default=None, description="Budget ceiling in currency")
    currency: Optional[str] = Field(default="INR", description="Currency code")
    travelers: Optional[int] = Field(default=1, ge=1, description="Number of travelers")
    duration_days: Optional[int] = Field(default=2, ge=1, description="Trip duration in days")


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "system": "TravelPilot AI Multi-Agent System",
        "version": "2.0.0",
        "deployment": "Vercel Serverless"
    }


@app.get("/api/places/resolve")
def resolve_place(name: str):
    """Resolves coordinates, administrative district, and transit hubs for a given place name."""
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Place name is required.")
    resolved = place_agent._resolve_single_place(name.strip())
    return _serialize(resolved)


@app.post("/api/plan")
def generate_travel_plan(req: PlanRequest):
    """Executes the full 12-agent LangGraph travel planning, verification, and budgeting graph."""
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="A travel query or prompt is required.")

    try:
        initial_state = create_initial_state(user_query=req.query.strip())

        # Apply overrides if provided
        if req.source and req.source.strip():
            initial_state["source"] = req.source.strip().title()
        if req.destination and req.destination.strip():
            initial_state["destination"] = req.destination.strip().title()
        if req.budget and req.budget > 0:
            initial_state["budget"] = float(req.budget)
        if req.currency:
            initial_state["currency"] = req.currency
        if req.travelers and req.travelers >= 1:
            initial_state["travelers"] = req.travelers
        if req.duration_days and req.duration_days >= 1:
            initial_state["duration_days"] = req.duration_days

        # Execute LangGraph pipeline
        result_state = travel_pipeline.invoke(initial_state)

        # Extract structured data
        outbound = result_state.get("selected_outbound_transport")
        ret_trans = result_state.get("selected_return_transport")
        hotel = result_state.get("selected_hotel")
        budget_bd = result_state.get("budget_breakdown")
        itinerary = result_state.get("itinerary", [])
        weather = result_state.get("weather")
        all_outbound = result_state.get("outbound_transport_options", [])
        all_return = result_state.get("return_transport_options", [])

        response_payload = {
            "execution_status": result_state.get("execution_status", "completed"),
            "replanning_count": result_state.get("replanning_count", 0),
            "source": result_state.get("source"),
            "destination": result_state.get("destination"),
            "budget_limit": result_state.get("budget"),
            "currency": result_state.get("currency", "INR"),
            "duration_days": result_state.get("duration_days", 2),
            "travelers": result_state.get("travelers", 1),
            "selected_outbound_transport": _serialize(outbound) if outbound else None,
            "selected_return_transport": _serialize(ret_trans) if ret_trans else None,
            "outbound_options_count": len(all_outbound),
            "return_options_count": len(all_return),
            "outbound_transport_options": [_serialize(o) for o in all_outbound],
            "return_transport_options": [_serialize(o) for o in all_return],
            "selected_hotel": _serialize(hotel) if hotel else None,
            "hotel_options_count": len(result_state.get("hotel_options", [])),
            "budget_breakdown": _serialize(budget_bd) if budget_bd else None,
            "weather": _serialize(weather) if weather else None,
            "itinerary": [_serialize(day) for day in itinerary],
            "disruption_alerts": result_state.get("disruption_alerts", []),
            "has_disruption_risk": result_state.get("has_disruption_risk", False),
            "recommended_reroute": result_state.get("recommended_reroute"),
            "savings_vs_expensive": {
                "outbound": result_state.get("cheapest_outbound_savings_vs_expensive", 0),
                "return": result_state.get("cheapest_return_savings_vs_expensive", 0),
                "taxi_outbound_fare": result_state.get("taxi_outbound_fare", 0),
                "taxi_return_fare": result_state.get("taxi_return_fare", 0)
            },
            "evidence_count": len(result_state.get("evidence_ledger", [])),
            "final_response": result_state.get("final_response", "")
        }

        return response_payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
