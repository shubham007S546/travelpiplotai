"""Ground Reality and Practical Traveler Essentials Model.

Addresses real-world friction faced by common travelers:
Cash/UPI blackouts, telecom signal drops, baggage cloakrooms,
local taxi touts, motion sickness on ghats, and power outages.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GroundRealityCheck(BaseModel):
    """Structured ground reality field kit for common travelers."""
    destination: str
    region_type: str = Field(default="hills", description="hills / rural / pilgrimage / metro / desert / coastal")
    
    # Financial & Payment Reality
    digital_payment_status: str = Field(
        default="PARTIAL_UPI",
        description="CASH_CRITICAL / PARTIAL_UPI / DIGITAL_FRIENDLY"
    )
    cash_guidance: str
    recommended_cash_inr: float = Field(default=2000.0, description="Minimum recommended physical cash per person")
    last_atm_hub: str = Field(default="District Headquarter / Major Transit Hub")
    
    # Telecom & Connectivity
    telecom_networks: Dict[str, str] = Field(
        default_factory=lambda: {
            "Jio": "4G Available",
            "Airtel": "Available",
            "BSNL": "Lifeline Rural Coverage",
            "Vi": "Spotty in Valleys"
        }
    )
    offline_readiness_warning: str
    
    # Luggage & Storage
    luggage_cloakroom_info: str
    
    # Anti-Scam & Local Transit Protection
    anti_scam_transit_advice: str
    statutory_fare_tip: str
    
    # Health, Terrain & Physiology
    health_motion_sickness_advice: str
    altitude_ams_risk: bool = False
    
    # Climate, Power & Gear
    clothing_and_power_advice: str
    women_and_family_tips: str
    
    # Quick Essentials Checklist
    packing_checklist: List[str] = Field(default_factory=list)
