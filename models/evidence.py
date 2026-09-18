"""Evidence and Grounding Models for TravelPilot AI."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SourceTier(str, Enum):
    """
    Source reliability hierarchy for grounded travel intelligence.
    Tier 1: Official government / transport authority (Weight: 1.0)
    Tier 2: Official provider API (Weight: 0.95)
    Tier 3: Structured Maps / routing data (Weight: 0.90)
    Tier 4: Trusted travel website (Weight: 0.80)
    Tier 5: General web search (Weight: 0.65)
    Tier 6: LLM inference (Weight: 0.0 for factual claims — strictly non-factual)
    """
    TIER_1_OFFICIAL = "Tier 1: Official Government / Tourism / Transport"
    TIER_2_PROVIDER_API = "Tier 2: Official Provider APIs (Amadeus, IRCTC, etc.)"
    TIER_3_STRUCTURED_MAPS = "Tier 3: Structured Map / Routing Data (Google Maps, ORS)"
    TIER_4_TRUSTED_TRAVEL = "Tier 4: Trusted Travel Portals (TripAdvisor, Booking, Agoda)"
    TIER_5_GENERAL_WEB = "Tier 5: General Web Search (Tavily, News, Blogs)"
    TIER_6_LLM_INFERENCE = "Tier 6: LLM Inference (Unverified estimate)"


# Tier reliability weight mapping (0.0 to 1.0)
TIER_RELIABILITY_WEIGHTS: Dict[SourceTier, float] = {
    SourceTier.TIER_1_OFFICIAL: 1.0,
    SourceTier.TIER_2_PROVIDER_API: 0.95,
    SourceTier.TIER_3_STRUCTURED_MAPS: 0.90,
    SourceTier.TIER_4_TRUSTED_TRAVEL: 0.80,
    SourceTier.TIER_5_GENERAL_WEB: 0.65,
    SourceTier.TIER_6_LLM_INFERENCE: 0.0,  # Tier 6 cannot be used as factual evidence
}


class Evidence(BaseModel):
    """Encapsulates verifiable external proof for any factual claim."""
    claim: str = Field(..., description="The factual claim being supported (e.g. fare, distance, hours)")
    value: Optional[Any] = Field(default=None, description="Exact factual value supported (e.g. 72.4, 240.0)")
    source: str = Field(..., description="Name of the provider, agency, or authority")
    source_url: Optional[str] = Field(default=None, description="Direct URL, API endpoint, or official tariff notice")
    source_type: str = Field(..., description="e.g. Official API, GTFS, MapMatrix, Geocode, Tariff")
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of data retrieval"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in claim accuracy")
    verified: bool = Field(default=True, description="Whether claim passed verification audit")
    evidence_type: str = Field(default="factual", description="fare / route / lodging / safety / weather")
    tier: SourceTier = Field(default=SourceTier.TIER_2_PROVIDER_API, description="Source hierarchy tier")
    supporting_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Raw payload or supporting key-value pairs"
    )

    # Backward compatibility alias
    @property
    def url(self) -> Optional[str]:
        return self.source_url

    @property
    def reliability_score(self) -> float:
        """Returns weighted reliability based on source tier and extraction confidence."""
        base_weight = TIER_RELIABILITY_WEIGHTS.get(self.tier, 0.0)
        return round(base_weight * self.confidence, 3)

    def to_record(self, verification_status: str = "VERIFIED") -> "EvidenceRecord":
        """Converts Evidence to unified EvidenceRecord schema."""
        return EvidenceRecord(
            claim=self.claim,
            value=self.value,
            provider=self.source,
            source_url=self.source_url,
            source_type=self.source_type,
            retrieved_at=self.retrieved_at,
            freshness="fresh",
            confidence=self.confidence,
            verification_status=verification_status if self.verified else "REJECTED",
            evidence=self.supporting_data or {}
        )


class EvidenceRecord(BaseModel):
    """Unified API response and factual claim provenance record (Requirement 10)."""
    claim: str = Field(..., description="Factual claim being verified")
    value: Optional[Any] = Field(default=None, description="Exact factual value or null if unavailable")
    provider: str = Field(..., description="Real external service, agency, or authority")
    source_url: Optional[str] = Field(default=None, description="Verification source URL or endpoint")
    source_type: str = Field(..., description="Category: Official API, Geocode, Routing, Gazette Tariff, etc.")
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 retrieval timestamp"
    )
    freshness: str = Field(default="fresh", description="Freshness indicator: fresh / cached / stale")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Verification confidence (0.0 to 1.0)")
    verification_status: str = Field(
        default="VERIFIED",
        description="VERIFIED / ESTIMATED / UNKNOWN / CONFLICT / REJECTED / DATA_UNAVAILABLE"
    )
    evidence: Optional[Dict[str, Any]] = Field(
        default=None, description="Raw supporting payload, breakdown, or HTTP response headers"
    )

    def to_evidence(self, tier: SourceTier = SourceTier.TIER_2_PROVIDER_API) -> Evidence:
        """Converts EvidenceRecord to legacy Evidence model."""
        return Evidence(
            claim=self.claim,
            value=self.value,
            source=self.provider,
            source_url=self.source_url,
            source_type=self.source_type,
            retrieved_at=self.retrieved_at,
            confidence=self.confidence,
            verified=(self.verification_status in ("VERIFIED", "ESTIMATED")),
            tier=tier,
            supporting_data=self.evidence
        )

