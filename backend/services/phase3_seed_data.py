"""
Phase 3 Seed Data Generator
Sprint 4 - Task 1: Test Data

Generates comprehensive seed data for testing Phase 3 counterfactual framework.
Includes 10 diverse test scenarios across multiple domains.
"""
from typing import List, Dict
import uuid
from datetime import datetime, timedelta


class Phase3SeedData:
    """Seed data generator for Phase 3 testing."""

    @staticmethod
    def generate_test_scenarios() -> List[Dict]:
        """Generate 10 diverse test scenarios with Phase 2 fragilities."""
        return [
            # Scenario 1: Geopolitical Crisis
            {
                "id": str(uuid.uuid4()),
                "title": "Taiwan Strait Crisis 2025",
                "description": "Escalating military tensions between China and Taiwan with US involvement",
                "domain": "geopolitical",
                "fragilities": [
                    {
                        "assumption_id": "geo_001",
                        "description": "Assumption that military readiness can be achieved within 90 days",
                        "fragility_score": 8.2,
                        "breach_probability": 0.65,
                        "evidence_gaps": ["No data on historical precedent", "Unclear logistical constraints"],
                        "severity": "critical"
                    },
                    {
                        "assumption_id": "geo_002",
                        "description": "Allies will maintain unified response",
                        "fragility_score": 7.5,
                        "breach_probability": 0.55,
                        "evidence_gaps": ["Unclear domestic political constraints"],
                        "severity": "high"
                    }
                ]
            },

            # Scenario 2: Economic Crisis
            {
                "id": str(uuid.uuid4()),
                "title": "Sovereign Debt Crisis 2026",
                "description": "Major economy faces bond market confidence loss and debt sustainability crisis",
                "domain": "economic",
                "fragilities": [
                    {
                        "assumption_id": "econ_001",
                        "description": "Central bank can absorb unlimited sovereign debt",
                        "fragility_score": 8.5,
                        "breach_probability": 0.45,
                        "evidence_gaps": ["Unknown threshold for market confidence loss"],
                        "severity": "critical"
                    },
                    {
                        "assumption_id": "econ_002",
                        "description": "International capital will not flee en masse",
                        "fragility_score": 7.8,
                        "breach_probability": 0.52,
                        "evidence_gaps": ["Limited data on capital flight dynamics"],
                        "severity": "high"
                    }
                ]
            },

            # Scenario 3: Technology Disruption
            {
                "id": str(uuid.uuid4()),
                "title": "AI Capability Breakthrough",
                "description": "Unexpected AI system achieves AGI-level reasoning, disrupting strategic balance",
                "domain": "technology",
                "fragilities": [
                    {
                        "assumption_id": "tech_001",
                        "description": "AGI development timeline assumes 10+ years",
                        "fragility_score": 6.5,
                        "breach_probability": 0.35,
                        "evidence_gaps": ["Unclear technical barriers"],
                        "severity": "high"
                    }
                ]
            },

            # Scenario 4: Climate Event
            {
                "id": str(uuid.uuid4()),
                "title": "Catastrophic Flooding Event",
                "description": "Major coastal infrastructure destroyed by unprecedented flooding",
                "domain": "environmental",
                "fragilities": [
                    {
                        "assumption_id": "env_001",
                        "description": "Infrastructure can withstand 100-year storm events",
                        "fragility_score": 7.2,
                        "breach_probability": 0.48,
                        "evidence_gaps": ["Climate model uncertainty"],
                        "severity": "high"
                    }
                ]
            },

            # Scenario 5: Public Health Crisis
            {
                "id": str(uuid.uuid4()),
                "title": "Novel Pandemic Outbreak",
                "description": "Highly transmissible novel pathogen emerges with vaccine-resistant properties",
                "domain": "health",
                "fragilities": [
                    {
                        "assumption_id": "health_001",
                        "description": "Vaccine development can occur within 12 months",
                        "fragility_score": 6.8,
                        "breach_probability": 0.42,
                        "evidence_gaps": ["Unknown pathogen characteristics"],
                        "severity": "high"
                    }
                ]
            },

            # Scenario 6: Supply Chain Disruption
            {
                "id": str(uuid.uuid4()),
                "title": "Global Semiconductor Shortage",
                "description": "Critical semiconductor production facilities offline for extended period",
                "domain": "operational",
                "fragilities": [
                    {
                        "assumption_id": "supply_001",
                        "description": "Alternative suppliers can cover 60% of capacity",
                        "fragility_score": 8.0,
                        "breach_probability": 0.58,
                        "evidence_gaps": ["Unclear technical compatibility"],
                        "severity": "critical"
                    }
                ]
            },

            # Scenario 7: Cyber Attack
            {
                "id": str(uuid.uuid4()),
                "title": "Critical Infrastructure Cyber Attack",
                "description": "Coordinated attack on power grid and financial systems",
                "domain": "security",
                "fragilities": [
                    {
                        "assumption_id": "cyber_001",
                        "description": "Air-gapped systems prevent cascade failures",
                        "fragility_score": 7.5,
                        "breach_probability": 0.50,
                        "evidence_gaps": ["Unknown attack vectors"],
                        "severity": "critical"
                    }
                ]
            },

            # Scenario 8: Political Upheaval
            {
                "id": str(uuid.uuid4()),
                "title": "Democratic Governance Crisis",
                "description": "Contested election results lead to institutional paralysis",
                "domain": "political",
                "fragilities": [
                    {
                        "assumption_id": "pol_001",
                        "description": "Institutional norms will hold under pressure",
                        "fragility_score": 6.9,
                        "breach_probability": 0.44,
                        "evidence_gaps": ["Historical precedent limited"],
                        "severity": "high"
                    }
                ]
            },

            # Scenario 9: Energy Crisis
            {
                "id": str(uuid.uuid4()),
                "title": "Global Energy Supply Shock",
                "description": "Multiple oil/gas producing regions offline simultaneously",
                "domain": "energy",
                "fragilities": [
                    {
                        "assumption_id": "energy_001",
                        "description": "Strategic reserves sufficient for 6 months",
                        "fragility_score": 7.8,
                        "breach_probability": 0.51,
                        "evidence_gaps": ["Unclear demand elasticity"],
                        "severity": "high"
                    }
                ]
            },

            # Scenario 10: Space Infrastructure
            {
                "id": str(uuid.uuid4()),
                "title": "Satellite Network Degradation",
                "description": "Kessler syndrome event cascades through LEO satellite constellations",
                "domain": "space",
                "fragilities": [
                    {
                        "assumption_id": "space_001",
                        "description": "Satellite redundancy ensures 95% uptime",
                        "fragility_score": 6.5,
                        "breach_probability": 0.38,
                        "evidence_gaps": ["Unknown cascade dynamics"],
                        "severity": "medium"
                    }
                ]
            }
        ]

    @staticmethod
    def generate_expected_breach_conditions() -> Dict[str, List[Dict]]:
        """Generate expected breach conditions for test scenarios."""
        return {
            "geo_001": [
                {
                    "axis": "temporal_shifts",
                    "trigger_event": "Military mobilization accelerates by 6 months",
                    "plausibility": 0.65
                },
                {
                    "axis": "resource_constraints",
                    "trigger_event": "Logistical capacity proves 40% below requirements",
                    "plausibility": 0.72
                }
            ],
            "econ_001": [
                {
                    "axis": "actor_behavior",
                    "trigger_event": "Bond vigilantes refuse to roll over 30% of debt",
                    "plausibility": 0.45
                },
                {
                    "axis": "structural_failures",
                    "trigger_event": "Central bank independence compromised by political pressure",
                    "plausibility": 0.52
                }
            ]
        }

    @staticmethod
    def generate_expected_counterfactuals() -> List[Dict]:
        """Generate expected counterfactual outputs for validation."""
        return [
            {
                "breach_condition_id": "breach_geo_001_temporal",
                "axis": "temporal_shifts",
                "narrative": (
                    "Following unexpected acceleration of military mobilization by 6 months, "
                    "allied forces find themselves unprepared for coordinated response. "
                    "Intelligence systems detect movement patterns indicating imminent action, "
                    "but diplomatic negotiations remain at early stages. Within 48 hours, "
                    "military options narrow to high-risk interventions or acquiescence. "
                    "Economic sanctions prove ineffective due to insufficient preparation time. "
                    "International coalitions fracture as individual nations prioritize "
                    "self-interest over collective security. The compressed timeline forces "
                    "decisions under uncertainty, increasing probability of miscalculation..."
                ),
                "divergence_timeline": [
                    {"date": "Month 0", "event": "Unexpected mobilization detected"},
                    {"date": "Month 1", "event": "Diplomatic efforts prove insufficient"},
                    {"date": "Month 2", "event": "Alliance coordination breaks down"},
                    {"date": "Month 3", "event": "Military confrontation becomes likely"}
                ],
                "affected_domains": ["military", "diplomatic", "economic"],
                "expected_severity": 8.5,
                "expected_probability": 0.62
            }
        ]

    @staticmethod
    def get_validation_criteria() -> Dict:
        """Get validation criteria for test scenarios."""
        return {
            "minimum_counterfactuals": 18,  # 3 per axis × 6 axes
            "narrative_min_words": 200,
            "narrative_max_words": 400,
            "divergence_points_min": 3,
            "divergence_points_max": 5,
            "consequence_depth_min": 2,
            "consequence_depth_max": 5,
            "severity_range": [0.0, 10.0],
            "probability_range": [0.0, 1.0],
            "axes_coverage": [
                "temporal_shifts",
                "actor_behavior",
                "resource_constraints",
                "structural_failures",
                "information_asymmetry",
                "external_shocks"
            ]
        }
