"""
Breach Condition Trigger Engine
Sprint 4 - Task 2: LLM-Powered Breach Generation

Automatically generates plausible breach conditions from Phase 2 fragility analysis.
Maps fragilities to strategic axes and creates realistic trigger events.
"""
from typing import List, Dict, Optional, Tuple
import json
import logging
from datetime import datetime
import asyncio

from services.llm_provider import LLMProvider
from services.axis_framework import (
    get_all_axes,
    get_axes_by_fragility_type,
    get_prompt_for_axis,
    StrategicAxis
)

logger = logging.getLogger(__name__)


class BreachConditionEngine:
    """
    LLM-powered engine for generating breach conditions from fragilities.

    Key Features:
    - Semantic matching of fragilities to strategic axes
    - Context-aware breach condition generation
    - Plausibility scoring and validation
    - Fallback mechanisms for reliability
    """

    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize breach engine.

        Args:
            llm_provider: LLM provider instance for generation
        """
        self.llm = llm_provider
        self.axes = get_all_axes()

    async def generate_breach_conditions(
        self,
        fragility: Dict,
        scenario_context: Dict,
        max_breaches: int = 4
    ) -> List[Dict]:
        """
        Generate 2-4 breach conditions for a given fragility.

        Args:
            fragility: Fragility point from Phase 2 analysis
            scenario_context: Full scenario context for contextualization
            max_breaches: Maximum number of breaches to generate (default 4)

        Returns:
            List of breach condition dictionaries with axis mappings
        """
        try:
            # Step 1: Map fragility to relevant axes
            relevant_axes = await self._map_fragility_to_axes(fragility, scenario_context)
            logger.info(f"Mapped fragility {fragility.get('assumption_id')} to {len(relevant_axes)} axes")

            # Step 2: Generate breach conditions per axis
            breach_conditions = []
            for axis_id, confidence in relevant_axes[:max_breaches]:
                try:
                    breach = await self._generate_breach_for_axis(
                        fragility=fragility,
                        axis_id=axis_id,
                        scenario_context=scenario_context,
                        axis_confidence=confidence
                    )
                    if breach:
                        breach_conditions.append(breach)
                except Exception as e:
                    logger.error(f"Failed to generate breach for axis {axis_id}: {e}")
                    continue

            # Step 3: Validate and deduplicate
            validated_breaches = self._validate_breaches(breach_conditions)

            logger.info(f"Generated {len(validated_breaches)} breach conditions")
            return validated_breaches

        except Exception as e:
            logger.error(f"Breach generation failed: {e}")
            # Fallback: Return template-based breaches
            return self._generate_fallback_breaches(fragility)

    async def _map_fragility_to_axes(
        self,
        fragility: Dict,
        scenario_context: Dict
    ) -> List[Tuple[str, float]]:
        """
        Map fragility to relevant strategic axes using semantic matching.

        Args:
            fragility: Fragility point dictionary
            scenario_context: Full scenario context

        Returns:
            List of (axis_id, confidence) tuples sorted by relevance
        """
        try:
            # Use LLM for semantic matching
            prompt = self._create_axis_mapping_prompt(fragility, scenario_context)

            response = await self.llm.generate_structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "mappings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "axis": {"type": "string"},
                                    "confidence": {"type": "number"},
                                    "reasoning": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            )

            mappings = response.get("mappings", [])

            # Convert to (axis_id, confidence) tuples
            axis_matches = []
            for mapping in mappings:
                axis_name = mapping.get("axis", "")
                confidence = mapping.get("confidence", 0.5)

                # Map axis name to axis ID
                axis_id = self._get_axis_id_from_name(axis_name)
                if axis_id:
                    axis_matches.append((axis_id, confidence))

            # Sort by confidence
            axis_matches.sort(key=lambda x: x[1], reverse=True)

            # Ensure at least 2 axes if possible
            if len(axis_matches) < 2:
                # Fallback to heuristic mapping
                fragility_type = self._infer_fragility_type(fragility)
                fallback_axes = get_axes_by_fragility_type(fragility_type)
                for axis_id in fallback_axes:
                    if axis_id not in [a[0] for a in axis_matches]:
                        axis_matches.append((axis_id, 0.6))

            return axis_matches[:4]  # Return top 4

        except Exception as e:
            logger.error(f"Axis mapping failed, using fallback: {e}")
            # Fallback to heuristic mapping
            fragility_type = self._infer_fragility_type(fragility)
            fallback_axes = get_axes_by_fragility_type(fragility_type)
            return [(axis_id, 0.6) for axis_id in fallback_axes]

    async def _generate_breach_for_axis(
        self,
        fragility: Dict,
        axis_id: str,
        scenario_context: Dict,
        axis_confidence: float
    ) -> Optional[Dict]:
        """
        Generate a breach condition for a specific axis.

        Args:
            fragility: Fragility point dictionary
            axis_id: Strategic axis identifier
            scenario_context: Full scenario context
            axis_confidence: Confidence in axis mapping (0-1)

        Returns:
            Breach condition dictionary or None if generation fails
        """
        try:
            # Get axis-specific prompt
            prompt = get_prompt_for_axis(
                axis_id=axis_id,
                fragility_description=fragility.get("description", ""),
                context=self._extract_context_variables(scenario_context)
            )

            # Add additional instructions for structured output
            prompt += """

Please provide your response in the following JSON format:
{
  "trigger_event": "Specific, observable event that triggers the breach",
  "description": "Detailed description of how the breach unfolds (100-150 words)",
  "preconditions": ["Required precondition 1", "Required precondition 2", "..."],
  "plausibility": 0.65,  // 0.0-1.0 scale
  "reasoning": "Justification for plausibility score based on evidence and historical precedent"
}

The trigger_event must be:
- Specific and observable (not vague)
- Realistic given the scenario context
- Directly related to the fragility identified

The plausibility score should reflect:
- Historical precedent (if similar events have occurred)
- Current evidence from the scenario
- Expert judgment on likelihood
"""

            response = await self.llm.generate_structured_output(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "trigger_event": {"type": "string"},
                        "description": {"type": "string"},
                        "preconditions": {"type": "array", "items": {"type": "string"}},
                        "plausibility": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["trigger_event", "description", "preconditions", "plausibility"]
                }
            )

            # Construct breach condition
            breach = {
                "axis_id": axis_id,
                "fragility_id": fragility.get("id"),
                "trigger_event": response.get("trigger_event"),
                "description": response.get("description"),
                "preconditions": response.get("preconditions", []),
                "plausibility_score": float(response.get("plausibility", 0.5)),
                "reasoning": response.get("reasoning", ""),
                "metadata": {
                    "llm_model": self.llm.model_name,
                    "prompt_version": "1.0",
                    "generated_at": datetime.utcnow().isoformat(),
                    "axis_confidence": axis_confidence
                }
            }

            # Validate breach quality
            if self._is_valid_breach(breach):
                return breach
            else:
                logger.warning(f"Generated breach failed validation for axis {axis_id}")
                return None

        except Exception as e:
            logger.error(f"Breach generation failed for axis {axis_id}: {e}")
            return None

    def _create_axis_mapping_prompt(self, fragility: Dict, scenario_context: Dict) -> str:
        """Create prompt for LLM-based axis mapping."""
        axes_description = "\n".join([
            f"- **{axis.name}**: {axis.description}"
            for axis in self.axes
        ])

        prompt = f"""You are analyzing a fragility point from strategic scenario analysis.

**Scenario Context:**
{scenario_context.get('description', '')}

**Fragility Identified:**
- Description: {fragility.get('description')}
- Severity: {fragility.get('fragility_score', 0)}/10
- Breach Probability: {fragility.get('breach_probability', 0)}
- Evidence Gaps: {', '.join(fragility.get('evidence_gaps', []))}

**Strategic Axes Available:**
{axes_description}

**Task:**
Map this fragility to 2-3 most relevant strategic axes. For each axis, provide:
1. Axis name (must match one from the list above)
2. Confidence score (0.0-1.0) reflecting how well the axis applies
3. Brief reasoning (1 sentence)

Consider:
- Which axes best capture how this assumption could fail?
- What types of breach conditions would be most relevant?
- Historical patterns and domain-specific vulnerabilities

Return JSON format with "mappings" array."""

        return prompt

    def _extract_context_variables(self, scenario_context: Dict) -> Dict:
        """Extract relevant context variables for prompt customization."""
        return {
            "duration": "6 months",  # Default duration
            "actors": scenario_context.get("actors", []),
            "resources": scenario_context.get("resources", []),
            "timeframes": scenario_context.get("timeframes", [])
        }

    def _get_axis_id_from_name(self, axis_name: str) -> Optional[str]:
        """Map axis name to axis ID."""
        name_to_id = {
            "temporal shifts": "temporal_shifts",
            "actor behavior changes": "actor_behavior",
            "actor behavior": "actor_behavior",
            "resource constraint changes": "resource_constraints",
            "resource constraints": "resource_constraints",
            "structural/institutional failures": "structural_failures",
            "structural failures": "structural_failures",
            "information asymmetry changes": "information_asymmetry",
            "information asymmetry": "information_asymmetry",
            "external shocks/black swans": "external_shocks",
            "external shocks": "external_shocks"
        }
        return name_to_id.get(axis_name.lower())

    def _infer_fragility_type(self, fragility: Dict) -> str:
        """Infer fragility type from description and evidence gaps."""
        description = fragility.get("description", "").lower()
        evidence_gaps = " ".join(fragility.get("evidence_gaps", [])).lower()
        combined = description + " " + evidence_gaps

        # Keyword-based heuristic
        if any(word in combined for word in ["timeline", "deadline", "timing", "delay"]):
            return "timing_mismatch"
        elif any(word in combined for word in ["actor", "behavior", "motivation", "capability"]):
            return "capability_gap"
        elif any(word in combined for word in ["resource", "supply", "capacity", "availability"]):
            return "resource_constraint"
        elif any(word in combined for word in ["cascade", "failure", "breakdown", "collapse"]):
            return "cascade_failure"
        elif any(word in combined for word in ["information", "intelligence", "data", "knowledge"]):
            return "information_gap"
        else:
            return "assumption_weakness"

    def _is_valid_breach(self, breach: Dict) -> bool:
        """Validate breach condition quality."""
        # Check required fields
        if not breach.get("trigger_event") or len(breach["trigger_event"]) < 20:
            return False
        if not breach.get("description") or len(breach["description"]) < 50:
            return False
        if not breach.get("preconditions") or len(breach["preconditions"]) == 0:
            return False

        # Check plausibility range
        plausibility = breach.get("plausibility_score", 0)
        if plausibility < 0.0 or plausibility > 1.0:
            return False

        return True

    def _validate_breaches(self, breaches: List[Dict]) -> List[Dict]:
        """Validate and deduplicate breach conditions."""
        validated = []
        seen_triggers = set()

        for breach in breaches:
            trigger = breach.get("trigger_event", "").lower()

            # Skip duplicates
            if trigger in seen_triggers:
                continue

            # Skip if failed validation
            if not self._is_valid_breach(breach):
                continue

            seen_triggers.add(trigger)
            validated.append(breach)

        return validated

    def _generate_fallback_breaches(self, fragility: Dict) -> List[Dict]:
        """Generate template-based fallback breaches when LLM fails."""
        fragility_type = self._infer_fragility_type(fragility)
        relevant_axes = get_axes_by_fragility_type(fragility_type)

        fallback_breaches = []
        for axis_id in relevant_axes[:2]:
            fallback_breaches.append({
                "axis_id": axis_id,
                "fragility_id": fragility.get("id"),
                "trigger_event": f"Critical assumption breach via {axis_id.replace('_', ' ')}",
                "description": f"The fragility '{fragility.get('description')}' fails through {axis_id.replace('_', ' ')} mechanisms.",
                "preconditions": ["Evidence gap confirmed", "Baseline assumption invalidated"],
                "plausibility_score": 0.5,
                "reasoning": "Fallback breach condition (LLM generation failed)",
                "metadata": {
                    "fallback": True,
                    "generated_at": datetime.utcnow().isoformat()
                }
            })

        return fallback_breaches


async def generate_all_breaches(
    fragilities: List[Dict],
    scenario_context: Dict,
    llm_provider: LLMProvider
) -> Dict[str, List[Dict]]:
    """
    Generate breach conditions for all fragilities in a scenario.

    Args:
        fragilities: List of fragility points from Phase 2
        scenario_context: Full scenario context
        llm_provider: LLM provider instance

    Returns:
        Dictionary mapping fragility IDs to breach condition lists
    """
    engine = BreachConditionEngine(llm_provider)
    breach_map = {}

    for fragility in fragilities:
        fragility_id = fragility.get("id")
        try:
            breaches = await engine.generate_breach_conditions(
                fragility=fragility,
                scenario_context=scenario_context,
                max_breaches=4
            )
            breach_map[fragility_id] = breaches
            logger.info(f"Generated {len(breaches)} breaches for fragility {fragility_id}")
        except Exception as e:
            logger.error(f"Failed to generate breaches for {fragility_id}: {e}")
            breach_map[fragility_id] = []

    return breach_map

# Backwards compatibility alias for older code
BreachConditionGenerator = BreachConditionEngine

