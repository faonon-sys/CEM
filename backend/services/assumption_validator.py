"""
Sprint 3 - Task 9: Scenario Input & Assumption Validation Service

Provides backend services for scenario input processing and assumption validation,
including NLP extraction, confidence scoring, and user validation workflows.
"""

import hashlib
import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AssumptionValidator:
    """
    Handles scenario input validation and assumption extraction preprocessing.

    Features:
    - Text validation and preprocessing
    - Real-time assumption extraction preview
    - User validation workflow (accept/reject/edit)
    - Domain tag management
    - Scenario templates
    """

    def __init__(self):
        self.min_scenario_length = 100  # minimum characters
        self.max_scenario_length = 5000  # maximum characters
        self.template_library = self._load_templates()

    def validate_scenario_text(self, text: str) -> Dict:
        """
        Validates scenario input text before processing.

        Args:
            text: Raw scenario text from user input

        Returns:
            Dict with validation results and metadata
        """
        issues = []
        warnings = []

        # Length validation
        text_length = len(text.strip())
        if text_length < self.min_scenario_length:
            issues.append(f"Scenario text too short ({text_length} chars). Minimum {self.min_scenario_length} required.")
        elif text_length > self.max_scenario_length:
            issues.append(f"Scenario text too long ({text_length} chars). Maximum {self.max_scenario_length} allowed.")

        # Content quality checks
        word_count = len(text.split())
        if word_count < 50:
            warnings.append(f"Low word count ({word_count}). Consider adding more context for better analysis.")

        sentence_count = len([s for s in text.split('.') if s.strip()])
        if sentence_count < 3:
            warnings.append("Few sentences detected. More detailed scenarios yield better insights.")

        # Check for placeholder text
        placeholders = ['lorem ipsum', 'todo', 'tbd', 'placeholder', 'example text']
        text_lower = text.lower()
        found_placeholders = [p for p in placeholders if p in text_lower]
        if found_placeholders:
            warnings.append(f"Placeholder text detected: {', '.join(found_placeholders)}")

        # Extract basic metadata
        metadata = {
            "character_count": text_length,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
            "has_numbers": bool(re.search(r'\d', text)),
            "has_dates": bool(re.search(r'\b\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)),
            "content_hash": hashlib.md5(text.encode()).hexdigest()[:12]
        }

        is_valid = len(issues) == 0

        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }

    def extract_inline_assumptions(self, text: str) -> List[Dict]:
        """
        Lightweight assumption extraction for real-time preview.
        Uses rule-based heuristics before full LLM processing.

        Args:
            text: Scenario text

        Returns:
            List of candidate assumptions with confidence scores
        """
        candidates = []

        # Patterns that often indicate assumptions
        assumption_patterns = [
            (r'assume[sd]?\s+that\s+([^.]+)', 0.9),  # "assume that X"
            (r'likely\s+(?:that\s+)?([^.]+)', 0.7),  # "likely X"
            (r'expect[sd]?\s+(?:that\s+)?([^.]+)', 0.8),  # "expect X"
            (r'will\s+([^.]+)', 0.6),  # "will X"
            (r'should\s+([^.]+)', 0.5),  # "should X"
            (r'if\s+([^,]+),', 0.6),  # conditional statements
            (r'given\s+that\s+([^,]+)', 0.7),  # "given that X"
            (r'presumably\s+([^.]+)', 0.8),  # "presumably X"
        ]

        for pattern, base_confidence in assumption_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                assumption_text = match.group(1).strip()

                # Skip if too short or too long
                if len(assumption_text) < 10 or len(assumption_text) > 200:
                    continue

                candidates.append({
                    "text": assumption_text,
                    "source_excerpt": match.group(0),
                    "confidence": base_confidence,
                    "extraction_method": "pattern_based",
                    "pattern_type": pattern.split('\\')[0],
                    "position": match.start()
                })

        # Deduplicate similar assumptions
        unique_candidates = self._deduplicate_candidates(candidates)

        # Sort by confidence and position
        unique_candidates.sort(key=lambda x: (-x['confidence'], x['position']))

        return unique_candidates[:10]  # Return top 10 candidates

    def _deduplicate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Remove duplicate or highly similar assumptions."""
        if not candidates:
            return []

        unique = []
        seen_texts = set()

        for candidate in candidates:
            text_normalized = candidate['text'].lower().strip()

            # Check for exact duplicates
            if text_normalized in seen_texts:
                continue

            # Check for very similar text (simple approach)
            is_similar = False
            for existing in unique:
                existing_text = existing['text'].lower().strip()
                # If 80%+ of words overlap, consider duplicate
                words1 = set(text_normalized.split())
                words2 = set(existing_text.split())
                if words1 and words2:
                    overlap = len(words1 & words2) / min(len(words1), len(words2))
                    if overlap > 0.8:
                        is_similar = True
                        break

            if not is_similar:
                unique.append(candidate)
                seen_texts.add(text_normalized)

        return unique

    def validate_assumption_batch(
        self,
        assumptions: List[Dict],
        actions: List[Dict]
    ) -> Tuple[List[Dict], Dict]:
        """
        Process batch validation actions from user.

        Args:
            assumptions: List of assumptions to validate
            actions: List of actions (accept, reject, edit)
                Format: [{"assumption_id": "...", "action": "accept|reject|edit", "new_text": "..."}]

        Returns:
            Tuple of (updated_assumptions, statistics)
        """
        updated_assumptions = []
        stats = {
            "total_processed": 0,
            "accepted": 0,
            "rejected": 0,
            "edited": 0,
            "errors": []
        }

        # Create action lookup
        action_map = {a['assumption_id']: a for a in actions}

        for assumption in assumptions:
            assumption_id = assumption.get('id')
            stats['total_processed'] += 1

            if assumption_id not in action_map:
                # No action specified, keep as is
                updated_assumptions.append(assumption)
                continue

            action_data = action_map[assumption_id]
            action_type = action_data.get('action', '').lower()

            if action_type == 'accept':
                assumption['validated'] = True
                assumption['validation_action'] = 'accepted'
                assumption['validation_timestamp'] = datetime.utcnow().isoformat()
                updated_assumptions.append(assumption)
                stats['accepted'] += 1

            elif action_type == 'reject':
                assumption['validated'] = True
                assumption['validation_action'] = 'rejected'
                assumption['validation_timestamp'] = datetime.utcnow().isoformat()
                # Don't add to updated list (effectively removed)
                stats['rejected'] += 1

            elif action_type == 'edit':
                new_text = action_data.get('new_text', '').strip()
                if not new_text:
                    stats['errors'].append(f"No new text provided for edit action on {assumption_id}")
                    updated_assumptions.append(assumption)
                else:
                    assumption['text'] = new_text
                    assumption['validated'] = True
                    assumption['validation_action'] = 'edited'
                    assumption['original_text'] = assumption.get('text')
                    assumption['validation_timestamp'] = datetime.utcnow().isoformat()
                    updated_assumptions.append(assumption)
                    stats['edited'] += 1
            else:
                stats['errors'].append(f"Unknown action '{action_type}' for {assumption_id}")
                updated_assumptions.append(assumption)

        return updated_assumptions, stats

    def suggest_domain_tags(self, text: str) -> List[Dict]:
        """
        Suggest domain tags for scenario based on content analysis.

        Args:
            text: Scenario text

        Returns:
            List of suggested domains with confidence scores
        """
        domain_keywords = {
            "geopolitical": ["war", "conflict", "military", "diplomatic", "sanctions", "treaty", "nation", "border", "sovereignty"],
            "economic": ["market", "economy", "financial", "trade", "inflation", "gdp", "currency", "investment", "recession"],
            "technological": ["ai", "artificial intelligence", "technology", "innovation", "digital", "cyber", "automation", "software"],
            "healthcare": ["health", "medical", "pandemic", "disease", "hospital", "patient", "drug", "treatment", "vaccine"],
            "environmental": ["climate", "environment", "carbon", "emissions", "sustainability", "renewable", "pollution", "biodiversity"],
            "social": ["society", "social", "culture", "population", "migration", "inequality", "education", "employment"],
            "legal": ["law", "legal", "regulation", "compliance", "court", "legislation", "policy", "governance"],
            "infrastructure": ["infrastructure", "transportation", "energy", "utilities", "network", "construction", "supply chain"]
        }

        text_lower = text.lower()
        suggestions = []

        for domain, keywords in domain_keywords.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                confidence = min(matches / len(keywords) * 2, 1.0)  # Scale confidence
                suggestions.append({
                    "domain": domain,
                    "confidence": round(confidence, 2),
                    "keyword_matches": matches,
                    "keywords_found": [kw for kw in keywords if kw in text_lower][:5]
                })

        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:5]  # Top 5 suggested domains

    def _load_templates(self) -> List[Dict]:
        """Load scenario templates for quick start."""
        return [
            {
                "id": "geopolitical_crisis",
                "name": "Geopolitical Crisis",
                "description": "Analysis of international conflict or diplomatic tension",
                "domains": ["geopolitical", "economic", "social"],
                "template_text": "Analyze a scenario where [country/region] faces [type of crisis]. "
                               "Key stakeholders include [actors]. The immediate trigger is [event]. "
                               "Expected timeline: [duration]. Critical assumptions about stability, "
                               "international response, and escalation dynamics should be examined."
            },
            {
                "id": "tech_disruption",
                "name": "Technology Disruption",
                "description": "Impact of emerging technology on markets/society",
                "domains": ["technological", "economic", "social"],
                "template_text": "Examine the rollout of [technology] in [sector/region]. "
                               "Adoption rate assumptions: [metrics]. Key enablers: [factors]. "
                               "Potential barriers: [challenges]. Stakeholder impacts across "
                               "[affected parties] should be analyzed for hidden dependencies."
            },
            {
                "id": "market_analysis",
                "name": "Market Analysis",
                "description": "Economic trends and market behavior scenarios",
                "domains": ["economic", "technological", "social"],
                "template_text": "Analyze market dynamics in [sector] driven by [key factors]. "
                               "Supply assumptions: [conditions]. Demand drivers: [factors]. "
                               "Competitive landscape: [structure]. Regulatory environment: [framework]. "
                               "Critical price/volume/timing assumptions need interrogation."
            },
            {
                "id": "climate_event",
                "name": "Climate/Environmental Event",
                "description": "Environmental crisis or climate-related scenario",
                "domains": ["environmental", "economic", "social"],
                "template_text": "Assess scenario where [climate event] impacts [region/sector]. "
                               "Physical effects: [impacts]. Economic consequences: [outcomes]. "
                               "Adaptation capacity: [capabilities]. Policy response assumptions: [expectations]. "
                               "Infrastructure resilience and supply chain dependencies are critical."
            },
            {
                "id": "public_health",
                "name": "Public Health Crisis",
                "description": "Disease outbreak or healthcare system stress",
                "domains": ["healthcare", "social", "economic"],
                "template_text": "Analyze outbreak of [disease/condition] affecting [population]. "
                               "Transmission assumptions: [model]. Healthcare capacity: [resources]. "
                               "Intervention strategies: [measures]. Social compliance: [expectations]. "
                               "Critical dependencies on medical supply chains and behavioral responses."
            }
        ]

    def get_template(self, template_id: str) -> Optional[Dict]:
        """Retrieve scenario template by ID."""
        for template in self.template_library:
            if template['id'] == template_id:
                return template
        return None

    def get_all_templates(self) -> List[Dict]:
        """Get all available scenario templates."""
        return self.template_library


# Global instance
validator = AssumptionValidator()
