"""Fare-Distance Validator, Outlier Detector, and Time-Distance Consistency Audit."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from models.transport import TransportOption, TransportType


class AnomalyReport(BaseModel):
    """Structured report of a detected data anomaly or outlier."""
    anomaly_type: str  # SPEED_ANOMALY, FARE_ANOMALY, DISTANCE_ANOMALY, PROVIDER_ANOMALY
    message: str
    component_id: str
    severity: str = "critical"  # critical / warning
    is_rejected: bool = True


class FareDistanceValidator:
    """Validates realistic price-per-km rates, physical speeds, and flags outliers."""

    # Reasonable operating speed bounds (km/h)
    SPEED_BOUNDS = {
        TransportType.BUS: (10.0, 95.0),
        TransportType.TRAIN: (20.0, 160.0),
        TransportType.TAXI: (12.0, 110.0),
        TransportType.SHARED_TAXI: (12.0, 100.0),
        TransportType.AUTO_RICKSHAW: (8.0, 55.0),
        TransportType.WALKING: (2.5, 6.5),
        TransportType.FLIGHT: (200.0, 950.0)
    }

    # Realistic effective fare rates per km (INR)
    RATE_BOUNDS = {
        TransportType.BUS: (0.80, 5.50),
        TransportType.TRAIN: (0.25, 4.50),
        TransportType.TAXI: (10.0, 35.0),
        TransportType.SHARED_TAXI: (2.0, 8.0),
        TransportType.AUTO_RICKSHAW: (8.0, 25.0),
        TransportType.FLIGHT: (1.5, 18.0)
    }

    @classmethod
    def validate_transport_option(
        cls,
        option: TransportOption,
        is_intercity: bool = True,
        origin_has_station: bool = True,
        dest_has_station: bool = True
    ) -> List[AnomalyReport]:
        """Audits a transit option for synthetic artifacts, impossible speeds, and rate outliers."""
        anomalies: List[AnomalyReport] = []

        # 1. Missing Provider or Source
        if not option.provider or option.provider.strip().lower() in ("unknown", "none", "placeholder"):
            anomalies.append(AnomalyReport(
                anomaly_type="PROVIDER_ANOMALY",
                message=f"Missing or placeholder provider name on option '{option.id}'",
                component_id=option.id,
                severity="critical"
            ))

        # Check for banned synthetic names
        synthetic_markers = [
            "state road transport express",
            "regional shared mobility union",
            "intercity bus fare aggregator",
            "indian railways express"
        ]
        if any(marker in option.provider.strip().lower() for marker in synthetic_markers):
            anomalies.append(AnomalyReport(
                anomaly_type="PROVIDER_ANOMALY",
                message=f"Synthetic/hallucinated provider name detected: '{option.provider}'",
                component_id=option.id,
                severity="critical"
            ))

        # 2. Negative or Suspicious Zero Fare
        if option.fare is not None:
            if option.fare < 0.0:
                anomalies.append(AnomalyReport(
                    anomaly_type="FARE_ANOMALY",
                    message=f"Negative fare detected (₹{option.fare:.2f}) on option '{option.id}'",
                    component_id=option.id,
                    severity="critical"
                ))
            elif option.fare == 0.0 and option.mode != TransportType.WALKING:
                anomalies.append(AnomalyReport(
                    anomaly_type="FARE_ANOMALY",
                    message=f"Unexpected zero fare on motorized transit '{option.id}'",
                    component_id=option.id,
                    severity="critical"
                ))

        # 3. Distance Bounds
        if is_intercity and option.distance_km > 0:
            if option.distance_km < 1.0:
                anomalies.append(AnomalyReport(
                    anomaly_type="DISTANCE_ANOMALY",
                    message=f"Intercity distance is unrealistically small ({option.distance_km:.2f} km)",
                    component_id=option.id,
                    severity="critical"
                ))

        # 4. Train Station Verification
        if option.mode == TransportType.TRAIN:
            if not origin_has_station or not dest_has_station:
                anomalies.append(AnomalyReport(
                    anomaly_type="TRAIN_STATION_ANOMALY",
                    message=f"Train option proposed between points lacking verified railway stations ({option.origin} → {option.destination})",
                    component_id=option.id,
                    severity="critical"
                ))

        # 5. Time-Distance Consistency (Physical Speed Check)
        if option.distance_km > 0 and option.duration > 0:
            hours = option.duration / 60.0
            avg_speed = option.distance_km / hours

            min_speed, max_speed = cls.SPEED_BOUNDS.get(option.mode, (5.0, 120.0))
            if avg_speed > max_speed:
                anomalies.append(AnomalyReport(
                    anomaly_type="SPEED_ANOMALY",
                    message=f"Physically impossible average speed ({avg_speed:.1f} km/h > max {max_speed} km/h) on mode {option.mode.value}",
                    component_id=option.id,
                    severity="critical"
                ))
            elif avg_speed < min_speed and option.distance_km > 15.0:
                anomalies.append(AnomalyReport(
                    anomaly_type="SPEED_ANOMALY",
                    message=f"Unusually slow transit speed ({avg_speed:.1f} km/h < min {min_speed} km/h) on mode {option.mode.value}",
                    component_id=option.id,
                    severity="warning",
                    is_rejected=False
                ))

        # 6. Fare vs Distance Consistency Check
        if option.fare is not None and option.distance_km > 2.0:
            effective_rate = option.fare / option.distance_km
            min_rate, max_rate = cls.RATE_BOUNDS.get(option.mode, (0.5, 50.0))

            if effective_rate < min_rate or effective_rate > max_rate:
                anomalies.append(AnomalyReport(
                    anomaly_type="RATE_INCONSISTENCY",
                    message=f"Fare estimate inconsistent with known tariff: ₹{effective_rate:.2f}/km for {option.mode.value} (expected ₹{min_rate:.2f}-₹{max_rate:.2f}/km)",
                    component_id=option.id,
                    severity="warning",
                    is_rejected=False
                ))

        return anomalies

    @classmethod
    def cross_verify_and_rethink(cls, option: TransportOption) -> tuple:
        """
        Cross-verifies proposed fare against deterministic distance method.
        If the fare is anomalous (>35% discrepancy from physical distance tariff),
        the agent 'rethinks' and self-corrects the fare to the official distance tariff.
        """
        from verification.fare_verifier import FareVerifier

        if not option or option.distance_km <= 0.0 or option.is_multi_leg:
            return option, False, ""

        if option.mode in (TransportType.BUS, TransportType.SHARED_TAXI):
            tariff_key = "bus_ordinary" if option.mode == TransportType.BUS else "shared_taxi"
            expected_res = FareVerifier.calculate_distance_fare(tariff_key, option.distance_km)

            if expected_res.fare is not None:
                exp_fare = expected_res.fare
                curr_fare = option.fare or 0.0

                # Check if deviation exceeds 35%
                if curr_fare <= 0.0 or abs(curr_fare - exp_fare) / max(1.0, exp_fare) > 0.35:
                    old_fare = curr_fare
                    option.fare = exp_fare
                    option.estimated = True
                    option.fare_type = "ESTIMATED"
                    rethink_msg = (
                        f"Rethink Loop: Fare on '{option.provider}' adjusted from ₹{old_fare:.0f} to ₹{exp_fare:.0f} "
                        f"using distance verification method ({option.distance_km:.1f} km road distance × gazetted tariff)."
                    )
                    if not option.fare_model_details:
                        option.fare_model_details = {}
                    option.fare_model_details["rethink_note"] = rethink_msg
                    return option, True, rethink_msg

        return option, False, ""
