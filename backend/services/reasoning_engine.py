"""
Core reasoning engine for multi-phase structured analysis.
"""
import json
import logging
from typing import List, Dict, Any
from services.llm_provider import get_llm_provider
from utils.prompts import PromptLibrary, REASONING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Core reasoning engine that powers all phases of structured analysis.
    Uses LLM provider abstraction for flexible provider switching.
    """

    def __init__(self):
        self.provider = get_llm_provider()
        self.prompt_library = PromptLibrary()

    async def extract_assumptions(self, scenario: str) -> List[Dict[str, Any]]:
        """
        Phase 1: Extract assumptions from scenario description.

        Args:
            scenario: The scenario description text

        Returns:
            List of assumptions with id, text, category, and confidence
        """
        try:
            prompt = self.prompt_library.format(
                "assumption_extraction",
                scenario=scenario
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=3000
            )

            # Parse JSON response
            content = response["content"]
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            assumptions = result.get("assumptions", [])

            logger.info(f"Extracted {len(assumptions)} assumptions")
            return assumptions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response content: {response.get('content', '')}")
            # Return empty list with error handling
            return []
        except Exception as e:
            logger.error(f"Error extracting assumptions: {str(e)}")
            raise

    async def generate_baseline_narrative(
        self,
        scenario: str,
        assumptions: List[Dict[str, Any]]
    ) -> str:
        """
        Phase 1: Generate baseline narrative from scenario and assumptions.

        Args:
            scenario: The scenario description
            assumptions: List of extracted assumptions

        Returns:
            Baseline narrative text
        """
        try:
            # Format assumptions for prompt
            assumptions_text = "\n".join([
                f"- {a['text']} (Category: {a['category']}, Confidence: {a['confidence']})"
                for a in assumptions
            ])

            prompt = self.prompt_library.format(
                "baseline_narrative",
                scenario=scenario,
                assumptions=assumptions_text
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.4,
                max_tokens=1500
            )

            narrative = response["content"].strip()
            logger.info("Generated baseline narrative")
            return narrative

        except Exception as e:
            logger.error(f"Error generating baseline narrative: {str(e)}")
            raise

    async def generate_probing_questions(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Phase 2: Generate probing questions to challenge assumptions.

        Args:
            assumptions: List of assumptions from Phase 1

        Returns:
            List of questions with assumption_id, question_text, and dimension
        """
        try:
            # Format assumptions for prompt
            assumptions_text = json.dumps(assumptions, indent=2)

            prompt = self.prompt_library.format(
                "probing_questions",
                assumptions=assumptions_text
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.5,
                max_tokens=4000
            )

            # Parse JSON response
            content = response["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            questions = result.get("questions", [])

            logger.info(f"Generated {len(questions)} probing questions")
            return questions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error generating probing questions: {str(e)}")
            raise

    async def generate_counterfactuals(
        self,
        scenario: str,
        assumptions: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Phase 3: Generate counterfactual scenarios across six strategic axes.

        Args:
            scenario: Original scenario description
            assumptions: List of assumptions from Phase 1
            vulnerabilities: List of questions/vulnerabilities from Phase 2

        Returns:
            List of counterfactuals with axis, breach_condition, consequences, etc.
        """
        try:
            # Format inputs
            assumptions_text = json.dumps(assumptions, indent=2)
            vulnerabilities_text = json.dumps(vulnerabilities, indent=2)

            prompt = self.prompt_library.format(
                "counterfactual_generation",
                scenario=scenario,
                assumptions=assumptions_text,
                vulnerabilities=vulnerabilities_text
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.6,
                max_tokens=4000
            )

            # Parse JSON response
            content = response["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            counterfactuals = result.get("counterfactuals", [])

            logger.info(f"Generated {len(counterfactuals)} counterfactuals")
            return counterfactuals

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse counterfactuals JSON: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error generating counterfactuals: {str(e)}")
            raise

    async def generate_strategic_outcome(
        self,
        breach_condition: str,
        consequences: List[Dict[str, Any]],
        axis: str
    ) -> Dict[str, Any]:
        """
        Phase 5: Generate strategic outcome trajectory for a counterfactual.

        Args:
            breach_condition: The breach condition text
            consequences: List of consequences
            axis: Strategic axis

        Returns:
            Strategic outcome with trajectory, decision points, inflection points
        """
        try:
            # Format inputs
            consequences_text = json.dumps(consequences, indent=2)

            prompt = self.prompt_library.format(
                "strategic_outcome",
                breach_condition=breach_condition,
                consequences=consequences_text,
                axis=axis
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.5,
                max_tokens=3000
            )

            # Parse JSON response
            content = response["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            logger.info(f"Generated strategic outcome for axis: {axis}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse strategic outcome JSON: {str(e)}")
            return {
                "trajectory": {},
                "decision_points": [],
                "inflection_points": [],
                "confidence_intervals": {}
            }
        except Exception as e:
            logger.error(f"Error generating strategic outcome: {str(e)}")
            raise
