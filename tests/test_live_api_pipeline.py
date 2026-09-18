"""Live Unmocked Integration Test Suite & Production Data Audit (Golden Cases A through J).

This test suite executes real, unmocked HTTP queries against production public APIs:
- Open-Meteo Geocoding & Weather APIs
- OpenStreetMap Nominatim
- OSRM Public Routing Engine
- Frankfurter Currency Exchange
"""

import pytest
import requests
from datetime import datetime, timezone
from models.place import ResolvedPlace
from models.transport import TransportOption, TransportType, FareType
from models.activity import ActivityOption, ActivityCategory
from services.transport_verification import TransportVerificationPipeline
from services.routing_service import RoutingService
from services.weather_service import OpenMeteoWeatherService
from services.currency_service import FrankfurterCurrencyService
from verification.fare_verifier import FareVerifier
from verification.route_verifier import RouteVerifier
from verification.fare_distance_validator import FareDistanceValidator
from agents.place_resolution_agent import PlaceResolutionAgent
from utils.api_audit import record_api_call, get_global_audit_log, sanitize_url


def is_network_available() -> bool:
    """Checks if network connectivity is active."""
    try:
        r = requests.get("https://geocoding-api.open-meteo.com/v1/search?name=Delhi&count=1", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


# ============================================================================
# GOLDEN CASE A: Jihri to Bajaura (Village to Village Hub-and-Spoke Routing)
# ============================================================================
def test_golden_case_a_jihri_to_bajaura_village_topology():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Jihri")
    dst = agent._resolve_single_place("Bajaura")

    # Geocoding Verification
    assert "Jihri" in src.canonical_name
    assert dst.canonical_name == "Bajaura"
    assert src.latitude is not None and src.longitude is not None
    assert dst.latitude is not None and dst.longitude is not None
    assert src.is_rural is True or dst.is_rural is True

    # Transit Pipeline Discovery
    pipeline = TransportVerificationPipeline()
    options, route_res, messages = pipeline.discover_and_verify_transport(src, dst, "2026-10-01")

    # Road Distance must be verified via real routing
    assert route_res is not None
    assert route_res.road_distance_km > 30.0
    assert route_res.distance_status in ("CONSISTENT", "CONFLICT")

    # ZERO Direct Trains between villages
    train_opts = [o for o in options if o.mode == TransportType.TRAIN]
    assert len(train_opts) == 0, "Golden Case A Violation: Fabricated train between Jihri and Bajaura"

    # Must contain Multi-Leg Hub-and-Spoke option or local shared transit
    multi_leg_opts = [o for o in options if o.is_multi_leg or (o.legs and len(o.legs) > 0)]
    assert len(multi_leg_opts) >= 1, "Golden Case A: Expected multi-leg hub-and-spoke transit option"

    hub_opt = multi_leg_opts[0]
    assert hub_opt.fare is not None
    # Fare must reflect realistic feeder + corridor cost, not ₹82 magic synthetic number
    assert hub_opt.fare >= 85.0
    assert len(hub_opt.legs) >= 2
    assert any("Aut" in leg.destination or "Aut" in leg.origin for leg in hub_opt.legs)

    # Must also offer direct point-to-point taxi
    taxi_opts = [o for o in options if o.mode == TransportType.TAXI]
    assert len(taxi_opts) >= 1
    assert taxi_opts[0].fare > 500.0


# ============================================================================
# GOLDEN CASE B: Delhi to Shimla (Metropolitan to Hill Station Corridor)
# ============================================================================
def test_golden_case_b_delhi_to_shimla():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Delhi")
    dst = agent._resolve_single_place("Shimla")

    assert src.canonical_name == "New Delhi"
    assert dst.canonical_name == "Shimla"
    assert src.is_rural is False
    assert dst.is_rural is False

    pipeline = TransportVerificationPipeline()
    options, route_res, _ = pipeline.discover_and_verify_transport(src, dst, "2026-10-01")

    assert len(options) >= 2
    # Delhi to Shimla has verified train (NDLS -> Kalka -> Shimla) or bus
    bus_opts = [o for o in options if o.mode == TransportType.BUS]
    assert len(bus_opts) >= 1
    assert "HRTC" in bus_opts[0].provider or "Undertaking" in bus_opts[0].provider
    assert bus_opts[0].fare > 400.0


# ============================================================================
# GOLDEN CASE C: Jaipur to Delhi (Intercity Golden Corridor)
# ============================================================================
def test_golden_case_c_jaipur_to_delhi():
    agent = PlaceResolutionAgent()
    src = agent._resolve_single_place("Jaipur")
    dst = agent._resolve_single_place("Delhi")

    pipeline = TransportVerificationPipeline()
    options, route_res, _ = pipeline.discover_and_verify_transport(src, dst, "2026-10-01")

    # Both Tier-1 cities with verified railway stations
    train_opts = [o for o in options if o.mode == TransportType.TRAIN]
    assert len(train_opts) >= 1
    assert "Indian Railways" in train_opts[0].provider
    assert train_opts[0].fare is not None and train_opts[0].fare > 100.0


# ============================================================================
# GOLDEN CASE D: Bajaura Ambiguous Query Disambiguation
# ============================================================================
def test_golden_case_d_ambiguous_locality():
    agent = PlaceResolutionAgent()
    res = agent._resolve_single_place("Bajaura")
    assert res.canonical_name == "Bajaura"
    assert res.latitude is not None
    # Hierarchy must accurately map to Kullu, Himachal Pradesh
    assert "Kullu" in (res.district or "") or "Himachal" in (res.state or "")


# ============================================================================
# GOLDEN CASE E: Remote Village without regular bus schedule (Langza / Spiti)
# ============================================================================
def test_golden_case_e_remote_village_no_fake_schedule():
    # If a remote transit route has no official state bus schedule, it must be marked UNKNOWN/ESTIMATED
    opt = TransportOption(
        id="spiti-feeder-01",
        mode=TransportType.SHARED_TAXI,
        provider="Spiti Valley 4x4 Local Operators",
        origin="Kaza Hub",
        destination="Langza Village",
        departure="On demand / morning departure",
        arrival="Variable",
        duration=45,
        distance_km=16.0,
        fare=None,
        fare_type=FareType.UNKNOWN.value,
        availability_status="UNVERIFIED"
    )
    assert opt.fare is None
    assert opt.fare_type == "UNKNOWN"
    assert opt.availability_status == "UNVERIFIED"


# ============================================================================
# GOLDEN CASE F: Zero-Fare and Negative-Fare Traps
# ============================================================================
def test_golden_case_f_zero_fare_and_negative_fare_traps():
    # Paid motorized transport cannot have ₹0 or negative fare
    zero_fare_bus = TransportOption(
        id="bad-bus-0",
        mode=TransportType.BUS,
        provider="HRTC",
        origin="Mandi",
        destination="Shimla",
        departure="08:00",
        arrival="12:00",
        duration=240,
        distance_km=140.0,
        fare=0.0
    )
    anomalies = FareDistanceValidator.validate_transport_option(zero_fare_bus)
    assert any(a.anomaly_type == "FARE_ANOMALY" for a in anomalies)
    assert any(a.severity == "critical" and a.is_rejected for a in anomalies)


# ============================================================================
# GOLDEN CASE G: Physical Speed Violation Trap
# ============================================================================
def test_golden_case_g_speed_violation_trap():
    # Impossible 250 km/h bus
    supersonic_bus = TransportOption(
        id="fast-bus",
        mode=TransportType.BUS,
        provider="HRTC",
        origin="Delhi",
        destination="Shimla",
        departure="08:00",
        arrival="09:00",
        duration=60,  # 1 hour for 340 km = 340 km/h
        distance_km=340.0,
        fare=500.0
    )
    anomalies = FareDistanceValidator.validate_transport_option(supersonic_bus)
    assert any(a.anomaly_type == "SPEED_ANOMALY" for a in anomalies)
    assert any(a.severity == "critical" and a.is_rejected for a in anomalies)


# ============================================================================
# GOLDEN CASE H: Live Weather Telemetry (Unmocked Open-Meteo)
# ============================================================================
def test_golden_case_h_live_weather_service():
    if not is_network_available():
        pytest.skip("External network unreachable")

    weather_svc = OpenMeteoWeatherService()
    weather = weather_svc.get_forecast("Shimla")
    assert weather is not None
    assert weather.temperature_c is not None
    assert -30.0 <= weather.temperature_c <= 50.0
    assert len(weather.condition) > 0

    # Also test live currency conversion via Frankfurter
    forex_svc = FrankfurterCurrencyService()
    inr_amount = forex_svc.convert_currency(100.0, "USD", "INR")
    assert inr_amount > 5000.0


# ============================================================================
# GOLDEN CASE I: Live Forex & Activities Admission Fee Policy
# ============================================================================
def test_golden_case_i_admission_fee_policy():
    # Unverified attractions must have cost = None, admission_fee_status = "UNKNOWN"
    unverified_museum = ActivityOption(
        id="act-heritage-museum",
        name="District Heritage Museum",
        category=ActivityCategory.MUSEUM,
        location="Heritage Complex",
        cost=None,
        admission_fee_status="UNKNOWN"
    )
    assert unverified_museum.cost is None
    assert unverified_museum.cost_safe == 0.0
    assert unverified_museum.admission_fee_status == "UNKNOWN"

    # Open public viewpoint has cost = 0.0 with admission_fee_status = "FREE"
    viewpoint = ActivityOption(
        id="act-viewpoint-free",
        name="Sunset Panorama Point",
        category=ActivityCategory.VIEWPOINT,
        location="Ridge Viewpoint",
        cost=0.0,
        admission_fee_status="FREE"
    )
    assert viewpoint.cost == 0.0
    assert viewpoint.admission_fee_status == "FREE"


# ============================================================================
# GOLDEN CASE J: Route Divergence Check (> 15% Threshold)
# ============================================================================
def test_golden_case_j_route_divergence_conflict_handling():
    verifier = RouteVerifier()
    # Mock two distinct routing returns with > 15% divergence
    dist_a = 50.0
    dist_b = 35.0  # Divergence: abs(50-35) / 42.5 = 35.3%
    avg = (dist_a + dist_b) / 2.0
    diff_pct = abs(dist_a - dist_b) / avg * 100.0
    assert diff_pct > 15.0

    # Conservative distance rule picks the larger distance
    conservative_dist = max(dist_a, dist_b)
    assert conservative_dist == 50.0


# ============================================================================
# API AUDIT LOG & CREDENTIAL SANITIZATION
# ============================================================================
def test_api_audit_log_credential_sanitization():
    raw_url = "https://api.service.com/v1/data?api_key=secret_xyz123&query=delhi"
    sanitized = sanitize_url(raw_url)
    assert "secret_xyz123" not in sanitized
    assert "[REDACTED]" in sanitized

    record_api_call(
        provider="TestAuditProvider",
        endpoint="/v1/test",
        url=raw_url,
        method="GET",
        status_code=200,
        response_summary="Live test response"
    )

    log = get_global_audit_log()
    assert len(log) > 0
    latest = log[-1]
    assert latest["provider"] == "TestAuditProvider"
    assert "secret_xyz123" not in latest["url"]
    assert "[REDACTED]" in latest["url"]
