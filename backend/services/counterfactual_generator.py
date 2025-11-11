"""
Counterfactual Scenario Generator with Divergence Mapping
Sprint 4 - Task 3: Core Generation Engine

Generates alternative outcome trajectories from breach conditions.
Traces consequences through dependency graphs and creates detailed narratives.
"""
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta
import asyncio
import networkx as nx

from services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class CounterfactualGenerator:
    """
    Core engine for generating counterfactual scenarios.

    Key Features:
    - Divergence timeline identification
    - Consequence cascade through dependency graphs
    - Multi-level cause-effect tracing (depth 2-5)
    - Narrative generation (200-400 words)
    - Preliminary severity/probability scoring
    """

    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize counterfactual generator.

        Args:
            llm_provider: LLM provider for narrative generation
        """
        self.llm = llm_provider
        self.max_depth = 5  # Maximum cascade depth
        self.pruning_threshold = 0.3  # Probability threshold for pruning

    async def generate_counterfactual(
        self,
        breach_condition: Dict,
        phase2_graph: nx.DiGraph,
        scenario_context: Dict
    ) -> Dict:
        """
        Generate a counterfactual scenario from a breach condition.

        Args:
            breach_condition: Breach condition dictionary
            phase2_graph: Dependency graph from Phase 2 analysis
            scenario_context: Full scenario context

        Returns:
            Complete counterfactual scenario dictionary
        """
        try:
            logger.info(f"Generating counterfactual for breach: {breach_condition.get('trigger_event')}")

            # Step 1: Identify divergence timeline
            divergence_points = await self._identify_divergence_points(
                breach_condition,
                scenario_context
            )

            # Step 2: Trace cascading consequences
            consequence_tree = await self._trace_consequences(
                breach=breach_condition,
                graph=phase2_graph,
                max_depth=self.max_depth,
                pruning_threshold=self.pruning_threshold
            )

            # Step 3: Generate narrative
            narrative = await self._generate_narrative(
                breach=breach_condition,
                consequences=consequence_tree,
                divergence=divergence_points,
                word_limit=400
            )

            # Step 4: Preliminary scoring
            scores = await self._preliminary_scoring(
                consequence_tree,
                breach_condition,
                phase2_graph
            )

            # Step 5: Identify affected domains
            affected_domains = self._identify_affected_domains(consequence_tree)

            # Construct counterfactual
            counterfactual = {
                "breach_id": breach_condition.get("id"),
                "scenario_id": scenario_context.get("id"),
                "axis": breach_condition.get("axis_id"),
                "narrative": narrative,
                "divergence_timeline": divergence_points,
                "consequences": consequence_tree,
                "affected_domains": affected_domains,
                "preliminary_severity": scores["severity"],
                "preliminary_probability": scores["probability"],
                "generation_metadata": {
                    "llm_model": self.llm.model_name,
                    "generated_at": datetime.utcnow().isoformat(),
                    "word_count": len(narrative.split()),
                    "consequence_depth": self._get_max_depth(consequence_tree),
                    "cascade_breadth": len(consequence_tree)
                }
            }

            logger.info(f"Successfully generated counterfactual: {len(narrative)} chars, {len(consequence_tree)} consequences")
            return counterfactual

        except Exception as e:
            logger.error(f"Counterfactual generation failed: {e}")
            raise

    async def _identify_divergence_points(
        self,
        breach_condition: Dict,
        scenario_context: Dict
    ) -> List[Dict]:
        """
        Identify key timeline divergence points from baseline.

        Args:
            breach_condition: Breach condition dictionary
            scenario_context: Full scenario context

        Returns:
            List of divergence point dictionaries with dates and events
        """
        prompt = f"""You are analyzing a counterfactual scenario where a baseline assumption fails.

**Baseline Scenario:**
{scenario_context.get('description', '')}

**Breach Event:**
{breach_condition.get('description', '')}

**Trigger:**
{breach_condition.get('trigger_event', '')}

**Task:**
Identify 3-5 key divergence points where this counterfactual timeline splits from the baseline.
For each divergence point, specify:
1. Timeframe (e.g., "Month 0", "Quarter 2", "Year 1", specific dates if given)
2. Event description (what happens at this divergence)
3. Significance (why this point is critical to the cascade)

Return JSON format:
{{
  "divergence_points": [
    {{
      "timeframe": "Month 0",
      "event": "Breach trigger event occurs",
      "significance": "Initial point of departure from baseline"
    }},
    ...
  ]
}}

Focus on:
- Key decision points that change
- Critical events that occur earlier/later or not at all
- Threshold crossings that cascade into further divergence
"""

        response = await self.llm.generate_structured_output(
            prompt=prompt,
            schema={
                "type": "object",
                "properties": {
                    "divergence_points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timeframe": {"type": "string"},
                                "event": {"type": "string"},
                                "significance": {"type": "string"}
                            }
                        },
                        "minItems": 3,
                        "maxItems": 5
                    }
                }
            }
        )

        return response.get("divergence_points", [])

    async def _trace_consequences(
        self,
        breach: Dict,
        graph: nx.DiGraph,
        max_depth: int,
        pruning_threshold: float
    ) -> List[Dict]:
        """
        Trace cascading consequences through dependency graph.

        Args:
            breach: Breach condition dictionary
            graph: Dependency graph (networkx DiGraph)
            max_depth: Maximum cascade depth
            pruning_threshold: Minimum probability to continue cascade

        Returns:
            List of consequence dictionaries forming a tree structure
        """
        try:
            # Start from breach fragility node
            fragility_id = breach.get("fragility_id")
            if fragility_id not in graph:
                logger.warning(f"Fragility {fragility_id} not in graph, generating standalone consequences")
                return await self._generate_standalone_consequences(breach)

            consequences = []

            # BFS traversal with depth tracking
            queue = [(fragility_id, 0, 1.0, None)]  # (node, depth, probability, parent_id)
            visited = set()

            while queue:
                current_node, depth, cumulative_prob, parent_id = queue.pop(0)

                # Stop if max depth or probability too low
                if depth >= max_depth or cumulative_prob < pruning_threshold:
                    continue

                if current_node in visited:
                    continue

                visited.add(current_node)

                # Get node data
                node_data = graph.nodes[current_node]

                # Create consequence entry
                consequence = {
                    "id": f"cons_{current_node}_{depth}",
                    "depth": depth + 1,
                    "parent_id": parent_id,
                    "description": node_data.get("description", ""),
                    "affected_domains": node_data.get("domains", []),
                    "affected_actors": node_data.get("actors", []),
                    "affected_resources": node_data.get("resources", []),
                    "probability": cumulative_prob,
                    "timeframe": self._estimate_timeframe(depth)
                }

                consequences.append(consequence)

                # Add children to queue
                for neighbor in graph.successors(current_node):
                    edge_data = graph[current_node][neighbor]
                    edge_weight = edge_data.get("weight", 0.5)

                    # Only follow edges above threshold
                    if edge_weight > 0.4:
                        new_prob = cumulative_prob * edge_weight
                        queue.append((neighbor, depth + 1, new_prob, consequence["id"]))

            # If no consequences found, generate fallback
            if not consequences:
                consequences = await self._generate_standalone_consequences(breach)

            return consequences

        except Exception as e:
            logger.error(f"Consequence tracing failed: {e}")
            return await self._generate_standalone_consequences(breach)

    async def _generate_standalone_consequences(self, breach: Dict) -> List[Dict]:
        """Generate consequences using LLM when graph traversal unavailable."""
        prompt = f"""Generate 3-5 cascading consequences from this breach condition.

**Breach:**
{breach.get('description', '')}

**Trigger:**
{breach.get('trigger_event', '')}

For each consequence, provide:
1. Description (what happens)
2. Depth level (1=immediate, 2=secondary, 3=tertiary, etc.)
3. Affected domains (economic, political, operational, social, technological, environmental)
4. Timeframe (when this consequence manifests)

Return JSON format:
{{
  "consequences": [
    {{
      "description": "Immediate consequence description",
      "depth": 1,
      "affected_domains": ["economic", "political"],
      "timeframe": "0-3 months"
    }},
    ...
  ]
}}
"""

        response = await self.llm.generate_structured_output(
            prompt=prompt,
            schema={
                "type": "object",
                "properties": {
                    "consequences": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "depth": {"type": "integer"},
                                "affected_domains": {"type": "array", "items": {"type": "string"}},
                                "timeframe": {"type": "string"}
                            }
                        }
                    }
                }
            }
        )

        consequences = []
        for i, cons in enumerate(response.get("consequences", [])):
            consequences.append({
                "id": f"cons_standalone_{i}",
                "depth": cons.get("depth", i + 1),
                "parent_id": None if i == 0 else f"cons_standalone_{i-1}",
                "description": cons.get("description", ""),
                "affected_domains": cons.get("affected_domains", []),
                "affected_actors": [],
                "affected_resources": [],
                "probability": 1.0 / (i + 1),  # Decay with depth
                "timeframe": cons.get("timeframe", "")
            })

        return consequences

    async def _generate_narrative(
        self,
        breach: Dict,
        consequences: List[Dict],
        divergence: List[Dict],
        word_limit: int = 400
    ) -> str:
        """
        Generate coherent narrative from breach and consequences.

        Args:
            breach: Breach condition dictionary
            consequences: List of consequence dictionaries
            divergence: List of divergence points
            word_limit: Target word count (200-400)

        Returns:
            Narrative string
        """
        # Organize consequences by depth
        by_depth = {}
        for cons in consequences:
            depth = cons.get("depth", 1)
            if depth not in by_depth:
                by_depth[depth] = []
            by_depth[depth].append(cons["description"])

        consequences_summary = "\n".join([
            f"**Level {depth}**: {'; '.join(descs)}"
            for depth, descs in sorted(by_depth.items())
        ])

        prompt = f"""Write a compelling counterfactual narrative (200-400 words).

**Breach Event:**
{breach.get('trigger_event', '')}

**Breach Description:**
{breach.get('description', '')}

**Divergence Timeline:**
{chr(10).join([f"- {d.get('timeframe')}: {d.get('event')}" for d in divergence])}

**Cascading Consequences:**
{consequences_summary}

**Requirements:**
1. Start with the breach trigger event
2. Flow through the divergence timeline chronologically
3. Describe how consequences cascade and compound
4. Be specific with actors, systems, resources affected
5. Convey escalating severity and momentum
6. Target 200-400 words (current target: ~{word_limit})
7. Professional tone, active voice

Write the narrative as a single coherent paragraph or 2-3 short paragraphs."""

        narrative = await self.llm.generate_text(prompt)

        # Trim if too long
        words = narrative.split()
        if len(words) > word_limit + 50:
            narrative = " ".join(words[:word_limit]) + "..."

        return narrative

    async def _preliminary_scoring(
        self,
        consequence_tree: List[Dict],
        breach_condition: Dict,
        phase2_graph: nx.DiGraph
    ) -> Dict[str, float]:
        """
        Calculate preliminary severity and probability scores.
        (Will be refined by Task 4 scoring engine)

        Args:
            consequence_tree: List of consequence dictionaries
            breach_condition: Breach condition dictionary
            phase2_graph: Phase 2 dependency graph

        Returns:
            Dictionary with severity and probability scores
        """
        # Severity based on cascade depth and breadth
        max_depth = self._get_max_depth(consequence_tree)
        breadth = len(consequence_tree)

        # Normalize to 0-10 scale
        depth_score = min(max_depth / 5.0, 1.0) * 10  # Max depth 5 -> 10
        breadth_score = min(breadth / 10.0, 1.0) * 10  # 10+ consequences -> 10

        severity = (depth_score * 0.5 + breadth_score * 0.5)  # Average

        # Probability based on breach plausibility and evidence strength
        breach_plausibility = breach_condition.get("plausibility_score", 0.5)

        probability = breach_plausibility * 0.7 + 0.15  # Scale to 0.15-0.85 range

        return {
            "severity": round(severity, 2),
            "probability": round(probability, 2)
        }

    def _identify_affected_domains(self, consequence_tree: List[Dict]) -> List[str]:
        """Extract unique affected domains from consequence tree."""
        domains = set()
        for cons in consequence_tree:
            domains.update(cons.get("affected_domains", []))
        return sorted(list(domains))

    def _get_max_depth(self, consequence_tree: List[Dict]) -> int:
        """Get maximum depth in consequence tree."""
        if not consequence_tree:
            return 0
        return max(cons.get("depth", 0) for cons in consequence_tree)

    def _estimate_timeframe(self, depth: int) -> str:
        """Estimate timeframe based on cascade depth."""
        timeframes = {
            0: "0-3 months",
            1: "3-6 months",
            2: "6-12 months",
            3: "1-2 years",
            4: "2-5 years",
            5: "5+ years"
        }
        return timeframes.get(depth, "5+ years")


async def generate_all_counterfactuals(
    breach_conditions: Dict[str, List[Dict]],
    phase2_graph: nx.DiGraph,
    scenario_context: Dict,
    llm_provider: LLMProvider
) -> List[Dict]:
    """
    Generate counterfactuals for all breach conditions.

    Args:
        breach_conditions: Dictionary mapping fragility IDs to breach lists
        phase2_graph: Phase 2 dependency graph
        scenario_context: Full scenario context
        llm_provider: LLM provider instance

    Returns:
        List of counterfactual dictionaries
    """
    generator = CounterfactualGenerator(llm_provider)
    counterfactuals = []

    for fragility_id, breaches in breach_conditions.items():
        for breach in breaches:
            try:
                cf = await generator.generate_counterfactual(
                    breach_condition=breach,
                    phase2_graph=phase2_graph,
                    scenario_context=scenario_context
                )
                counterfactuals.append(cf)
                logger.info(f"Generated counterfactual for breach {breach.get('id')}")
            except Exception as e:
                logger.error(f"Failed to generate counterfactual for breach {breach.get('id')}: {e}")
                continue

    logger.info(f"Generated {len(counterfactuals)} total counterfactuals")
    return counterfactuals
