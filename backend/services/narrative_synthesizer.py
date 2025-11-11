"""
Baseline narrative synthesis and summary generation.
Sprint 2 - Task 8: Multi-Stage LLM Summarization
"""
import logging
import json
from typing import List, Dict, Any
from collections import defaultdict
from services.llm_provider import get_llm_provider
from utils.prompts import REASONING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class BaselineNarrative:
    """Synthesized baseline narrative result."""

    def __init__(
        self,
        summary: str,
        themes: List[str],
        anchor_assumptions: List[str],
        word_count: int
    ):
        self.summary = summary
        self.themes = themes
        self.anchor_assumptions = anchor_assumptions
        self.word_count = word_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "themes": self.themes,
            "anchor_assumptions": self.anchor_assumptions,
            "word_count": self.word_count
        }


class NarrativeSynthesizer:
    """
    Multi-stage narrative synthesis system.

    Pipeline:
    1. Extract narrative themes from assumptions
    2. Cluster assumptions by theme
    3. Generate narrative for each theme
    4. Synthesize unified baseline narrative
    5. Identify anchor assumptions
    """

    THEME_EXTRACTION_PROMPT = """Analyze these assumptions and identify 3-5 overarching narrative themes that connect them.

Assumptions:
{assumptions}

For each theme, provide:
- A concise label (2-4 words)
- A brief description (1 sentence)
- The assumption IDs that belong to this theme

Return as JSON:
{{
    "themes": [
        {{
            "label": "Theme name",
            "description": "Brief description",
            "assumption_ids": ["assumption_1", "assumption_2"]
        }}
    ]
}}"""

    UNIFIED_NARRATIVE_PROMPT = """Given this scenario and thematic assumption groups, generate a unified baseline narrative.

Scenario:
{scenario_text}

Thematic Assumption Groups:
{theme_narratives}

Critical Assumption Relationships:
{relationships_summary}

Generate a cohesive 300-500 word baseline narrative that:
1. Articulates the dominant worldview embedded in these assumptions
2. Shows how themes interconnect to form a coherent mental model
3. Highlights the strongest/most critical assumptions anchoring the narrative
4. Uses clear, accessible language (avoid jargon)
5. Frames as "The conventional wisdom assumes that..."

Do not introduce new ideas not present in the assumptions.
Focus on synthesizing the implicit worldview that underlies the scenario."""

    ANCHOR_IDENTIFICATION_PROMPT = """Given these assumptions and their relationships, identify the 5 most critical "anchor" assumptions.

Assumptions:
{assumptions}

Relationships:
{relationships}

Quality Scores:
{quality_scores}

Anchor assumptions are those that:
- Have high quality scores (specificity, verifiability, impact)
- Many other assumptions depend on them
- If they fail, large parts of the scenario collapse

Return as JSON:
{{
    "anchors": [
        {{
            "assumption_id": "assumption_X",
            "reasoning": "Why this is an anchor (1 sentence)"
        }}
    ]
}}

Return exactly 5 anchors, ranked by criticality."""

    def __init__(self):
        self.provider = get_llm_provider()

    async def synthesize(
        self,
        scenario_text: str,
        assumptions: List[Dict[str, Any]],
        relationships: Dict[str, Any]
    ) -> BaselineNarrative:
        """
        Synthesize baseline narrative from scenario and assumptions.

        Args:
            scenario_text: Original scenario description
            assumptions: List of validated, scored, categorized assumptions
            relationships: Relationship graph data

        Returns:
            BaselineNarrative object
        """
        try:
            logger.info("Starting narrative synthesis...")

            # Stage 1: Extract themes
            themes = await self._extract_themes(assumptions)

            # Stage 2: Cluster by theme (done in extract_themes)

            # Stage 3 & 4: Generate unified narrative
            unified_narrative = await self._generate_unified_narrative(
                scenario_text,
                assumptions,
                themes,
                relationships
            )

            # Stage 5: Identify anchors
            anchor_ids = await self._identify_anchors(
                assumptions,
                relationships
            )

            word_count = len(unified_narrative.split())

            logger.info(
                f"Narrative synthesis complete: {word_count} words, "
                f"{len(themes)} themes, {len(anchor_ids)} anchors"
            )

            return BaselineNarrative(
                summary=unified_narrative,
                themes=[t["label"] for t in themes],
                anchor_assumptions=anchor_ids,
                word_count=word_count
            )

        except Exception as e:
            logger.error(f"Error in narrative synthesis: {str(e)}")
            raise

    async def _extract_themes(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract narrative themes from assumptions.

        Args:
            assumptions: List of assumptions

        Returns:
            List of theme objects with labels and descriptions
        """
        try:
            # Format assumptions for prompt
            assumptions_text = json.dumps(
                [
                    {
                        "id": a["id"],
                        "text": a["text"],
                        "domains": a.get("domains", [])
                    }
                    for a in assumptions
                ],
                indent=2
            )

            prompt = self.THEME_EXTRACTION_PROMPT.format(
                assumptions=assumptions_text
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.5,
                max_tokens=2000
            )

            # Parse response
            content = response["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            themes = result.get("themes", [])

            # Ensure we have 3-5 themes
            if len(themes) < 3:
                # Fall back to domain-based themes
                themes = self._generate_domain_themes(assumptions)

            logger.info(f"Extracted {len(themes)} narrative themes")

            return themes

        except Exception as e:
            logger.warning(f"Theme extraction failed, using domain fallback: {str(e)}")
            return self._generate_domain_themes(assumptions)

    def _generate_domain_themes(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fallback: Generate themes based on domains.

        Args:
            assumptions: List of assumptions

        Returns:
            List of theme objects
        """
        domain_groups = defaultdict(list)

        for assumption in assumptions:
            for domain in assumption.get("domains", ["strategic"]):
                domain_groups[domain].append(assumption["id"])

        themes = []
        for domain, ids in sorted(domain_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            themes.append({
                "label": domain.replace("_", " ").title(),
                "description": f"Assumptions related to {domain} considerations",
                "assumption_ids": ids
            })

        return themes

    async def _generate_unified_narrative(
        self,
        scenario_text: str,
        assumptions: List[Dict[str, Any]],
        themes: List[Dict[str, Any]],
        relationships: Dict[str, Any]
    ) -> str:
        """
        Generate unified baseline narrative.

        Args:
            scenario_text: Original scenario
            assumptions: List of assumptions
            themes: Extracted themes
            relationships: Relationship data

        Returns:
            Narrative text (300-500 words)
        """
        try:
            # Format theme narratives
            theme_narratives = []
            for theme in themes:
                theme_assumptions = [
                    a for a in assumptions
                    if a["id"] in theme.get("assumption_ids", [])
                ]

                theme_text = f"**{theme['label']}**: {theme['description']}\n"
                theme_text += "\n".join([
                    f"- {a['text']}"
                    for a in theme_assumptions[:5]  # Limit to avoid token overflow
                ])
                theme_narratives.append(theme_text)

            theme_narratives_text = "\n\n".join(theme_narratives)

            # Summarize relationships
            rel_stats = relationships.get("statistics", {})
            relationships_summary = f"""
Total relationships: {rel_stats.get('relationships_found', 0)}
- Dependencies: {rel_stats.get('dependencies', 0)}
- Reinforcements: {rel_stats.get('reinforcements', 0)}
- Contradictions: {rel_stats.get('contradictions', 0)}

Critical assumptions: {', '.join(relationships.get('graph_analysis', {}).get('critical_assumptions', [])[:3])}
"""

            prompt = self.UNIFIED_NARRATIVE_PROMPT.format(
                scenario_text=scenario_text[:1000],  # Limit to avoid token overflow
                theme_narratives=theme_narratives_text,
                relationships_summary=relationships_summary
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.6,  # Slightly creative for readability
                max_tokens=800
            )

            narrative = response["content"].strip()

            logger.info("Generated unified baseline narrative")

            return narrative

        except Exception as e:
            logger.error(f"Error generating unified narrative: {str(e)}")
            # Fallback to simple concatenation
            return self._generate_fallback_narrative(scenario_text, assumptions)

    def _generate_fallback_narrative(
        self,
        scenario_text: str,
        assumptions: List[Dict[str, Any]]
    ) -> str:
        """Generate simple fallback narrative."""
        narrative = f"The conventional wisdom regarding this scenario assumes several key points:\n\n"

        # Group by domain
        by_domain = defaultdict(list)
        for assumption in assumptions:
            domain = assumption.get("domains", ["strategic"])[0]
            by_domain[domain].append(assumption["text"])

        for domain, texts in list(by_domain.items())[:3]:
            narrative += f"**{domain.title()}**: "
            narrative += " ".join(texts[:3])
            narrative += "\n\n"

        narrative += "These assumptions form the baseline narrative that underpins the scenario's expected trajectory."

        return narrative

    async def _identify_anchors(
        self,
        assumptions: List[Dict[str, Any]],
        relationships: Dict[str, Any]
    ) -> List[str]:
        """
        Identify anchor assumptions using combined scoring.

        Args:
            assumptions: List of assumptions with quality scores
            relationships: Relationship graph data

        Returns:
            List of assumption IDs (top 5 anchors)
        """
        try:
            # Prepare data for LLM
            assumptions_summary = json.dumps(
                [
                    {
                        "id": a["id"],
                        "text": a["text"],
                        "quality_score": a.get("quality_score", 50)
                    }
                    for a in assumptions
                ],
                indent=2
            )

            relationships_summary = json.dumps(
                relationships.get("graph_analysis", {}),
                indent=2
            )

            quality_scores = {
                a["id"]: a.get("quality_score", 50)
                for a in assumptions
            }

            prompt = self.ANCHOR_IDENTIFICATION_PROMPT.format(
                assumptions=assumptions_summary,
                relationships=relationships_summary,
                quality_scores=json.dumps(quality_scores, indent=2)
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1000
            )

            # Parse response
            content = response["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            anchors = result.get("anchors", [])

            anchor_ids = [a["assumption_id"] for a in anchors]

            logger.info(f"Identified {len(anchor_ids)} anchor assumptions")

            return anchor_ids[:5]

        except Exception as e:
            logger.warning(f"Anchor identification failed, using fallback: {str(e)}")
            return self._identify_anchors_fallback(assumptions, relationships)

    def _identify_anchors_fallback(
        self,
        assumptions: List[Dict[str, Any]],
        relationships: Dict[str, Any]
    ) -> List[str]:
        """
        Fallback anchor identification using heuristics.

        Args:
            assumptions: List of assumptions
            relationships: Relationship data

        Returns:
            List of assumption IDs
        """
        # Combine quality score + graph centrality
        critical_assumptions = relationships.get("graph_analysis", {}).get("critical_assumptions", [])

        scored = []
        for assumption in assumptions:
            quality = assumption.get("quality_score", 50)
            graph_score = 20 if assumption["id"] in critical_assumptions else 0

            combined = quality * 0.7 + graph_score * 0.3
            scored.append((assumption["id"], combined))

        # Sort by combined score
        scored.sort(key=lambda x: x[1], reverse=True)

        return [aid for aid, score in scored[:5]]
