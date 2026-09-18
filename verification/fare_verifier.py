"""Fare Verification and Distance-Based Tariff Engine."""

from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from models.transport import FareType, FareModelType, TransportType, EstimatedFareDetails


class TariffModel(BaseModel):
    """Authentic published tariff specification with legal/agency provenance."""
    model_config = {"protected_namespaces": ()}
    tariff_source: str = Field(..., description="Issuing transport authority or gazetted tariff notification")
    legal_notice_ref: Optional[str] = Field(default=None, description="Gazette notification order number or legal reference")
    effective_date: str = Field(..., description="Effective gazette date (YYYY-MM-DD)")
    vehicle_type: str = Field(..., description="Specific vehicle category (e.g. Ordinary Bus, Sedan Cab, Auto)")
    mode: TransportType
    model_type: FareModelType = FareModelType.DISTANCE_BASED
    base_fare: float = Field(default=0.0, ge=0.0)
    per_km_rate: float = Field(default=0.0, ge=0.0)
    minimum_fare: float = Field(default=0.0, ge=0.0)
    waiting_rate_per_hour: float = Field(default=0.0, ge=0.0)
    night_charge_multiplier: float = Field(default=1.0, ge=1.0)
    toll_policy: str = Field(default="Tolls and state entry taxes extra at actuals")
    source_url: Optional[str] = None


class VerifiedFareResult(BaseModel):
    """Structured audit and breakdown of verified or estimated fare."""
    model_config = {"protected_namespaces": ()}
    fare: Optional[float]
    fare_type: str  # LIVE, OFFICIAL_TARIFF, PROVIDER_QUOTE, ESTIMATED, UNKNOWN
    currency: str = "INR"
    model_type: str
    display_label: str
    calculation_breakdown: Optional[str] = None
    breakdown_details: Dict[str, Any] = Field(default_factory=dict)
    tariff_source: Optional[str] = None
    estimated_fare_details: Optional[EstimatedFareDetails] = None
    confidence: float = 0.85


# Officially published tariff registry with statutory legal provenance
PUBLISHED_TARIFFS: Dict[str, TariffModel] = {
    "bus_ordinary": TariffModel(
        tariff_source="Himachal Pradesh State Transport Authority (STA) Notification",
        legal_notice_ref="HP Gaz. Extra., Notification No. TPT-A(3)-1/2020",
        effective_date="2023-08-01",
        vehicle_type="Ordinary Stage Carriage Bus (3x2)",
        mode=TransportType.BUS,
        model_type=FareModelType.DISTANCE_BASED,
        base_fare=10.0,
        per_km_rate=1.65,
        minimum_fare=10.0,
        source_url="https://himachal.nic.in/transport"
    ),
    "bus_deluxe": TariffModel(
        tariff_source="Himachal Road Transport Corporation (HRTC) Stage Carriage Fare Notification",
        legal_notice_ref="HRTC Fare Revision Order 2023/118",
        effective_date="2023-08-01",
        vehicle_type="Deluxe 2x2 AC / Semi-Deluxe Bus",
        mode=TransportType.BUS,
        model_type=FareModelType.DISTANCE_BASED,
        base_fare=30.0,
        per_km_rate=2.75,
        minimum_fare=50.0,
        source_url="https://hrtchp.com"
    ),
    "taxi_sedan": TariffModel(
        tariff_source="District Transport Office / RTA Approved Tourist Taxi Fare Card",
        legal_notice_ref="DTO Rate Notification HP-01-2024-TAXI",
        effective_date="2024-01-15",
        vehicle_type="Hatchback / Compact Sedan (Point-to-Point)",
        mode=TransportType.TAXI,
        model_type=FareModelType.DISTANCE_BASED,
        base_fare=250.0,
        per_km_rate=18.0,
        minimum_fare=400.0,
        toll_policy="Toll plaza charges extra at actuals",
        source_url="https://himachaltourism.gov.in"
    ),
    "shared_taxi": TariffModel(
        tariff_source="Regional Transport Authority (RTA) / Himachal Motor Vehicles Rules",
        legal_notice_ref="RTA Maxi Cab Per-Seat Regulatory Schedule",
        effective_date="2023-11-01",
        vehicle_type="Maxi Cab Shared Seat (Per Passenger)",
        mode=TransportType.SHARED_TAXI,
        model_type=FareModelType.DISTANCE_BASED,
        base_fare=40.0,
        per_km_rate=3.50,
        minimum_fare=50.0,
        source_url="https://himachal.nic.in/transport"
    ),
    "auto_rickshaw": TariffModel(
        tariff_source="Municipal Corporation Metered Auto Tariff",
        legal_notice_ref="STA/MTR/2023-42",
        effective_date="2023-05-10",
        vehicle_type="3-Wheeler Auto Rickshaw",
        mode=TransportType.AUTO_RICKSHAW,
        model_type=FareModelType.METERED,
        base_fare=30.0,
        per_km_rate=15.0,
        minimum_fare=30.0,
        source_url="https://transport.delhi.gov.in"
    )
}


class FareVerifier:
    """Strict fare calculation and verification engine."""

    @classmethod
    def calculate_distance_fare(
        cls,
        tariff_key: str,
        road_distance_km: float,
        is_night: bool = False
    ) -> VerifiedFareResult:
        """
        Calculates estimated fare ONLY when an authentic tariff model exists.
        Formula: base_fare + (per_km_rate * road_distance)
        """
        tariff = PUBLISHED_TARIFFS.get(tariff_key)
        if not tariff or tariff.model_type == FareModelType.UNKNOWN or road_distance_km <= 0:
            return VerifiedFareResult(
                fare=None,
                fare_type=FareType.UNKNOWN.value,
                model_type=FareModelType.UNKNOWN.value,
                display_label="Fare unavailable",
                calculation_breakdown="Fare unavailable — could not be verified.",
                confidence=0.0
            )

        # Base + distance calculation
        distance_charge = round(tariff.per_km_rate * road_distance_km, 2)
        subtotal = tariff.base_fare + distance_charge
        subtotal = max(subtotal, tariff.minimum_fare)

        if is_night:
            subtotal = subtotal * tariff.night_charge_multiplier

        final_fare = round(subtotal, 0)
        breakdown_str = (
            f"Distance: {road_distance_km:.1f} km | "
            f"Fare source: {tariff.tariff_source} | "
            f"Model: ₹{tariff.base_fare:.0f} base + ₹{tariff.per_km_rate:.2f}/km | "
            f"Calculation: ₹{tariff.base_fare:.0f} + ({road_distance_km:.1f} × ₹{tariff.per_km_rate:.2f}) = ₹{final_fare:.0f}"
        )

        details = {
            "road_distance_km": road_distance_km,
            "tariff_source": tariff.tariff_source,
            "legal_notice_ref": tariff.legal_notice_ref,
            "effective_date": tariff.effective_date,
            "base_fare": tariff.base_fare,
            "per_km_rate": tariff.per_km_rate,
            "minimum_fare": tariff.minimum_fare,
            "vehicle_type": tariff.vehicle_type,
            "formula": f"₹{tariff.base_fare:.0f} + (₹{tariff.per_km_rate:.2f} × {road_distance_km:.1f} km)",
            "final_fare": final_fare,
            "toll_policy": tariff.toll_policy
        }

        est_fare_details = EstimatedFareDetails(
            tariff_name=tariff.vehicle_type,
            tariff_source=tariff.tariff_source,
            tariff_url=tariff.source_url,
            tariff_effective_date=tariff.effective_date,
            vehicle_type=tariff.vehicle_type,
            base_fare=tariff.base_fare,
            per_km_rate=tariff.per_km_rate,
            road_distance_km=road_distance_km,
            calculation=f"₹{tariff.base_fare:.0f} + ({road_distance_km:.1f} km × ₹{tariff.per_km_rate:.2f}/km) = ₹{final_fare:.0f}",
            resulting_fare=final_fare,
            applicable_region="Himachal Pradesh / Regional",
            applicable_service="Stage Carriage / Regulated Point-to-Point",
            confidence=0.90
        )

        return VerifiedFareResult(
            fare=final_fare,
            fare_type=FareType.ESTIMATED.value,
            model_type=tariff.model_type.value,
            display_label=f"Estimated fare: ₹{final_fare:.0f}",
            calculation_breakdown=breakdown_str,
            breakdown_details=details,
            tariff_source=tariff.tariff_source,
            estimated_fare_details=est_fare_details,
            confidence=0.90
        )
