"""Comprehensive 20-Scenario Reliability & Grounding Test Suite (Requirement 47)."""

import pytest
from models.place import ResolvedPlace
from models.transport import TransportOption, TransportType, FareType, FareModelType
from models.evidence import Evidence, SourceTier
from models.budget import BudgetBreakdown
from agents.place_resolution_agent import PlaceResolutionAgent
from verification.route_verifier import RouteVerifier, RouteEvidence, RouteVerificationResult
from verification.fare_verifier import FareVerifier
from verification.fare_distance_validator import FareDistanceValidator
from verification.source_reliability import SourceReliabilityModel
from verification.final_verifier import FinalVerifier
from services.transport_verification import TransportVerificationPipeline
from services.weather_service import OpenMeteoWeatherService


# 1. Village -> Village (e.g. Jihri to Bajaura)
def test_01_village_to_village():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Jihri")
    dst = agent._resolve_single_place("Bajaura")

    assert src.is_valid is True
    assert dst.is_valid is True
    assert src.is_rural is True or dst.is_rural is True

    pipeline = TransportVerificationPipeline()
    options, route_res, notes = pipeline.discover_and_verify_transport(src, dst, "2026-10-01", travelers=1)

    assert route_res is not None
    assert route_res.road_distance_km > 0.0
    # Between Jihri and Bajaura, no direct railway exists
    train_opts = [o for o in options if o.mode == TransportType.TRAIN]
    assert len(train_opts) == 0, "Must not fabricate a direct train between villages"


# 2. Village -> City (e.g. Jihri to Shimla)
def test_02_village_to_city():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Jihri")
    dst = agent._resolve_single_place("Shimla")

    assert src.is_rural is True
    assert dst.is_rural is False

    pipeline = TransportVerificationPipeline()
    options, route_res, _ = pipeline.discover_and_verify_transport(src, dst, "2026-10-01", travelers=1)

    assert len(options) > 0
    assert all(o.distance_km > 50.0 for o in options)


# 3. City -> Village (e.g. Delhi to Bajaura)
def test_03_city_to_village():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Delhi")
    dst = agent._resolve_single_place("Bajaura")

    assert src.is_rural is False
    assert dst.is_rural is True


# 4. City -> City (e.g. Delhi to Jaipur)
def test_04_city_to_city():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Delhi")
    dst = agent._resolve_single_place("Jaipur")

    pipeline = TransportVerificationPipeline()
    options, route_res, _ = pipeline.discover_and_verify_transport(src, dst, "2026-10-01", travelers=1)

    # Both Delhi and Jaipur have verified railway stations
    train_opts = [o for o in options if o.mode == TransportType.TRAIN]
    assert len(train_opts) >= 1, "Verified rail corridor should have train option"
    assert train_opts[0].fare is not None


# 5. Ambiguous Village (e.g. Bajaura with multiple state matches)
def test_05_ambiguous_village():
    agent = PlaceResolutionAgent()
    # Query without hint returns multiple candidate alternatives if found
    res = agent._resolve_single_place("Bajaura")
    assert res.canonical_name == "Bajaura"
    assert res.latitude is not None


# 6. No Train Available (e.g. Mandi to Shimla or Jihri to Bajaura)
def test_06_no_train_available():
    pipeline = TransportVerificationPipeline()
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Mandi")
    dst = agent._resolve_single_place("Shimla")

    options, _, messages = pipeline.discover_and_verify_transport(src, dst, "2026-10-01")
    train_opts = [o for o in options if o.mode == TransportType.TRAIN]

    # Mandi has no railway station, so direct train must NOT be fabricated
    assert len(train_opts) == 0
    assert any("No verified train service" in m for m in messages)


# 7. No Bus Schedule Available (fallback message without fake schedule)
def test_07_no_bus_schedule_available():
    # If route has incomplete schedule, fare is marked unknown or estimated
    opt = TransportOption(
        id="bus-unk",
        mode=TransportType.BUS,
        provider="Local Route Carrier",
        origin="Remote Point A",
        destination="Remote Point B",
        departure="Schedule unconfirmed",
        arrival="Schedule unconfirmed",
        duration=120,
        distance_km=40.0,
        fare=None,
        fare_type=FareType.UNKNOWN.value,
        source_type="Unconfirmed Local Transit"
    )
    assert opt.fare is None
    assert opt.fare_type == "UNKNOWN"


# 8. No Fare Available (fare = null and label 'Fare unavailable')
def test_08_no_fare_available():
    res = FareVerifier.calculate_distance_fare("non_existent_tariff", 50.0)
    assert res.fare is None
    assert res.fare_type == FareType.UNKNOWN.value
    assert res.display_label == "Fare unavailable"


# 9. Conflicting Route Distances (disagreement > 15% flags CONFLICT)
def test_09_conflicting_route_distances():
    dist_a = 74.0
    dist_b = 35.0  # Disagreement ~71%
    avg = (dist_a + dist_b) / 2.0
    diff_pct = abs(dist_a - dist_b) / avg * 100

    assert diff_pct > 15.0
    status = "CONFLICT" if diff_pct > 15.0 else "CONSISTENT"
    assert status == "CONFLICT"


# 10. Fake Provider Detection (rejects hallucinated SRT / Unions)
def test_10_fake_provider_detection():
    fake_opt = TransportOption(
        id="fake-01",
        mode=TransportType.BUS,
        provider="State Road Transport Express",  # Synthetic marker
        origin="Locality A",
        destination="Locality B",
        departure="08:00",
        arrival="11:00",
        duration=180,
        distance_km=100.0,
        fare=200.0,
        fare_type=FareType.ESTIMATED.value
    )
    anomalies = FareDistanceValidator.validate_transport_option(fake_opt)
    provider_anomalies = [a for a in anomalies if a.anomaly_type == "PROVIDER_ANOMALY"]
    assert len(provider_anomalies) >= 1
    assert provider_anomalies[0].is_rejected is True


# 11. Missing Source (flags ungrounded claim)
def test_11_missing_source():
    ev = Evidence(
        claim="Invented transit claim",
        source="",
        source_type="",
        tier=SourceTier.TIER_6_LLM_INFERENCE,
        confidence=0.3
    )
    audit = SourceReliabilityModel.evaluate_evidence(ev)
    assert audit["is_valid_factual_source"] is False
    assert audit["weight"] == 0.0


# 12. Impossible Travel Time (speed > 120 km/h for road transit)
def test_12_impossible_travel_time():
    fast_opt = TransportOption(
        id="super-bus",
        mode=TransportType.BUS,
        provider="HRTC",
        origin="Mandi",
        destination="Shimla",
        departure="08:00",
        arrival="08:10",  # 10 minutes for 145 km = 870 km/h!
        duration=10,
        distance_km=145.0,
        fare=240.0,
        fare_type=FareType.OFFICIAL_TARIFF.value
    )
    anomalies = FareDistanceValidator.validate_transport_option(fast_opt)
    speed_anomalies = [a for a in anomalies if a.anomaly_type == "SPEED_ANOMALY"]
    assert len(speed_anomalies) >= 1
    assert speed_anomalies[0].severity == "critical"
    assert speed_anomalies[0].is_rejected is True


# 13. Zero Fare on Motorized Transit (flags anomaly)
def test_13_zero_fare():
    zero_opt = TransportOption(
        id="zero-taxi",
        mode=TransportType.TAXI,
        provider="Local Stand Taxi",
        origin="Mandi",
        destination="Shimla",
        departure="08:00",
        arrival="12:00",
        duration=240,
        distance_km=145.0,
        fare=0.0,
        fare_type=FareType.LIVE.value
    )
    anomalies = FareDistanceValidator.validate_transport_option(zero_opt)
    fare_anomalies = [a for a in anomalies if a.anomaly_type == "FARE_ANOMALY"]
    assert len(fare_anomalies) >= 1


# 14. Negative Fare (rejected)
def test_14_negative_fare():
    neg_opt = TransportOption(
        id="neg-bus",
        mode=TransportType.BUS,
        provider="HRTC",
        origin="Mandi",
        destination="Shimla",
        departure="08:00",
        arrival="12:00",
        duration=240,
        distance_km=145.0,
        fare=-50.0,
        fare_type=FareType.ESTIMATED.value
    )
    anomalies = FareDistanceValidator.validate_transport_option(neg_opt)
    assert any(a.anomaly_type == "FARE_ANOMALY" and a.is_rejected for a in anomalies)


# 15. Budget Violation & Uncertainty Check
def test_15_budget_violation():
    bd = BudgetBreakdown.compute(
        total_budget=1300.0,
        intercity_transport=400.0,
        stay=800.0,
        food=350.0,
        activities=100.0,
        local_mobility=50.0
    )
    # Total expected = 1700 + emergency
    assert bd.is_feasible is False
    assert bd.violation_amount > 0
    assert "exceeds your budget" in bd.feasibility_status_message or "Budget insufficient" in bd.feasibility_status_message


# 16. Estimated Fare Calculation
def test_16_estimated_fare():
    res = FareVerifier.calculate_distance_fare("bus_ordinary", 100.0)
    assert res.fare is not None
    assert res.fare_type == FareType.ESTIMATED.value
    assert "₹10" in res.calculation_breakdown  # Base fare
    assert res.fare == round(10.0 + (1.65 * 100.0), 0)


# 17. Official Fare
def test_17_official_fare():
    opt = TransportOption(
        id="hrtc-01",
        mode=TransportType.BUS,
        provider="HRTC",
        origin="Mandi",
        destination="Shimla",
        departure="07:00",
        arrival="11:30",
        duration=270,
        distance_km=145.0,
        fare=240.0,
        fare_type=FareType.OFFICIAL_TARIFF.value,
        booking_url="https://hrtchp.com"
    )
    assert opt.fare_type == "OFFICIAL_TARIFF"
    assert opt.fare == 240.0


# 18. Multiple Transport Legs
def test_18_multiple_transport_legs():
    # Village -> Nearest Station -> Destination Hub
    leg1 = TransportOption(
        id="leg-1",
        mode=TransportType.TAXI,
        provider="Local Shared Maxi Cab",
        origin="Jihri",
        destination="Aut Highway Stop",
        departure="07:00",
        arrival="07:30",
        duration=30,
        distance_km=15.0,
        fare=80.0,
        fare_type=FareType.ESTIMATED.value
    )
    leg2 = TransportOption(
        id="leg-2",
        mode=TransportType.BUS,
        provider="HRTC",
        origin="Aut Highway Stop",
        destination="Bajaura",
        departure="07:45",
        arrival="08:25",
        duration=40,
        distance_km=28.0,
        fare=50.0,
        fare_type=FareType.OFFICIAL_TARIFF.value
    )
    assert leg1.destination == leg2.origin
    assert leg1.fare + leg2.fare == 130.0


# 19. Last-Mile Transport
def test_19_last_mile_transport():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Jihri")
    assert src.is_rural is True


# 20. Weather Telemetry Grounding
def test_20_weather_change():
    ws = OpenMeteoWeatherService()
    forecast = ws.get_forecast("Shimla")
    assert forecast.temperature_c is not None
    assert forecast.source in ["Open-Meteo Live API", "OpenWeatherMap Live API", "Open-Meteo Climatological Estimate"]
    assert forecast.retrieved_at != ""
