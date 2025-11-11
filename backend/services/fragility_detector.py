"""
Sprint 3 - Task 3: Fragility Detection and Scoring Algorithm

Analyzes user responses to generated questions and identifies fragility points—
assumptions showing high sensitivity to challenge, lack of evidence, or cascading dependencies.
"""

import logging
import re
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FragilityPoint:
    """Represents an identified fragility in an assumption."""

    def __init__(
        self,
        assumption_id: str,
        fragility_score: float,
        breach_probability: float,
        impact_radius: List[str],
        evidence_gaps: List[str],
        markers: List[Dict]
    ):
        self.assumption_id = assumption_id
        self.fragility_score = fragility_score  # 1-10 scale
        self.breach_probability = breach_probability  # 0-1
        self.impact_radius = impact_radius  # dependent assumption IDs
        self.evidence_gaps = evidence_gaps
        self.markers = markers  # linguistic markers of uncertainty

    def to_dict(self) -> Dict:
        return {
            "assumption_id": self.assumption_id,
            "fragility_score": round(self.fragility_score, 2),
            "breach_probability": round(self.breach_probability, 3),
            "impact_radius": self.impact_radius,
            "evidence_gaps": self.evidence_gaps,
            "markers": self.markers,
            "severity": self._get_severity_label()
        }

    def _get_severity_label(self) -> str:
        """Convert score to severity label."""
        if self.fragility_score >= 8.0:
            return "critical"
        elif self.fragility_score >= 6.0:
            return "high"
        elif self.fragility_score >= 4.0:
            return "medium"
        else:
            return "low"


class FragilityDetector:
    """
    Multi-factor fragility scoring algorithm.

    Fragility Score = (
        0.4 * evidence_weakness +
        0.3 * dependency_count_normalized +
        0.2 * response_uncertainty +
        0.1 * breach_likelihood
    )
    """

    def __init__(self):
        # Linguistic markers of uncertainty
        self.uncertainty_markers = [
            "maybe", "possibly", "perhaps", "might", "could", "uncertain",
            "not sure", "unclear", "probably", "likely", "assume", "guess",
            "think", "believe", "hope", "seems", "appears"
        ]

        self.hedge_words = [
            "somewhat", "relatively", "fairly", "quite", "rather",
            "approximately", "roughly", "around", "about"
        ]

        self.weak_evidence_markers = [
            "no data", "limited evidence", "anecdotal", "unverified",
            "unconfirmed", "speculation", "assumption", "hearsay"
        ]

    def analyze_responses(
        self,
        questions_and_responses: List[Dict],
        assumptions: List[Dict],
        dependency_graph: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze user responses to identify fragility points.

        Args:
            questions_and_responses: List of {question, response, confidence} dicts
            assumptions: List of assumptions being interrogated
            dependency_graph: Optional graph of assumption dependencies

        Returns:
            Dict with fragility analysis results
        """
        logger.info(f"Analyzing {len(questions_and_responses)} responses for fragilities")

        fragility_points = []
        assumption_scores = {}

        # Build assumption ID lookup
        assumption_map = {a["id"]: a for a in assumptions}

        for qa in questions_and_responses:
            question = qa.get("question", {})
            response = qa.get("response", {})

            assumption_ids = question.get("assumption_ids", [])
            response_text = response.get("text", "")
            response_confidence = response.get("confidence", 0.5)

            for assumption_id in assumption_ids:
                if assumption_id not in assumption_map:
                    continue

                assumption = assumption_map[assumption_id]

                # Calculate fragility components
                evidence_weakness = self._analyze_evidence_weakness(
                    response_text,
                    response_confidence
                )

                response_uncertainty = self._analyze_response_uncertainty(
                    response_text
                )

                dependency_count = self._get_dependency_score(
                    assumption_id,
                    dependency_graph
                )

                breach_likelihood = self._estimate_breach_likelihood(
                    evidence_weakness,
                    response_uncertainty,
                    response_confidence
                )

                # Calculate composite fragility score (1-10 scale)
                raw_score = (
                    0.4 * evidence_weakness +
                    0.3 * dependency_count +
                    0.2 * response_uncertainty +
                    0.1 * breach_likelihood
                )
                fragility_score = raw_score * 10  # Scale to 1-10

                # Extract linguistic markers
                markers = self._extract_markers(response_text)

                # Identify evidence gaps
                evidence_gaps = self._identify_evidence_gaps(
                    response_text,
                    question.get("text", "")
                )

                # Get impact radius from dependency graph
                impact_radius = self._get_impact_radius(
                    assumption_id,
                    dependency_graph
                )

                # Store or update score for this assumption
                if assumption_id not in assumption_scores:
                    assumption_scores[assumption_id] = []

                assumption_scores[assumption_id].append({
                    "fragility_score": fragility_score,
                    "breach_probability": breach_likelihood,
                    "evidence_gaps": evidence_gaps,
                    "markers": markers,
                    "impact_radius": impact_radius
                })

        # Aggregate scores for assumptions with multiple questions
        for assumption_id, scores in assumption_scores.items():
            # Average fragility score across questions
            avg_fragility = sum(s["fragility_score"] for s in scores) / len(scores)

            # Max breach probability (conservative)
            max_breach = max(s["breach_probability"] for s in scores)

            # Union of evidence gaps
            all_gaps = []
            for s in scores:
                all_gaps.extend(s["evidence_gaps"])
            unique_gaps = list(set(all_gaps))

            # Union of markers
            all_markers = []
            for s in scores:
                all_markers.extend(s["markers"])

            # Union of impact radius
            all_impact = []
            for s in scores:
                all_impact.extend(s["impact_radius"])
            unique_impact = list(set(all_impact))

            fragility = FragilityPoint(
                assumption_id=assumption_id,
                fragility_score=avg_fragility,
                breach_probability=max_breach,
                impact_radius=unique_impact,
                evidence_gaps=unique_gaps,
                markers=all_markers
            )

            fragility_points.append(fragility)

        # Sort by fragility score
        fragility_points.sort(key=lambda f: f.fragility_score, reverse=True)

        return {
            "fragility_points": [f.to_dict() for f in fragility_points],
            "summary": {
                "total_analyzed": len(assumptions),
                "fragilities_found": len(fragility_points),
                "critical_count": sum(1 for f in fragility_points if f.fragility_score >= 8.0),
                "high_count": sum(1 for f in fragility_points if 6.0 <= f.fragility_score < 8.0),
                "medium_count": sum(1 for f in fragility_points if 4.0 <= f.fragility_score < 6.0),
                "average_fragility": sum(f.fragility_score for f in fragility_points) / len(fragility_points) if fragility_points else 0
            },
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    def _analyze_evidence_weakness(self, response_text: str, confidence: float) -> float:
        """
        Analyze strength of evidence in response (0-1 scale, higher = weaker).

        Factors:
        - Presence of weak evidence markers
        - Response length (very short = weak)
        - Confidence score
        - Specificity
        """
        text_lower = response_text.lower()
        score = 0.0

        # Check for weak evidence markers
        weak_markers_found = sum(1 for marker in self.weak_evidence_markers if marker in text_lower)
        score += min(weak_markers_found * 0.2, 0.4)

        # Response length (very short responses indicate weak support)
        word_count = len(response_text.split())
        if word_count < 20:
            score += 0.3
        elif word_count < 50:
            score += 0.15

        # Inverse confidence
        score += (1.0 - confidence) * 0.4

        # Check for specificity (numbers, dates, names)
        has_numbers = bool(re.search(r'\d', response_text))
        has_dates = bool(re.search(r'\b\d{4}\b', response_text))
        has_proper_nouns = bool(re.search(r'\b[A-Z][a-z]+\b', response_text))

        specificity_count = sum([has_numbers, has_dates, has_proper_nouns])
        if specificity_count == 0:
            score += 0.2
        elif specificity_count == 1:
            score += 0.1

        return min(score, 1.0)

    def _analyze_response_uncertainty(self, response_text: str) -> float:
        """
        Detect linguistic markers of uncertainty (0-1 scale).
        """
        text_lower = response_text.lower()
        score = 0.0

        # Count uncertainty markers
        uncertainty_count = sum(1 for marker in self.uncertainty_markers if marker in text_lower)
        score += min(uncertainty_count * 0.15, 0.5)

        # Count hedge words
        hedge_count = sum(1 for hedge in self.hedge_words if hedge in text_lower)
        score += min(hedge_count * 0.1, 0.3)

        # Check for conditional language
        conditionals = ["if", "unless", "provided that", "assuming", "depends on"]
        conditional_count = sum(1 for cond in conditionals if cond in text_lower)
        score += min(conditional_count * 0.1, 0.2)

        return min(score, 1.0)

    def _get_dependency_score(self, assumption_id: str, dependency_graph: Optional[Dict]) -> float:
        """
        Calculate normalized dependency count (0-1 scale).

        Higher score = more dependencies = higher fragility.
        """
        if not dependency_graph:
            return 0.3  # Default moderate score

        # Count outgoing dependencies (what depends on this assumption)
        relationships = dependency_graph.get("relationships", [])
        dependency_count = 0

        for rel in relationships:
            if rel.get("assumption_a_id") == assumption_id and rel.get("type") == "depends_on":
                dependency_count += 1

        # Normalize (assume max 10 dependencies for scaling)
        max_dependencies = 10
        return min(dependency_count / max_dependencies, 1.0)

    def _estimate_breach_likelihood(
        self,
        evidence_weakness: float,
        uncertainty: float,
        confidence: float
    ) -> float:
        """
        Estimate probability that assumption will fail (0-1).
        """
        # Weighted combination
        breach = (
            0.5 * evidence_weakness +
            0.3 * uncertainty +
            0.2 * (1.0 - confidence)
        )
        return min(breach, 1.0)

    def _extract_markers(self, response_text: str) -> List[Dict]:
        """Extract uncertainty and hedge markers with positions."""
        markers = []
        text_lower = response_text.lower()

        for marker in self.uncertainty_markers + self.hedge_words:
            if marker in text_lower:
                # Find all occurrences
                start = 0
                while True:
                    pos = text_lower.find(marker, start)
                    if pos == -1:
                        break
                    markers.append({
                        "type": "uncertainty" if marker in self.uncertainty_markers else "hedge",
                        "text": marker,
                        "position": pos,
                        "confidence": 0.8
                    })
                    start = pos + 1

        return markers[:10]  # Limit to top 10

    def _identify_evidence_gaps(self, response_text: str, question_text: str) -> List[str]:
        """Identify specific evidence gaps mentioned in response."""
        gaps = []
        text_lower = response_text.lower()

        gap_patterns = [
            "don't know",
            "no data",
            "no evidence",
            "unclear",
            "uncertain",
            "not documented",
            "not measured",
            "not tracked",
            "missing",
            "lack of",
            "no information"
        ]

        for pattern in gap_patterns:
            if pattern in text_lower:
                # Extract context around the gap
                pos = text_lower.find(pattern)
                start = max(0, pos - 30)
                end = min(len(response_text), pos + 50)
                context = response_text[start:end].strip()
                gaps.append(context)

        return gaps[:5]  # Top 5 gaps

    def _get_impact_radius(self, assumption_id: str, dependency_graph: Optional[Dict]) -> List[str]:
        """
        Get list of assumptions that depend on this one (impact radius).
        """
        if not dependency_graph:
            return []

        relationships = dependency_graph.get("relationships", [])
        dependent_ids = []

        for rel in relationships:
            # If other assumptions depend on this one
            if rel.get("assumption_a_id") != assumption_id and rel.get("assumption_b_id") == assumption_id:
                if rel.get("type") == "depends_on":
                    dependent_ids.append(rel.get("assumption_a_id"))

        return list(set(dependent_ids))


# Global instance
fragility_detector = FragilityDetector()
