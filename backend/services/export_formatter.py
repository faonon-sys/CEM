"""
Export and formatting system for assumptions and analysis results.
Sprint 2 - Task 4: Multi-Format Serialization Pipeline
"""
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportFormatter:
    """
    Multi-format export system for analysis results.

    Supports:
    - JSON (for system consumption)
    - Markdown (for human review)
    - Structured reports
    """

    def __init__(self):
        pass

    def export_json(
        self,
        scenario: Dict[str, Any],
        assumptions: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        relationships: Dict[str, Any] = None,
        narrative: Dict[str, Any] = None
    ) -> str:
        """
        Export analysis results as JSON.

        Args:
            scenario: Scenario data
            assumptions: List of validated assumptions
            metadata: Extraction metadata
            relationships: Optional relationship graph data
            narrative: Optional baseline narrative

        Returns:
            JSON string
        """
        export_data = {
            "scenario": {
                "id": scenario.get("id"),
                "title": scenario.get("title"),
                "text": scenario.get("description") or scenario.get("text"),
                "created_at": scenario.get("created_at"),
                "user_id": scenario.get("user_id")
            },
            "assumptions": [
                {
                    "id": a["id"],
                    "text": a["text"],
                    "source_excerpt": a.get("source_excerpt", ""),
                    "domains": a.get("domains", []),
                    "category": a.get("category", ""),
                    "quality_score": a.get("quality_score"),
                    "quality_dimensions": a.get("quality_dimensions", {}),
                    "priority_tier": a.get("priority_tier"),
                    "confidence": a.get("confidence"),
                    "validated": a.get("validated", False),
                    "user_edited": a.get("user_edited", False),
                    "is_cross_domain": a.get("is_cross_domain", False)
                }
                for a in assumptions
            ],
            "metadata": {
                "total_assumptions": len(assumptions),
                "domain_distribution": self._calculate_domain_distribution(assumptions),
                "priority_distribution": self._calculate_priority_distribution(assumptions),
                "extraction_model": metadata.get("extraction_model"),
                "prompt_version": metadata.get("prompt_version"),
                "consistency_score": metadata.get("consistency_score"),
                "export_timestamp": datetime.utcnow().isoformat()
            }
        }

        if relationships:
            export_data["relationships"] = relationships

        if narrative:
            export_data["baseline_narrative"] = narrative

        return json.dumps(export_data, indent=2)

    def export_markdown(
        self,
        scenario: Dict[str, Any],
        assumptions: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        relationships: Dict[str, Any] = None,
        narrative: Dict[str, Any] = None
    ) -> str:
        """
        Export analysis results as formatted Markdown report.

        Args:
            scenario: Scenario data
            assumptions: List of validated assumptions
            metadata: Extraction metadata
            relationships: Optional relationship graph data
            narrative: Optional baseline narrative

        Returns:
            Markdown string
        """
        md = []

        # Header
        md.append(f"# Scenario Analysis: {scenario.get('title', 'Untitled')}")
        md.append("")
        md.append("---")
        md.append("")

        # Overview
        md.append("## Overview")
        md.append("")
        md.append(f"- **Date**: {scenario.get('created_at', 'N/A')}")
        md.append(f"- **Assumptions Identified**: {len(assumptions)}")

        domains = list(self._calculate_domain_distribution(assumptions).keys())
        md.append(f"- **Domains Covered**: {', '.join(domains)}")
        md.append(f"- **Extraction Model**: {metadata.get('extraction_model', 'N/A')}")

        if metadata.get('consistency_score'):
            md.append(f"- **Consistency Score**: {metadata['consistency_score']:.2f}")

        md.append("")

        # Baseline Narrative (if available)
        if narrative and narrative.get("summary"):
            md.append("## Baseline Narrative")
            md.append("")
            md.append(narrative["summary"])
            md.append("")

            if narrative.get("themes"):
                md.append("### Narrative Themes")
                md.append("")
                for theme in narrative["themes"]:
                    md.append(f"- **{theme}**")
                md.append("")

        # Assumptions by Priority
        md.append("## Assumptions by Priority")
        md.append("")

        priority_groups = self._group_by_priority(assumptions)

        for priority in ["high", "needs_review", "medium", "low"]:
            group = priority_groups.get(priority, [])
            if not group:
                continue

            emoji = {
                "high": "🔴",
                "needs_review": "⚠️",
                "medium": "🟡",
                "low": "🟢"
            }.get(priority, "")

            md.append(f"### {emoji} {priority.replace('_', ' ').title()} Priority ({len(group)})")
            md.append("")

            for i, assumption in enumerate(group, 1):
                md.append(f"**{i}. {assumption['text']}**")
                md.append("")
                md.append(f"- **Domains**: {', '.join(assumption.get('domains', []))}")
                md.append(f"- **Quality Score**: {assumption.get('quality_score', 'N/A'):.1f}/100")
                md.append(f"- **Confidence**: {assumption.get('confidence', 0.0):.0%}")

                if assumption.get('source_excerpt'):
                    md.append(f"- **Source**: \"{assumption['source_excerpt'][:100]}...\"")

                if assumption.get('is_cross_domain'):
                    md.append(f"- **Note**: Cross-domain assumption")

                md.append("")

        # Assumptions by Domain
        md.append("## Assumptions by Domain")
        md.append("")

        domain_groups = self._group_by_domain(assumptions)

        for domain, group in sorted(domain_groups.items()):
            md.append(f"### {domain.title()} ({len(group)})")
            md.append("")

            for i, assumption in enumerate(group, 1):
                priority_emoji = {
                    "high": "🔴",
                    "needs_review": "⚠️",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(assumption.get("priority_tier"), "")

                md.append(f"{i}. **[{priority_emoji} {assumption.get('priority_tier', 'unknown').title()}]** {assumption['text']}")
                md.append(f"   - Confidence: {assumption.get('confidence', 0.0):.0%}, Quality: {assumption.get('quality_score', 0):.1f}/100")
                md.append("")

        # Relationships (if available)
        if relationships and relationships.get("statistics"):
            md.append("## Assumption Relationships")
            md.append("")

            stats = relationships["statistics"]
            md.append(f"- **Total Relationships**: {stats.get('relationships_found', 0)}")
            md.append(f"  - Dependencies: {stats.get('dependencies', 0)}")
            md.append(f"  - Reinforcements: {stats.get('reinforcements', 0)}")
            md.append(f"  - Contradictions: {stats.get('contradictions', 0)}")
            md.append("")

            graph_analysis = relationships.get("graph_analysis", {})

            if graph_analysis.get("critical_assumptions"):
                md.append("### Critical Assumptions")
                md.append("")
                md.append("These assumptions have many dependencies:")
                md.append("")
                for assumption_id in graph_analysis["critical_assumptions"]:
                    # Find assumption by ID
                    assumption = next((a for a in assumptions if a["id"] == assumption_id), None)
                    if assumption:
                        md.append(f"- **{assumption_id}**: {assumption['text']}")
                md.append("")

            if graph_analysis.get("contradiction_pairs"):
                md.append("### Contradictory Assumptions")
                md.append("")
                for id_a, id_b in graph_analysis["contradiction_pairs"]:
                    a = next((a for a in assumptions if a["id"] == id_a), None)
                    b = next((a for a in assumptions if a["id"] == id_b), None)
                    if a and b:
                        md.append(f"- **{id_a}** ↔ **{id_b}**")
                        md.append(f"  - {a['text']}")
                        md.append(f"  - {b['text']}")
                        md.append("")

        # Summary Statistics
        md.append("## Summary Statistics")
        md.append("")

        domain_dist = self._calculate_domain_distribution(assumptions)
        priority_dist = self._calculate_priority_distribution(assumptions)

        avg_quality = sum(a.get("quality_score", 0) for a in assumptions) / len(assumptions) if assumptions else 0
        avg_confidence = sum(a.get("confidence", 0) for a in assumptions) / len(assumptions) if assumptions else 0

        md.append(f"- **Average Quality Score**: {avg_quality:.1f}/100")
        md.append(f"- **Average Confidence**: {avg_confidence:.0%}")
        md.append(f"- **High-Priority Assumptions**: {priority_dist.get('high', 0)}")
        md.append(f"- **Cross-Domain Assumptions**: {sum(1 for a in assumptions if a.get('is_cross_domain'))}")
        md.append("")

        # Footer
        md.append("---")
        md.append("")
        md.append(f"*Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
        md.append("")

        return "\n".join(md)

    def _calculate_domain_distribution(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate domain distribution."""
        distribution = {}
        for assumption in assumptions:
            for domain in assumption.get("domains", []):
                distribution[domain] = distribution.get(domain, 0) + 1
        return distribution

    def _calculate_priority_distribution(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate priority distribution."""
        distribution = {}
        for assumption in assumptions:
            priority = assumption.get("priority_tier", "unknown")
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution

    def _group_by_priority(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group assumptions by priority tier."""
        groups = {
            "high": [],
            "needs_review": [],
            "medium": [],
            "low": []
        }

        for assumption in assumptions:
            priority = assumption.get("priority_tier", "low")
            if priority in groups:
                groups[priority].append(assumption)

        return groups

    def _group_by_domain(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group assumptions by domain (primary domain)."""
        groups = {}

        for assumption in assumptions:
            domains = assumption.get("domains", ["unknown"])
            primary_domain = domains[0]

            if primary_domain not in groups:
                groups[primary_domain] = []

            groups[primary_domain].append(assumption)

        return groups
