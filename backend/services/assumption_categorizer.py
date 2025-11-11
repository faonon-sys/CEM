"""
Multi-domain assumption categorization system.
Sprint 2 - Task 2: Categorization System with Hybrid Rule-Based + ML
"""
import logging
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


# Domain taxonomy with keywords and subcategories
DOMAIN_TAXONOMY = {
    "political": {
        "keywords": [
            "policy", "regulation", "government", "legislation", "governance",
            "political", "parliament", "congress", "administration", "treaty",
            "diplomatic", "sovereignty", "regime", "election", "coalition",
            "sanctions", "ministry", "bureau", "federal", "state"
        ],
        "subcategories": ["domestic_policy", "geopolitics", "governance", "regulatory"]
    },
    "economic": {
        "keywords": [
            "market", "trade", "financial", "economy", "economic", "fiscal",
            "monetary", "currency", "investment", "budget", "revenue", "profit",
            "cost", "price", "inflation", "gdp", "growth", "recession", "banking",
            "capital", "debt", "credit", "supply", "demand", "commodity"
        ],
        "subcategories": ["macroeconomic", "industry", "labor", "trade", "financial_markets"]
    },
    "technological": {
        "keywords": [
            "technology", "software", "hardware", "digital", "automation",
            "ai", "algorithm", "data", "cyber", "network", "system", "platform",
            "innovation", "engineering", "computing", "infrastructure", "technical",
            "bandwidth", "encryption", "protocol", "semiconductor", "chip"
        ],
        "subcategories": ["infrastructure", "innovation", "cybersecurity", "digital_transformation"]
    },
    "social": {
        "keywords": [
            "social", "public", "society", "community", "population", "demographic",
            "cultural", "behavior", "opinion", "support", "protest", "movement",
            "migration", "education", "health", "welfare", "inequality", "justice",
            "rights", "identity", "cohesion", "trust", "sentiment"
        ],
        "subcategories": ["demographics", "public_opinion", "social_movements", "cultural_dynamics"]
    },
    "operational": {
        "keywords": [
            "operations", "logistics", "supply", "chain", "delivery", "production",
            "manufacturing", "capacity", "process", "implementation", "execution",
            "coordination", "management", "efficiency", "workflow", "timeline",
            "deployment", "maintenance", "distribution", "inventory"
        ],
        "subcategories": ["supply_chain", "logistics", "implementation", "process_management"]
    },
    "strategic": {
        "keywords": [
            "strategy", "strategic", "objective", "goal", "priority", "plan",
            "vision", "mission", "positioning", "competitive", "advantage",
            "alliance", "partnership", "influence", "power", "leadership",
            "decision", "choice", "direction", "intent", "doctrine"
        ],
        "subcategories": ["planning", "positioning", "alliances", "decision_making"]
    },
    "environmental": {
        "keywords": [
            "environment", "climate", "energy", "renewable", "carbon", "emissions",
            "sustainability", "ecological", "natural", "resource", "pollution",
            "conservation", "weather", "temperature", "water", "agriculture",
            "biodiversity", "waste", "green"
        ],
        "subcategories": ["climate", "energy", "natural_resources", "sustainability"]
    },
    "cultural": {
        "keywords": [
            "culture", "cultural", "tradition", "values", "belief", "religion",
            "language", "identity", "heritage", "norm", "custom", "ritual",
            "narrative", "worldview", "ideology", "philosophy", "ethics"
        ],
        "subcategories": ["values", "beliefs", "traditions", "narratives"]
    }
}


class AssumptionCategorizer:
    """
    Hybrid categorization system combining rule-based and semantic approaches.

    Features:
    - Multi-label classification (assumptions can span domains)
    - Confidence scoring for each domain assignment
    - Subcategory assignment within domains
    - Cross-domain assumption detection
    """

    def __init__(self):
        self.taxonomy = DOMAIN_TAXONOMY
        # In production, load pre-trained ML model here
        # self.ml_model = load_model("assumption_classifier.pkl")

    def categorize(self, assumption: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize a single assumption into domains.

        Args:
            assumption: Assumption dict with 'text', 'category', etc.

        Returns:
            Enhanced assumption with 'domains' (list), 'domain_confidence' (dict)
        """
        text = assumption.get("text", "").lower()
        original_category = assumption.get("category", "").lower()

        # Rule-based classification
        domain_scores = self._rule_based_classify(text)

        # Incorporate original category if provided
        if original_category in self.taxonomy:
            domain_scores[original_category] = max(
                domain_scores.get(original_category, 0.0),
                0.8  # High confidence for explicitly tagged domains
            )

        # Select domains above threshold
        threshold = 0.3
        domains = [
            domain for domain, score in domain_scores.items()
            if score >= threshold
        ]

        # Ensure at least one domain
        if not domains:
            if original_category in self.taxonomy:
                domains = [original_category]
            else:
                # Default to highest scoring domain
                if domain_scores:
                    domains = [max(domain_scores, key=domain_scores.get)]
                else:
                    domains = ["strategic"]  # Safe default

        # Add to assumption
        assumption["domains"] = domains
        assumption["domain_confidence"] = {
            domain: domain_scores.get(domain, 0.0)
            for domain in domains
        }
        assumption["is_cross_domain"] = len(domains) > 1

        # Assign subcategories
        assumption["subcategories"] = self._assign_subcategories(text, domains)

        return assumption

    def categorize_batch(self, assumptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize a list of assumptions.

        Args:
            assumptions: List of assumption dicts

        Returns:
            List of enhanced assumptions with domain information
        """
        categorized = []
        for assumption in assumptions:
            categorized.append(self.categorize(assumption))

        # Log statistics
        domain_counts = defaultdict(int)
        cross_domain_count = 0

        for assumption in categorized:
            for domain in assumption["domains"]:
                domain_counts[domain] += 1
            if assumption["is_cross_domain"]:
                cross_domain_count += 1

        logger.info(
            f"Categorized {len(assumptions)} assumptions. "
            f"Cross-domain: {cross_domain_count}. "
            f"Domain distribution: {dict(domain_counts)}"
        )

        return categorized

    def _rule_based_classify(self, text: str) -> Dict[str, float]:
        """
        Rule-based classification using keyword matching.

        Args:
            text: Assumption text (lowercase)

        Returns:
            Dictionary of {domain: confidence_score}
        """
        domain_scores = {}

        for domain, config in self.taxonomy.items():
            keywords = config["keywords"]

            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in text)

            # Calculate score (normalized by number of keywords in domain)
            if matches > 0:
                # More matches = higher confidence
                score = min(matches / 5.0, 1.0)  # Cap at 1.0
                domain_scores[domain] = score

        return domain_scores

    def _assign_subcategories(
        self,
        text: str,
        domains: List[str]
    ) -> Dict[str, str]:
        """
        Assign subcategories within each domain.

        Args:
            text: Assumption text (lowercase)
            domains: List of assigned domains

        Returns:
            Dictionary of {domain: subcategory}
        """
        subcategories = {}

        for domain in domains:
            if domain not in self.taxonomy:
                continue

            # For now, use simple heuristics
            # In production, use ML classifier or more sophisticated rules
            available_subcats = self.taxonomy[domain]["subcategories"]

            if available_subcats:
                # Default to first subcategory
                # TODO: Implement proper subcategory classification
                subcategories[domain] = available_subcats[0]

        return subcategories

    def get_domain_distribution(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Calculate domain distribution across assumptions.

        Args:
            assumptions: List of categorized assumptions

        Returns:
            Dictionary of {domain: count}
        """
        distribution = defaultdict(int)

        for assumption in assumptions:
            for domain in assumption.get("domains", []):
                distribution[domain] += 1

        return dict(distribution)

    def get_cross_domain_assumptions(
        self,
        assumptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get assumptions that span multiple domains.

        Args:
            assumptions: List of categorized assumptions

        Returns:
            List of cross-domain assumptions
        """
        return [
            assumption for assumption in assumptions
            if assumption.get("is_cross_domain", False)
        ]

    def filter_by_domain(
        self,
        assumptions: List[Dict[str, Any]],
        domains: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter assumptions by domains.

        Args:
            assumptions: List of categorized assumptions
            domains: List of domain names to filter by

        Returns:
            Filtered list of assumptions
        """
        return [
            assumption for assumption in assumptions
            if any(domain in assumption.get("domains", []) for domain in domains)
        ]
