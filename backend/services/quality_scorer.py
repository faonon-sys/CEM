"""
Assumption quality scoring and confidence metrics.
Sprint 2 - Task 6: Multi-Dimensional Quality Scoring Algorithm
"""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# Vague terms that reduce specificity score
VAGUE_TERMS = {
    "maybe", "might", "could", "possibly", "probably", "likely", "unlikely",
    "somewhat", "fairly", "relatively", "quite", "rather", "pretty",
    "generally", "usually", "often", "sometimes", "occasionally",
    "various", "several", "many", "few", "some", "certain",
    "thing", "stuff", "things", "issues", "factors", "aspects"
}

# Systemic keywords that increase impact score
SYSTEMIC_KEYWORDS = {
    "system", "systemic", "cascade", "cascading", "fundamental", "foundational",
    "critical", "infrastructure", "structural", "backbone", "core", "essential",
    "widespread", "pervasive", "comprehensive", "total", "complete", "entire",
    "network", "interconnected", "interdependent", "linked"
}


class QualityScore:
    """Quality score result with dimensions."""

    def __init__(
        self,
        composite: float,
        dimensions: Dict[str, float],
        priority_tier: str
    ):
        self.composite = composite
        self.dimensions = dimensions
        self.priority_tier = priority_tier

    def to_dict(self) -> Dict[str, Any]:
        return {
            "composite": round(self.composite, 2),
            "dimensions": {k: round(v, 2) for k, v in self.dimensions.items()},
            "priority_tier": self.priority_tier
        }


class AssumptionQualityScorer:
    """
    Multi-dimensional quality scoring for assumptions.

    Scoring Dimensions:
    1. Specificity (25%) - How concrete and measurable
    2. Verifiability (25%) - Can it be proven true/false
    3. Impact Potential (35%) - How consequential if it fails
    4. Source Strength (15%) - Quality of source evidence

    Priority Tiers:
    - High Priority: composite > 70, confidence > 0.7
    - Medium Priority: composite 40-70
    - Low Priority: composite < 40
    - Needs Review: confidence < 0.5 (regardless of quality)
    """

    def __init__(self):
        pass

    def score(self, assumption: Dict[str, Any]) -> QualityScore:
        """
        Calculate comprehensive quality score for an assumption.

        Args:
            assumption: Assumption dict with text, domains, confidence, etc.

        Returns:
            QualityScore object with composite score and dimensions
        """
        text = assumption.get("text", "")
        domains = assumption.get("domains", [])
        confidence = assumption.get("confidence", 0.5)
        source_excerpt = assumption.get("source_excerpt", "")

        # Calculate dimensional scores
        scores = {
            "specificity": self._score_specificity(text),
            "verifiability": self._score_verifiability(text),
            "impact_potential": self._score_impact(text, domains),
            "source_strength": self._score_source(source_excerpt)
        }

        # Weighted composite score
        composite = (
            scores["specificity"] * 0.25 +
            scores["verifiability"] * 0.25 +
            scores["impact_potential"] * 0.35 +
            scores["source_strength"] * 0.15
        )

        # Assign priority tier
        priority_tier = self._assign_tier(composite, confidence)

        return QualityScore(
            composite=composite,
            dimensions=scores,
            priority_tier=priority_tier
        )

    def score_batch(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Score a batch of assumptions and add quality metadata.

        Args:
            assumptions: List of assumption dicts

        Returns:
            List of assumptions enhanced with quality_score dict
        """
        scored = []

        for assumption in assumptions:
            quality = self.score(assumption)
            assumption["quality_score"] = quality.composite
            assumption["quality_dimensions"] = quality.dimensions
            assumption["priority_tier"] = quality.priority_tier
            scored.append(assumption)

        # Sort by priority
        scored.sort(
            key=lambda a: (
                0 if a["priority_tier"] == "high" else
                1 if a["priority_tier"] == "needs_review" else
                2 if a["priority_tier"] == "medium" else 3
            )
        )

        # Log statistics
        tier_counts = {}
        for assumption in scored:
            tier = assumption["priority_tier"]
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        logger.info(
            f"Scored {len(assumptions)} assumptions. "
            f"Priority distribution: {tier_counts}"
        )

        return scored

    def _score_specificity(self, text: str) -> float:
        """
        Score specificity: higher for quantifiable, specific claims.

        Args:
            text: Assumption text

        Returns:
            Score (0-100)
        """
        score = 50  # baseline

        text_lower = text.lower()

        # Check for numbers, dates, percentages
        has_numbers = bool(re.search(r'\d+', text))
        has_percentage = bool(re.search(r'\d+%', text))
        has_date = bool(re.search(r'\d{4}|january|february|march|april|may|june|july|august|september|october|november|december', text_lower))

        if has_numbers:
            score += 15
        if has_percentage:
            score += 10
        if has_date:
            score += 10

        # Check for specific entities (simple heuristic: capitalized words)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        named_entities = len(set(capitalized_words))
        score += min(named_entities * 5, 25)

        # Penalize vague terms
        vague_count = sum(1 for word in text_lower.split() if word in VAGUE_TERMS)
        score -= vague_count * 5

        # Penalize very short or very long assumptions
        word_count = len(text.split())
        if word_count < 5:
            score -= 10
        elif word_count > 40:
            score -= 5

        return max(0, min(100, score))

    def _score_verifiability(self, text: str) -> float:
        """
        Score verifiability: higher for falsifiable claims with observable consequences.

        Args:
            text: Assumption text

        Returns:
            Score (0-100)
        """
        score = 50  # baseline

        text_lower = text.lower()

        # Look for verifiable language patterns
        verifiable_patterns = [
            r'will\s+\w+',  # Future predictions
            r'can\s+be\s+\w+',  # Observable capabilities
            r'results?\s+in',  # Causal claims
            r'leads?\s+to',
            r'causes?',
            r'enables?',
            r'prevents?',
            r'increases?',
            r'decreases?',
            r'improves?',
            r'reduces?'
        ]

        for pattern in verifiable_patterns:
            if re.search(pattern, text_lower):
                score += 10

        # Check for measurable outcomes
        if re.search(r'\d+%|\d+\s*(percent|times|fold)', text_lower):
            score += 15

        # Penalize subjective language
        subjective_terms = {
            "believe", "feel", "think", "seem", "appear",
            "good", "bad", "better", "worse", "best", "worst"
        }
        subjective_count = sum(1 for word in text_lower.split() if word in subjective_terms)
        score -= subjective_count * 8

        # Check for conditional language (reduces verifiability)
        conditional_terms = {"if", "unless", "provided", "assuming", "suppose"}
        if any(term in text_lower for term in conditional_terms):
            score -= 10

        return max(0, min(100, score))

    def _score_impact(self, text: str, domains: List[str]) -> float:
        """
        Score impact potential: higher for multi-domain and systemic assumptions.

        Args:
            text: Assumption text
            domains: List of domains this assumption affects

        Returns:
            Score (0-100)
        """
        score = 30  # baseline

        # Multi-domain impact
        domain_count = len(domains) if domains else 1
        score += min(domain_count * 15, 35)

        text_lower = text.lower()

        # Systemic keywords
        systemic_count = sum(
            1 for keyword in SYSTEMIC_KEYWORDS
            if keyword in text_lower
        )
        score += min(systemic_count * 10, 30)

        # Scope indicators
        scope_indicators = {
            "all", "every", "entire", "global", "national", "widespread",
            "multiple", "across", "throughout"
        }
        scope_count = sum(1 for word in text_lower.split() if word in scope_indicators)
        score += min(scope_count * 5, 15)

        # Negative framing (risks often more impactful)
        negative_terms = {"fail", "failure", "collapse", "crisis", "disruption", "breakdown"}
        if any(term in text_lower for term in negative_terms):
            score += 10

        return max(0, min(100, score))

    def _score_source(self, source_excerpt: str) -> float:
        """
        Score source strength: higher for explicit source citations.

        Args:
            source_excerpt: Source text excerpt (if available)

        Returns:
            Score (0-100)
        """
        if not source_excerpt:
            return 30  # Default if no source provided

        score = 50  # baseline

        # Has source excerpt
        excerpt_length = len(source_excerpt.split())

        if excerpt_length > 5:
            score += 20
        elif excerpt_length > 0:
            score += 10

        # Check for quotation marks (indicates direct quote)
        if '"' in source_excerpt or '"' in source_excerpt:
            score += 15

        # Long excerpts suggest strong evidence
        if excerpt_length > 15:
            score += 15

        return max(0, min(100, score))

    def _assign_tier(self, composite: float, confidence: float) -> str:
        """
        Assign priority tier based on composite score and confidence.

        Args:
            composite: Composite quality score (0-100)
            confidence: Extraction confidence (0-1)

        Returns:
            Priority tier: "high", "medium", "low", or "needs_review"
        """
        # Flag low confidence for review regardless of quality
        if confidence < 0.5:
            return "needs_review"

        if composite >= 70 and confidence >= 0.7:
            return "high"
        elif composite >= 40:
            return "medium"
        else:
            return "low"

    def get_priority_assumptions(
        self,
        assumptions: List[Dict[str, Any]],
        tier: str = "high"
    ) -> List[Dict[str, Any]]:
        """
        Get assumptions by priority tier.

        Args:
            assumptions: List of scored assumptions
            tier: Priority tier to filter ("high", "medium", "low", "needs_review")

        Returns:
            Filtered list of assumptions
        """
        return [
            assumption for assumption in assumptions
            if assumption.get("priority_tier") == tier
        ]
