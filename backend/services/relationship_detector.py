"""
Assumption relationship and dependency detection system.
Sprint 2 - Task 7: Graph-Based Dependency Analysis
"""
import logging
import json
from typing import List, Dict, Any, Tuple, Optional
from itertools import combinations
from collections import defaultdict
from services.llm_provider import get_llm_provider
from utils.prompts import REASONING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class RelationshipType:
    """Relationship types between assumptions."""
    DEPENDS_ON = "depends_on"  # A logically requires B
    CONTRADICTS = "contradicts"  # A and B cannot both be true
    REINFORCES = "reinforces"  # A strengthens B


class Relationship:
    """Relationship between two assumptions."""

    def __init__(
        self,
        assumption_a_id: str,
        assumption_b_id: str,
        relationship_type: str,
        confidence: float,
        explanation: str = ""
    ):
        self.assumption_a_id = assumption_a_id
        self.assumption_b_id = assumption_b_id
        self.type = relationship_type
        self.confidence = confidence
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assumption_a_id": self.assumption_a_id,
            "assumption_b_id": self.assumption_b_id,
            "type": self.type,
            "confidence": self.confidence,
            "explanation": self.explanation
        }


class GraphAnalysis:
    """Results of graph analysis."""

    def __init__(
        self,
        circular_dependencies: List[List[str]],
        assumption_clusters: List[List[str]],
        critical_assumptions: List[str],
        contradiction_pairs: List[Tuple[str, str]]
    ):
        self.circular_dependencies = circular_dependencies
        self.assumption_clusters = assumption_clusters
        self.critical_assumptions = critical_assumptions
        self.contradiction_pairs = contradiction_pairs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "circular_dependencies": self.circular_dependencies,
            "assumption_clusters": self.assumption_clusters,
            "critical_assumptions": self.critical_assumptions,
            "contradiction_pairs": self.contradiction_pairs
        }


class RelationshipDetector:
    """
    Detect and analyze relationships between assumptions.

    Uses LLM-based pairwise comparison with domain filtering to reduce
    O(n²) complexity.
    """

    RELATIONSHIP_PROMPT = """Analyze the relationship between these two assumptions:

Assumption A:
ID: {id_a}
Text: {text_a}
Domains: {domains_a}

Assumption B:
ID: {id_b}
Text: {text_b}
Domains: {domains_b}

Determine if there is a logical relationship between them:

1. **depends_on**: Assumption A logically requires Assumption B to be true
   (If B fails, A cannot hold)

2. **contradicts**: Assumption A and B cannot both be true simultaneously
   (They are mutually exclusive)

3. **reinforces**: Assumption A strengthens the likelihood of Assumption B
   (They support each other)

4. **none**: No significant relationship

Return your analysis as JSON:
{{
    "relationship": "depends_on" | "contradicts" | "reinforces" | "none",
    "confidence": 0.0-1.0,
    "explanation": "Brief explanation of the relationship (1-2 sentences)"
}}

Be conservative - only identify relationships with confidence > 0.6."""

    def __init__(self):
        self.provider = get_llm_provider()
        self.graph = defaultdict(list)  # adjacency list
        self.relationships = []

    async def detect_relationships(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect relationships between assumptions and build dependency graph.

        Args:
            assumptions: List of categorized assumptions

        Returns:
            {
                "relationships": List of relationship objects,
                "graph_analysis": GraphAnalysis dict,
                "statistics": Summary statistics
            }
        """
        try:
            # Get candidate pairs (reduced by domain filtering)
            pairs = self._get_candidate_pairs(assumptions)

            logger.info(
                f"Analyzing {len(pairs)} assumption pairs "
                f"(from {len(assumptions)} assumptions)"
            )

            # Analyze relationships (batch would be better in production)
            relationships = []
            for i, (a1, a2) in enumerate(pairs):
                if i % 10 == 0:
                    logger.info(f"Analyzing pair {i+1}/{len(pairs)}")

                rel = await self._classify_relationship(a1, a2)

                if rel and rel.type != "none" and rel.confidence > 0.6:
                    relationships.append(rel)
                    self._add_to_graph(rel)

            # Analyze graph structure
            graph_analysis = self._analyze_graph(assumptions)

            # Calculate statistics
            statistics = {
                "total_assumptions": len(assumptions),
                "total_pairs_analyzed": len(pairs),
                "relationships_found": len(relationships),
                "dependencies": sum(1 for r in relationships if r.type == RelationshipType.DEPENDS_ON),
                "contradictions": sum(1 for r in relationships if r.type == RelationshipType.CONTRADICTS),
                "reinforcements": sum(1 for r in relationships if r.type == RelationshipType.REINFORCES)
            }

            logger.info(f"Found {len(relationships)} relationships: {statistics}")

            return {
                "relationships": [r.to_dict() for r in relationships],
                "graph_analysis": graph_analysis.to_dict(),
                "statistics": statistics
            }

        except Exception as e:
            logger.error(f"Error detecting relationships: {str(e)}")
            raise

    def _get_candidate_pairs(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Get candidate assumption pairs using domain filtering.

        Only compares assumptions that share at least one domain,
        reducing O(n²) to approximately O(n*k) where k is average
        assumptions per domain.

        Args:
            assumptions: List of assumptions

        Returns:
            List of (assumption_a, assumption_b) tuples
        """
        # Group by domain
        by_domain = defaultdict(list)

        for assumption in assumptions:
            for domain in assumption.get("domains", ["strategic"]):
                by_domain[domain].append(assumption)

        # Generate pairs within each domain
        pairs_set = set()  # Use set to avoid duplicates

        for domain, group in by_domain.items():
            for a1, a2 in combinations(group, 2):
                # Create ordered tuple (smaller id first)
                pair = tuple(sorted([a1["id"], a2["id"]]))
                pairs_set.add(pair)

        # Convert back to assumption objects
        assumption_by_id = {a["id"]: a for a in assumptions}

        pairs = [
            (assumption_by_id[id1], assumption_by_id[id2])
            for id1, id2 in pairs_set
        ]

        return pairs

    async def _classify_relationship(
        self,
        a1: Dict[str, Any],
        a2: Dict[str, Any]
    ) -> Optional[Relationship]:
        """
        Use LLM to classify relationship between two assumptions.

        Args:
            a1: First assumption
            a2: Second assumption

        Returns:
            Relationship object or None if classification fails
        """
        try:
            prompt = self.RELATIONSHIP_PROMPT.format(
                id_a=a1["id"],
                text_a=a1["text"],
                domains_a=", ".join(a1.get("domains", [])),
                id_b=a2["id"],
                text_b=a2["text"],
                domains_b=", ".join(a2.get("domains", []))
            )

            response = await self.provider.complete(
                prompt=prompt,
                system=REASONING_SYSTEM_PROMPT,
                temperature=0.2,  # Low temperature for consistency
                max_tokens=500
            )

            # Parse JSON response
            content = response["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            relationship_type = result.get("relationship")
            confidence = result.get("confidence", 0.0)
            explanation = result.get("explanation", "")

            if relationship_type and relationship_type != "none":
                return Relationship(
                    assumption_a_id=a1["id"],
                    assumption_b_id=a2["id"],
                    relationship_type=relationship_type,
                    confidence=confidence,
                    explanation=explanation
                )

            return None

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse relationship JSON: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Error classifying relationship: {str(e)}")
            return None

    def _add_to_graph(self, relationship: Relationship):
        """Add relationship to adjacency list graph."""
        if relationship.type == RelationshipType.DEPENDS_ON:
            # A depends on B: edge from A to B
            self.graph[relationship.assumption_a_id].append(
                (relationship.assumption_b_id, relationship.type, relationship.confidence)
            )
        elif relationship.type == RelationshipType.REINFORCES:
            # Bidirectional
            self.graph[relationship.assumption_a_id].append(
                (relationship.assumption_b_id, relationship.type, relationship.confidence)
            )
            self.graph[relationship.assumption_b_id].append(
                (relationship.assumption_a_id, relationship.type, relationship.confidence)
            )

    def _analyze_graph(self, assumptions: List[Dict[str, Any]]) -> GraphAnalysis:
        """
        Analyze graph structure to identify patterns.

        Args:
            assumptions: List of assumptions

        Returns:
            GraphAnalysis object
        """
        # Find circular dependencies (simple DFS-based cycle detection)
        circular = self._find_circular_dependencies()

        # Find clusters (connected components)
        clusters = self._find_clusters(assumptions)

        # Find critical nodes (high out-degree)
        critical = self._find_critical_nodes(top_n=5)

        # Find contradiction pairs
        contradictions = [
            (r.assumption_a_id, r.assumption_b_id)
            for r in self.relationships
            if r.type == RelationshipType.CONTRADICTS
        ]

        return GraphAnalysis(
            circular_dependencies=circular,
            assumption_clusters=clusters,
            critical_assumptions=critical,
            contradiction_pairs=contradictions
        )

    def _find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies using DFS.

        Returns:
            List of cycles (each cycle is a list of assumption IDs)
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor, rel_type, _ in self.graph.get(node, []):
                if rel_type != RelationshipType.DEPENDS_ON:
                    continue

                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.remove(node)

        for node in self.graph.keys():
            if node not in visited:
                dfs(node, [])

        return cycles

    def _find_clusters(self, assumptions: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Find connected components (clusters of related assumptions).

        Args:
            assumptions: List of assumptions

        Returns:
            List of clusters (each cluster is a list of assumption IDs)
        """
        visited = set()
        clusters = []

        def dfs(node, cluster):
            visited.add(node)
            cluster.append(node)

            for neighbor, _, _ in self.graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, cluster)

        all_nodes = {a["id"] for a in assumptions}

        for node in all_nodes:
            if node not in visited:
                cluster = []
                dfs(node, cluster)
                if len(cluster) > 1:  # Only include clusters with multiple nodes
                    clusters.append(cluster)

        return clusters

    def _find_critical_nodes(self, top_n: int = 5) -> List[str]:
        """
        Find critical assumptions (high out-degree = many depend on them).

        Args:
            top_n: Number of top critical nodes to return

        Returns:
            List of assumption IDs sorted by criticality
        """
        out_degree = defaultdict(int)

        for node, edges in self.graph.items():
            for neighbor, rel_type, confidence in edges:
                if rel_type == RelationshipType.DEPENDS_ON:
                    # neighbor is a dependency, so it's critical
                    out_degree[neighbor] += 1

        # Sort by out-degree
        sorted_nodes = sorted(
            out_degree.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [node for node, degree in sorted_nodes[:top_n]]
