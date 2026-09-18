"""Unit tests for evidence grounding and source reliability tiers."""

from models.evidence import Evidence, SourceTier, TIER_RELIABILITY_WEIGHTS
from verification.grounding_checker import GroundingChecker


def test_evidence_tier_reliability_hierarchy():
    """Confirms that Tier 1 (Official) yields higher reliability than Tier 6 (LLM)."""
    ev_official = Evidence(
        claim="HRTC Bus Fare ₹240",
        source="HRTC Schedule",
        source_type="Official",
        tier=SourceTier.TIER_1_OFFICIAL,
        confidence=1.0
    )
    ev_llm = Evidence(
        claim="Estimated fare ~₹300",
        source="LLM Estimation",
        source_type="Inference",
        tier=SourceTier.TIER_6_LLM_INFERENCE,
        confidence=0.5
    )

    assert ev_official.reliability_score > ev_llm.reliability_score
    assert ev_official.reliability_score == 1.0
    assert ev_llm.reliability_score == round(TIER_RELIABILITY_WEIGHTS[SourceTier.TIER_6_LLM_INFERENCE] * 0.5, 3)


def test_grounding_checker_metrics():
    """Verifies GCR (Grounded Claim Rate) and URR (Unsupported Recommendation Rate)."""
    ev_list = [
        Evidence(
            claim="Hotel room ₹850",
            source="HP Tourism",
            source_type="API",
            tier=SourceTier.TIER_1_OFFICIAL,
            confidence=0.95
        ),
        Evidence(
            claim="Transit ₹240",
            source="HRTC Tariff",
            source_type="Schedule",
            tier=SourceTier.TIER_1_OFFICIAL,
            confidence=0.98
        )
    ]

    audit = GroundingChecker.audit(evidence_list=ev_list, total_recommendations=2)
    assert audit["grounded_claim_rate"] == 1.0
    assert audit["unsupported_recommendation_rate"] == 0.0
    assert audit["is_grounded"] is True
    assert audit["source_reliability_score"] >= 0.90
