"""
Sprint 3 - Task 2: Context-Aware Question Generation Engine

Intelligent engine that analyzes assumptions and generates contextually relevant,
probing questions by matching templates, injecting scenario context, and prioritizing
based on fragility indicators.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
import hashlib
import json

from services.question_templates import template_library, QuestionDimension
from services.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)


class GeneratedQuestion:
    """Represents a generated question with context and metadata."""

    def __init__(
        self,
        question_id: str,
        text: str,
        dimension: str,
        template_id: str,
        rationale: str,
        priority_score: float,
        assumption_ids: List[str],
        variables_used: Dict[str, str]
    ):
        self.question_id = question_id
        self.text = text
        self.dimension = dimension
        self.template_id = template_id
        self.rationale = rationale
        self.priority_score = priority_score
        self.assumption_ids = assumption_ids
        self.variables_used = variables_used

    def to_dict(self) -> Dict:
        return {
            "question_id": self.question_id,
            "text": self.text,
            "dimension": self.dimension,
            "template_id": self.template_id,
            "rationale": self.rationale,
            "priority_score": self.priority_score,
            "assumption_ids": self.assumption_ids,
            "variables_used": self.variables_used
        }


class QuestionGenerationEngine:
    """
    Multi-stage pipeline for generating contextually relevant questions.

    Pipeline stages:
    1. Semantic matching: Match assumptions to templates
    2. Context injection: Fill template variables with scenario data
    3. Prioritization: Score questions by potential impact
    4. Sequencing: Order questions for logical flow
    """

    def __init__(self):
        self.llm = get_llm_provider()
        self.min_relevance_score = 0.5
        self.default_question_count = 10

    async def generate_questions(
        self,
        scenario_text: str,
        assumptions: List[Dict],
        max_questions: int = 10,
        dimension_filter: Optional[str] = None
    ) -> Dict:
        """
        Generate prioritized questions for a scenario.

        Args:
            scenario_text: Original scenario description
            assumptions: List of extracted assumptions with metadata
            max_questions: Maximum number of questions to generate
            dimension_filter: Optional filter for specific dimension

        Returns:
            Dict with generated questions and metadata
        """
        logger.info(f"Generating questions for {len(assumptions)} assumptions")

        # Stage 1: Extract key entities and context
        scenario_context = await self._extract_scenario_context(scenario_text, assumptions)

        # Stage 2: Match assumptions to templates
        template_matches = await self._match_templates_to_assumptions(
            assumptions,
            scenario_context,
            dimension_filter
        )

        logger.info(f"Found {len(template_matches)} template matches")

        # Stage 3: Instantiate questions with context
        generated_questions = await self._instantiate_questions(
            template_matches,
            scenario_context,
            assumptions
        )

        logger.info(f"Generated {len(generated_questions)} candidate questions")

        # Stage 4: Prioritize questions
        scored_questions = self._prioritize_questions(
            generated_questions,
            assumptions,
            scenario_context
        )

        # Stage 5: Sequence questions for logical flow
        sequenced_questions = self._sequence_questions(scored_questions)

        # Stage 6: Select top N questions
        final_questions = sequenced_questions[:max_questions]

        return {
            "questions": [q.to_dict() for q in final_questions],
            "total_generated": len(generated_questions),
            "total_matched": len(template_matches),
            "scenario_context": scenario_context,
            "generation_metadata": {
                "assumptions_analyzed": len(assumptions),
                "templates_considered": len(template_library.get_all_templates()),
                "dimension_filter": dimension_filter,
                "max_questions": max_questions
            }
        }

    async def _extract_scenario_context(
        self,
        scenario_text: str,
        assumptions: List[Dict]
    ) -> Dict:
        """
        Extract key entities and context from scenario for variable substitution.

        Returns context including:
        - Key actors/organizations
        - Resources mentioned
        - Temporal markers
        - Systems/components
        - Events
        """
        # Use LLM to extract structured context
        extraction_prompt = f"""Extract key entities from this scenario analysis for question generation.

Scenario:
{scenario_text}

Assumptions:
{json.dumps([{"id": a["id"], "text": a["text"]} for a in assumptions], indent=2)}

Extract and return JSON with:
{{
  "actors": ["list of key actors, organizations, countries, stakeholders"],
  "resources": ["key resources, materials, capabilities, assets"],
  "systems": ["systems, components, infrastructure, platforms"],
  "events": ["key events, milestones, decisions mentioned"],
  "timeframes": ["temporal markers, deadlines, durations"],
  "locations": ["geographical locations, facilities"],
  "concepts": ["key abstract concepts, policies, strategies"]
}}

Focus on concrete, specific entities that can be used in question templates.
Return ONLY valid JSON."""

        try:
            response = await self.llm.generate_structured_output(
                extraction_prompt,
                temperature=0.3
            )

            context = json.loads(response)

            # Add some basic NLP extraction as fallback
            context["entities"] = self._extract_entities_basic(scenario_text)

            return context

        except Exception as e:
            logger.warning(f"Context extraction failed: {e}, using fallback")
            return self._extract_context_fallback(scenario_text, assumptions)

    def _extract_entities_basic(self, text: str) -> Dict:
        """Basic entity extraction using regex patterns."""
        entities = {
            "numbers": re.findall(r'\b\d+(?:[.,]\d+)?%?\b', text),
            "dates": re.findall(r'\b\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
            "proper_nouns": re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        }
        return entities

    def _extract_context_fallback(self, scenario_text: str, assumptions: List[Dict]) -> Dict:
        """Fallback context extraction using simple heuristics."""
        # Extract key words from assumptions
        assumption_texts = " ".join([a.get("text", "") for a in assumptions])

        words = assumption_texts.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1

        common_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]

        return {
            "actors": ["key stakeholder", "decision maker", "organization"],
            "resources": ["critical resource", "capacity", "funding"],
            "systems": ["system", "infrastructure", "platform"],
            "events": ["key event", "milestone", "decision point"],
            "timeframes": ["timeline", "deadline", "duration"],
            "common_terms": [term[0] for term in common_terms],
            "entities": self._extract_entities_basic(scenario_text)
        }

    async def _match_templates_to_assumptions(
        self,
        assumptions: List[Dict],
        scenario_context: Dict,
        dimension_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Match question templates to assumptions based on semantic relevance.

        Returns list of (template, assumption, relevance_score) tuples.
        """
        matches = []

        # Get relevant templates
        templates = template_library.get_all_templates()
        if dimension_filter:
            templates = template_library.get_by_dimension(
                QuestionDimension(dimension_filter)
            )

        # For each template, find relevant assumptions
        for template in templates:
            # Check applicability against scenario context and assumptions
            relevant_assumptions = self._find_relevant_assumptions(
                template,
                assumptions,
                scenario_context
            )

            for assumption, relevance_score in relevant_assumptions:
                if relevance_score >= self.min_relevance_score:
                    matches.append({
                        "template": template,
                        "assumption": assumption,
                        "relevance_score": relevance_score
                    })

        return matches

    def _find_relevant_assumptions(
        self,
        template: Dict,
        assumptions: List[Dict],
        scenario_context: Dict
    ) -> List[Tuple[Dict, float]]:
        """
        Find assumptions relevant to a template.

        Uses multiple signals:
        - Domain/category overlap
        - Keyword matching
        - Assumption type alignment
        """
        relevant = []

        template_domains = set(template.get("applicability", []))
        template_assumption_types = set(template.get("assumption_types", []))
        template_text_lower = template["template_text"].lower()

        for assumption in assumptions:
            score = 0.0

            # Check domain overlap
            assumption_domains = set(assumption.get("domains", []))
            domain_overlap = len(template_domains & assumption_domains)
            if domain_overlap > 0:
                score += 0.3 * min(domain_overlap / len(template_domains), 1.0)

            # Check category alignment
            assumption_category = assumption.get("category", "").lower()
            if assumption_category in template_assumption_types:
                score += 0.2

            # Check keyword matching
            assumption_text_lower = assumption.get("text", "").lower()
            template_keywords = set(template_text_lower.split())
            assumption_keywords = set(assumption_text_lower.split())
            keyword_overlap = len(template_keywords & assumption_keywords)
            if keyword_overlap > 2:
                score += 0.2 * min(keyword_overlap / 10, 1.0)

            # Boost for high-quality or high-priority assumptions
            quality_score = assumption.get("quality_score", 50) / 100.0
            score += 0.15 * quality_score

            # Boost for cross-domain assumptions (more complex)
            if assumption.get("is_cross_domain"):
                score += 0.15

            if score > 0:
                relevant.append((assumption, score))

        # Sort by relevance
        relevant.sort(key=lambda x: x[1], reverse=True)
        return relevant[:3]  # Top 3 assumptions per template

    async def _instantiate_questions(
        self,
        template_matches: List[Dict],
        scenario_context: Dict,
        assumptions: List[Dict]
    ) -> List[GeneratedQuestion]:
        """
        Instantiate question templates with context-specific variables.
        """
        generated = []

        for match in template_matches:
            template = match["template"]
            assumption = match["assumption"]
            relevance = match["relevance_score"]

            # Extract variables needed for template
            variables = template["variables"]
            variable_values = self._extract_variable_values(
                variables,
                assumption,
                scenario_context
            )

            # Generate question text
            question_text = self._fill_template(
                template["template_text"],
                variable_values
            )

            # Generate rationale
            rationale = f"This question probes {template['explanation']} " \
                       f"Targets assumption: '{assumption.get('text', '')[:100]}...'"

            # Create question ID
            question_id = self._generate_question_id(
                template["template_id"],
                assumption["id"]
            )

            question = GeneratedQuestion(
                question_id=question_id,
                text=question_text,
                dimension=template["dimension"],
                template_id=template["template_id"],
                rationale=rationale,
                priority_score=relevance,  # Initial score from matching
                assumption_ids=[assumption["id"]],
                variables_used=variable_values
            )

            generated.append(question)

        return generated

    def _extract_variable_values(
        self,
        variables: List[str],
        assumption: Dict,
        scenario_context: Dict
    ) -> Dict[str, str]:
        """
        Extract or generate values for template variables from context.
        """
        values = {}

        for var in variables:
            # Try to find appropriate value from context
            var_lower = var.lower()

            if "actor" in var_lower:
                values[var] = self._select_from_context(scenario_context.get("actors", []), "actor")
            elif "resource" in var_lower:
                values[var] = self._select_from_context(scenario_context.get("resources", []), "resource")
            elif "system" in var_lower or "component" in var_lower:
                values[var] = self._select_from_context(scenario_context.get("systems", []), "system")
            elif "event" in var_lower:
                values[var] = self._select_from_context(scenario_context.get("events", []), "event")
            elif "time" in var_lower or "duration" in var_lower:
                values[var] = self._select_from_context(scenario_context.get("timeframes", []), "6 months")
            elif "percentage" in var_lower:
                values[var] = "25"
            elif "location" in var_lower:
                values[var] = self._select_from_context(scenario_context.get("locations", []), "key location")
            else:
                # Generic fallback
                values[var] = self._extract_from_assumption(assumption, var)

        return values

    def _select_from_context(self, context_list: List[str], default: str) -> str:
        """Select appropriate value from context list."""
        if context_list:
            return context_list[0]
        return default

    def _extract_from_assumption(self, assumption: Dict, variable: str) -> str:
        """Extract value from assumption text."""
        text = assumption.get("text", "")
        # Simple heuristic: use first noun phrase
        words = text.split()
        if len(words) > 2:
            return " ".join(words[:3])
        return "this element"

    def _fill_template(self, template_text: str, variables: Dict[str, str]) -> str:
        """Fill template with variable values."""
        result = template_text
        for var, value in variables.items():
            placeholder = f"{{{var}}}"
            result = result.replace(placeholder, value)
        return result

    def _generate_question_id(self, template_id: str, assumption_id: str) -> str:
        """Generate unique question ID."""
        combined = f"{template_id}_{assumption_id}"
        hash_suffix = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"q_{template_id}_{hash_suffix}"

    def _prioritize_questions(
        self,
        questions: List[GeneratedQuestion],
        assumptions: List[Dict],
        scenario_context: Dict
    ) -> List[GeneratedQuestion]:
        """
        Score questions by potential impact and assign final priorities.

        Scoring factors:
        - Template severity focus
        - Assumption quality/confidence
        - Cross-domain coverage
        - Gap coverage (dimensions not yet covered)
        """
        # Track dimension coverage
        dimension_coverage = {dim.value: 0 for dim in QuestionDimension}

        for question in questions:
            score = question.priority_score  # Start with relevance score

            # Boost for high-severity focus
            template = template_library.get_template_by_id(question.template_id)
            if template:
                severity = template.get("severity_focus")
                if severity in ["cascade_failure", "concentration_risk"]:
                    score += 0.2

            # Boost for targeting high-quality assumptions
            for assumption_id in question.assumption_ids:
                assumption = next((a for a in assumptions if a["id"] == assumption_id), None)
                if assumption:
                    quality = assumption.get("quality_score", 50) / 100.0
                    score += 0.15 * quality

            # Boost for dimension coverage gaps
            dim_count = dimension_coverage.get(question.dimension, 0)
            if dim_count < 3:  # Ensure minimum coverage per dimension
                score += 0.15 * (3 - dim_count)

            # Update dimension coverage
            dimension_coverage[question.dimension] += 1

            # Update question score
            question.priority_score = min(score, 1.0)

        # Sort by priority
        questions.sort(key=lambda q: q.priority_score, reverse=True)
        return questions

    def _sequence_questions(self, questions: List[GeneratedQuestion]) -> List[GeneratedQuestion]:
        """
        Sequence questions for logical flow.

        Strategy:
        - Start with foundational questions (structural, temporal)
        - Interleave dimensions for variety
        - Group related questions
        """
        if not questions:
            return []

        # Dimension order preference
        dimension_order = [
            QuestionDimension.STRUCTURAL.value,
            QuestionDimension.TEMPORAL.value,
            QuestionDimension.ACTOR_BASED.value,
            QuestionDimension.RESOURCE_BASED.value
        ]

        # Group by dimension
        by_dimension = {dim: [] for dim in dimension_order}
        for q in questions:
            if q.dimension in by_dimension:
                by_dimension[q.dimension].append(q)

        # Interleave dimensions
        sequenced = []
        max_per_dimension = max(len(qs) for qs in by_dimension.values()) if by_dimension.values() else 0

        for i in range(max_per_dimension):
            for dim in dimension_order:
                dim_questions = by_dimension[dim]
                if i < len(dim_questions):
                    sequenced.append(dim_questions[i])

        return sequenced


# Global instance
question_engine = QuestionGenerationEngine()
