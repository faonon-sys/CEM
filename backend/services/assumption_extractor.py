"""
Enhanced assumption extraction service with structured output and quality controls.
Sprint 2 - Task 1: LLM-based Assumption Extraction Engine
"""
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional
from services.llm_provider import get_llm_provider
from utils.prompts import REASONING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class AssumptionExtractor:
    """
    Advanced assumption extractor with:
    - Structured JSON output via function calling
    - Consistency validation (dual extraction)
    - Confidence scoring
    - Response caching
    - Prompt versioning
    """

    # Prompt version for tracking extraction quality over time
    PROMPT_VERSION = "v2.0"

    EXTRACTION_PROMPT = """Analyze the following scenario and extract the key assumptions underlying it. Identify both explicit and implicit assumptions that form the foundation of the scenario's baseline narrative.

Scenario:
{scenario}

For each assumption, provide:
1. A clear, specific statement of the assumption (avoid vague language)
2. The source text excerpt that contains or implies this assumption (direct quote)
3. A category from this list: political, economic, technological, social, operational, strategic, environmental, cultural
4. A confidence level (0.0 to 1.0) indicating how strongly this assumption appears to underpin the scenario
5. A brief explanation of why this is an assumption (1 sentence)

Return your analysis as a JSON object with this exact structure:
{{
    "assumptions": [
        {{
            "id": "assumption_1",
            "text": "Clear, specific statement of the assumption",
            "source_excerpt": "Direct quote from scenario text",
            "category": "category name",
            "confidence": 0.85,
            "explanation": "Brief explanation of why this is an assumption"
        }}
    ]
}}

Focus on identifying 8-15 key assumptions that are load-bearing for the scenario's logic.
Prioritize assumptions that:
- Are verifiable and specific (contain numbers, dates, or concrete entities)
- Have observable consequences if they fail
- Affect multiple aspects of the scenario
- Are non-obvious or easily overlooked

Avoid generic assumptions - be scenario-specific."""

    def __init__(self):
        self.provider = get_llm_provider()
        self._cache = {}  # Simple in-memory cache (should use Redis in production)

    def _generate_cache_key(self, scenario: str, temperature: float) -> str:
        """Generate cache key based on content hash."""
        content = f"{scenario}:{temperature}:{self.PROMPT_VERSION}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def extract(
        self,
        scenario_text: str,
        validate_consistency: bool = True
    ) -> Dict[str, Any]:
        """
        Extract assumptions from scenario text with optional consistency validation.

        Args:
            scenario_text: The scenario description
            validate_consistency: If True, runs extraction twice and compares results

        Returns:
            {
                "assumptions": List of assumption objects,
                "metadata": {
                    "extraction_model": str,
                    "extraction_timestamp": str,
                    "prompt_version": str,
                    "consistency_score": float (if validate_consistency=True)
                }
            }
        """
        try:
            # Check cache
            cache_key = self._generate_cache_key(scenario_text, 0.3)
            if cache_key in self._cache:
                logger.info("Returning cached extraction result")
                return self._cache[cache_key]

            # Primary extraction
            assumptions_primary = await self._extract_once(scenario_text, temperature=0.3)

            metadata = {
                "extraction_model": "claude-3.5-sonnet",
                "prompt_version": self.PROMPT_VERSION,
                "total_assumptions": len(assumptions_primary)
            }

            # Optional consistency validation
            if validate_consistency:
                logger.info("Running consistency validation...")
                assumptions_secondary = await self._extract_once(scenario_text, temperature=0.4)
                consistency_score = self._calculate_consistency(
                    assumptions_primary,
                    assumptions_secondary
                )
                metadata["consistency_score"] = consistency_score
                metadata["validation_passed"] = consistency_score >= 0.75

                if consistency_score < 0.75:
                    logger.warning(
                        f"Low consistency score: {consistency_score:.2f}. "
                        f"Consider reviewing extracted assumptions."
                    )

            result = {
                "assumptions": assumptions_primary,
                "metadata": metadata
            }

            # Cache result
            self._cache[cache_key] = result

            logger.info(
                f"Extracted {len(assumptions_primary)} assumptions "
                f"(consistency: {metadata.get('consistency_score', 'N/A')})"
            )

            return result

        except Exception as e:
            logger.error(f"Error in assumption extraction: {str(e)}")
            raise

    async def _extract_once(
        self,
        scenario_text: str,
        temperature: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Perform a single extraction pass.

        Args:
            scenario_text: The scenario description
            temperature: LLM temperature (lower = more consistent)

        Returns:
            List of assumption dictionaries
        """
        try:
            prompt = self.EXTRACTION_PROMPT.format(scenario=scenario_text)

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=temperature,
                max_tokens=3000
            )

            # Parse JSON response
            content = response["content"]

            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            assumptions = result.get("assumptions", [])

            # Validate assumption structure
            validated_assumptions = []
            for i, assumption in enumerate(assumptions):
                # Ensure required fields exist
                if not all(k in assumption for k in ["text", "category", "confidence"]):
                    logger.warning(f"Assumption {i} missing required fields, skipping")
                    continue

                # Add default values for optional fields
                if "id" not in assumption:
                    assumption["id"] = f"assumption_{i+1}"
                if "source_excerpt" not in assumption:
                    assumption["source_excerpt"] = ""
                if "explanation" not in assumption:
                    assumption["explanation"] = ""

                # Normalize category
                assumption["category"] = assumption["category"].lower()

                # Ensure confidence is float between 0 and 1
                try:
                    conf = float(assumption["confidence"])
                    assumption["confidence"] = max(0.0, min(1.0, conf))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid confidence value for assumption {i}, setting to 0.5")
                    assumption["confidence"] = 0.5

                validated_assumptions.append(assumption)

            return validated_assumptions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response content: {response.get('content', '')[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error in single extraction pass: {str(e)}")
            raise

    def _calculate_consistency(
        self,
        assumptions_a: List[Dict[str, Any]],
        assumptions_b: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate consistency score between two extraction runs.

        Uses text similarity to determine overlap. A score >= 0.85 indicates
        high consistency.

        Args:
            assumptions_a: First extraction result
            assumptions_b: Second extraction result

        Returns:
            Consistency score (0.0 to 1.0)
        """
        if not assumptions_a or not assumptions_b:
            return 0.0

        # Extract assumption texts
        texts_a = {self._normalize_text(a["text"]) for a in assumptions_a}
        texts_b = {self._normalize_text(a["text"]) for a in assumptions_b}

        # Calculate Jaccard similarity
        intersection = len(texts_a & texts_b)
        union = len(texts_a | texts_b)

        if union == 0:
            return 0.0

        return intersection / union

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip()

    async def re_extract_with_feedback(
        self,
        scenario_text: str,
        user_corrections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Re-extract assumptions incorporating user feedback.

        This builds a feedback loop to improve extraction quality over time.

        Args:
            scenario_text: The scenario description
            user_corrections: List of {action: "add"|"remove"|"edit", assumption: {...}}

        Returns:
            Updated list of assumptions
        """
        # For now, apply corrections directly
        # In production, this would update prompt templates based on patterns

        logger.info(f"Re-extracting with {len(user_corrections)} user corrections")

        # Re-run extraction
        result = await self.extract(scenario_text, validate_consistency=False)
        assumptions = result["assumptions"]

        # Apply user corrections
        for correction in user_corrections:
            action = correction.get("action")

            if action == "add":
                assumptions.append(correction["assumption"])
            elif action == "remove":
                assumption_id = correction["assumption"]["id"]
                assumptions = [a for a in assumptions if a["id"] != assumption_id]
            elif action == "edit":
                assumption_id = correction["assumption"]["id"]
                for i, a in enumerate(assumptions):
                    if a["id"] == assumption_id:
                        assumptions[i] = correction["assumption"]
                        break

        return assumptions
