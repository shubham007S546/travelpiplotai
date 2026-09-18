"""Grounding and Evidence Audit Checker."""

from typing import List, Dict, Any
from models.evidence import Evidence, SourceTier, TIER_RELIABILITY_WEIGHTS


class GroundingChecker:
    """Verifies that all recommended entities have verifiable external evidence."""

    @classmethod
    def audit(cls, evidence_list: List[Evidence], total_recommendations: int) -> Dict[str, Any]:
        if not evidence_list:
            return {
                "grounded_claim_rate": 0.0,
                "unsupported_recommendation_rate": 1.0,
                "source_reliability_score": 0.0,
                "tier_breakdown": {},
                "is_grounded": False
            }

        total_claims = len(evidence_list)
        supported_claims = sum(1 for e in evidence_list if e.tier != SourceTier.TIER_6_LLM_INFERENCE and e.confidence >= 0.7)
        gcr = round(supported_claims / total_claims, 3) if total_claims > 0 else 0.0

        unsupported_count = total_recommendations - len(evidence_list)
        unsupported_count += sum(1 for e in evidence_list if e.tier == SourceTier.TIER_6_LLM_INFERENCE)
        unsupported_count = max(0, unsupported_count)
        urr = round(unsupported_count / max(1, total_recommendations), 3)

        # Average reliability
        rel_scores = [TIER_RELIABILITY_WEIGHTS.get(e.tier, 0.5) * e.confidence for e in evidence_list]
        avg_rel = round(sum(rel_scores) / len(rel_scores), 3) if rel_scores else 0.0

        # Tier breakdown count
        tier_counts = {}
        for e in evidence_list:
            key = e.tier.value
            tier_counts[key] = tier_counts.get(key, 0) + 1

        return {
            "grounded_claim_rate": gcr,
            "unsupported_recommendation_rate": urr,
            "source_reliability_score": avg_rel,
            "tier_breakdown": tier_counts,
            "is_grounded": gcr >= 0.85
        }
