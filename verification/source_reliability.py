"""Source Trust Model and Tier Reliability Evaluation."""

from typing import Dict, Any, List
from models.evidence import Evidence, SourceTier, TIER_RELIABILITY_WEIGHTS


class SourceReliabilityModel:
    """Evaluates provenance quality and enforces tier-based factual gating."""

    @staticmethod
    def get_tier_weight(tier: SourceTier) -> float:
        """Returns mathematical weight for a source tier. Tier 6 is strictly 0.0."""
        return TIER_RELIABILITY_WEIGHTS.get(tier, 0.0)

    @classmethod
    def evaluate_evidence(cls, evidence: Evidence) -> Dict[str, Any]:
        """Audits a single evidence object against strict grounding rules."""
        is_factual = evidence.tier != SourceTier.TIER_6_LLM_INFERENCE
        weight = cls.get_tier_weight(evidence.tier)
        score = round(weight * evidence.confidence, 3)

        return {
            "claim": evidence.claim,
            "tier": evidence.tier.value,
            "weight": weight,
            "confidence": evidence.confidence,
            "reliability_score": score,
            "is_valid_factual_source": is_factual and (score >= 0.60),
            "source_url": evidence.source_url or "N/A"
        }

    @classmethod
    def calculate_source_confidence(cls, evidence_list: List[Evidence]) -> float:
        """Computes aggregate source confidence score across all collected claims."""
        if not evidence_list:
            return 0.0
        scores = []
        for e in evidence_list:
            if e.tier == SourceTier.TIER_6_LLM_INFERENCE:
                scores.append(0.0)
            else:
                scores.append(cls.get_tier_weight(e.tier) * e.confidence)
        return round(sum(scores) / len(scores), 3) if scores else 0.0
