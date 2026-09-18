"""Tests for Travel Blogger Real-World Mobility, Devotional Sites, Flights, Trains & Return Parity."""

import pytest
from agents.place_resolution_agent import PlaceResolutionAgent
from services.transport_verification import TransportVerificationPipeline
from verification.fare_distance_validator import FareDistanceValidator
from models.transport import TransportType


@pytest.fixture
def transport_pipeline():
    return TransportVerificationPipeline()


@pytest.fixture
def place_agent():
    return PlaceResolutionAgent()


def test_sundernagar_manali_bidirectional_parity(place_agent, transport_pipeline):
    """Verifies Sundernagar to Manali and Manali to Sundernagar both produce ₹230 HRTC multi-leg buses."""
    src = place_agent._resolve_single_place("Sundernagar")
    dst = place_agent._resolve_single_place("Manali")

    # Outbound
    out_options, _, _ = transport_pipeline.discover_and_verify_transport(src, dst, "2026-10-01")
    out_bus_multihop = [o for o in out_options if "HRTC Ordinary Bus" in o.provider]
    assert len(out_bus_multihop) >= 1
    assert out_bus_multihop[0].fare == 230.0
    assert out_bus_multihop[0].is_multi_leg is True
    assert len(out_bus_multihop[0].legs) == 2

    # Return
    ret_options, _, _ = transport_pipeline.discover_and_verify_transport(dst, src, "2026-10-03")
    ret_bus_multihop = [o for o in ret_options if "HRTC Ordinary Bus" in o.provider]
    assert len(ret_bus_multihop) >= 1
    assert ret_bus_multihop[0].fare == 230.0
    assert ret_bus_multihop[0].is_multi_leg is True
    assert len(ret_bus_multihop[0].legs) == 2


def test_delhi_varanasi_multimodal_discovery(place_agent, transport_pipeline):
    """Verifies intercity route Delhi-Varanasi discovers trains (including Vande Bharat), flights, buses, and cabs."""
    src = place_agent._resolve_single_place("Delhi")
    dst = place_agent._resolve_single_place("Varanasi")

    options, route_res, _ = transport_pipeline.discover_and_verify_transport(src, dst, "2026-10-01")
    modes = {o.mode for o in options}

    # Must contain Flight, Train, Bus, Taxi
    assert TransportType.FLIGHT in modes
    assert TransportType.TRAIN in modes
    assert TransportType.BUS in modes
    assert TransportType.TAXI in modes

    # Train must include Vande Bharat
    vb = [o for o in options if "Vande Bharat" in o.provider]
    assert len(vb) >= 1
    assert vb[0].fare > 500.0

    # Flight must have IATA DEL to VNS
    flights = [o for o in options if o.mode == TransportType.FLIGHT]
    assert len(flights) >= 1
    assert "DEL" in flights[0].origin
    assert "VNS" in flights[0].destination

    # All options must pass FareDistanceValidator without critical rejections
    for opt in options:
        anomalies = FareDistanceValidator.validate_transport_option(opt)
        critical = [a for a in anomalies if a.severity == "critical"]
        assert len(critical) == 0, f"Option {opt.id} rejected: {[c.message for c in critical]}"


def test_delhi_mumbai_metro_connectivity(place_agent, transport_pipeline):
    """Verifies Delhi-Mumbai has direct domestic flight and Vande Bharat/Rajdhani options."""
    src = place_agent._resolve_single_place("Delhi")
    dst = place_agent._resolve_single_place("Mumbai")

    options, _, _ = transport_pipeline.discover_and_verify_transport(src, dst, "2026-10-01")
    modes = {o.mode for o in options}

    assert TransportType.FLIGHT in modes
    assert TransportType.TRAIN in modes

    # Flight duration should be realistic (~180-200 mins including taxi/takeoff buffer)
    flight = [o for o in options if o.mode == TransportType.FLIGHT][0]
    assert 120 <= flight.duration <= 240
    assert "BOM" in flight.destination


def test_devotional_trek_kedarnath_decomposition(place_agent, transport_pipeline):
    """Verifies Haridwar to Kedarnath decomposes road transit to Gaurikund base."""
    src = place_agent._resolve_single_place("Haridwar")
    dst = place_agent._resolve_single_place("Kedarnath")

    options, _, _ = transport_pipeline.discover_and_verify_transport(src, dst, "2026-10-01")
    
    # Taxi or Bus should note drop at Gaurikund / base
    taxi_opt = [o for o in options if o.mode == TransportType.TAXI][0]
    assert "gaurikund" in (taxi_opt.actual_stop or "").lower() or "base" in (taxi_opt.destination or "").lower()
