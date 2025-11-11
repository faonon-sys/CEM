"""
Unit tests for Sprint 2 services.
Tests extraction, categorization, scoring, relationships, and synthesis.
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from services.assumption_categorizer import AssumptionCategorizer, DOMAIN_TAXONOMY
from services.quality_scorer import AssumptionQualityScorer
from services.export_formatter import ExportFormatter


class TestAssumptionCategorizer:
    """Test assumption categorization system."""

    def setup_method(self):
        self.categorizer = AssumptionCategorizer()

    def test_single_domain_categorization(self):
        """Test categorization of single-domain assumption."""
        assumption = {
            "id": "test_1",
            "text": "The government will implement new regulations on financial markets",
            "category": "political"
        }

        result = self.categorizer.categorize(assumption)

        assert "domains" in result
        assert len(result["domains"]) >= 1
        assert "political" in result["domains"] or "economic" in result["domains"]
        assert "domain_confidence" in result

    def test_multi_domain_categorization(self):
        """Test categorization of cross-domain assumption."""
        assumption = {
            "id": "test_2",
            "text": "Global supply chain disruptions will cause economic recession and political instability",
            "category": "economic"
        }

        result = self.categorizer.categorize(assumption)

        assert "domains" in result
        assert result.get("is_cross_domain", False) or len(result["domains"]) > 1

    def test_domain_distribution(self):
        """Test domain distribution calculation."""
        assumptions = [
            {"id": "1", "text": "Political assumption", "domains": ["political"]},
            {"id": "2", "text": "Economic assumption", "domains": ["economic"]},
            {"id": "3", "text": "Political assumption", "domains": ["political"]},
        ]

        distribution = self.categorizer.get_domain_distribution(assumptions)

        assert distribution["political"] == 2
        assert distribution["economic"] == 1

    def test_filter_by_domain(self):
        """Test filtering assumptions by domain."""
        assumptions = [
            {"id": "1", "domains": ["political"]},
            {"id": "2", "domains": ["economic", "political"]},
            {"id": "3", "domains": ["technological"]},
        ]

        filtered = self.categorizer.filter_by_domain(assumptions, ["political"])

        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "2"


class TestQualityScorer:
    """Test quality scoring system."""

    def setup_method(self):
        self.scorer = AssumptionQualityScorer()

    def test_high_quality_assumption(self):
        """Test scoring of high-quality assumption."""
        assumption = {
            "id": "test_1",
            "text": "The Federal Reserve will raise interest rates by 0.25% in Q3 2024, resulting in a 10% reduction in mortgage applications",
            "domains": ["economic", "political"],
            "confidence": 0.85,
            "source_excerpt": "According to the Fed's official statement dated March 15, 2024"
        }

        quality = self.scorer.score(assumption)

        assert quality.composite >= 60  # Should score as medium-high quality
        assert quality.priority_tier in ["high", "medium"]
        assert "specificity" in quality.dimensions
        assert quality.dimensions["specificity"] > 50  # Has numbers and dates

    def test_vague_assumption(self):
        """Test scoring of vague assumption."""
        assumption = {
            "id": "test_2",
            "text": "Things might get better or worse in the future",
            "domains": ["strategic"],
            "confidence": 0.4,
            "source_excerpt": ""
        }

        quality = self.scorer.score(assumption)

        assert quality.composite < 50  # Should score low
        assert quality.priority_tier in ["low", "needs_review"]

    def test_needs_review_tier(self):
        """Test that low confidence triggers needs_review tier."""
        assumption = {
            "id": "test_3",
            "text": "Specific assumption with numbers: GDP will grow 3.5%",
            "domains": ["economic"],
            "confidence": 0.4,  # Low confidence
            "source_excerpt": "Source text"
        }

        quality = self.scorer.score(assumption)

        assert quality.priority_tier == "needs_review"

    def test_batch_scoring(self):
        """Test batch scoring and sorting."""
        assumptions = [
            {
                "id": "low",
                "text": "Vague assumption",
                "domains": ["strategic"],
                "confidence": 0.5,
                "source_excerpt": ""
            },
            {
                "id": "high",
                "text": "The GDP will increase by 5.2% in Q4 2024 according to IMF projections",
                "domains": ["economic", "political"],
                "confidence": 0.9,
                "source_excerpt": "IMF report page 25"
            }
        ]

        scored = self.scorer.score_batch(assumptions)

        # Should be sorted by priority
        assert scored[0]["id"] == "high"
        assert scored[0]["priority_tier"] == "high"

    def test_impact_scoring_multi_domain(self):
        """Test that multi-domain assumptions score higher impact."""
        single_domain = {
            "id": "single",
            "text": "Economic growth will continue",
            "domains": ["economic"],
            "confidence": 0.7,
            "source_excerpt": ""
        }

        multi_domain = {
            "id": "multi",
            "text": "Economic growth will continue",
            "domains": ["economic", "political", "social"],
            "confidence": 0.7,
            "source_excerpt": ""
        }

        score_single = self.scorer.score(single_domain)
        score_multi = self.scorer.score(multi_domain)

        assert score_multi.dimensions["impact_potential"] > score_single.dimensions["impact_potential"]


class TestExportFormatter:
    """Test export formatting system."""

    def setup_method(self):
        self.formatter = ExportFormatter()

    def test_json_export(self):
        """Test JSON export format."""
        scenario = {
            "id": "test-uuid",
            "title": "Test Scenario",
            "description": "Test description",
            "created_at": "2024-01-01T00:00:00",
            "user_id": "user-uuid"
        }

        assumptions = [
            {
                "id": "assumption_1",
                "text": "Test assumption",
                "domains": ["political"],
                "quality_score": 75.5,
                "confidence": 0.8,
                "priority_tier": "high"
            }
        ]

        metadata = {
            "extraction_model": "claude-3.5-sonnet",
            "prompt_version": "v2.0"
        }

        json_output = self.formatter.export_json(scenario, assumptions, metadata)

        assert "scenario" in json_output
        assert "assumptions" in json_output
        assert "metadata" in json_output
        assert "test-uuid" in json_output

    def test_markdown_export(self):
        """Test Markdown export format."""
        scenario = {
            "id": "test-uuid",
            "title": "Test Scenario",
            "description": "Test description",
            "created_at": "2024-01-01T00:00:00",
            "user_id": "user-uuid"
        }

        assumptions = [
            {
                "id": "assumption_1",
                "text": "High priority assumption",
                "domains": ["political", "economic"],
                "quality_score": 85.0,
                "confidence": 0.9,
                "priority_tier": "high",
                "is_cross_domain": True
            },
            {
                "id": "assumption_2",
                "text": "Low priority assumption",
                "domains": ["social"],
                "quality_score": 35.0,
                "confidence": 0.5,
                "priority_tier": "low",
                "is_cross_domain": False
            }
        ]

        metadata = {
            "extraction_model": "claude-3.5-sonnet"
        }

        md_output = self.formatter.export_markdown(scenario, assumptions, metadata)

        # Check structure
        assert "# Scenario Analysis" in md_output
        assert "## Overview" in md_output
        assert "## Assumptions by Priority" in md_output
        assert "### 🔴 High Priority" in md_output
        assert "### 🟢 Low Priority" in md_output
        assert "Cross-domain assumption" in md_output

    def test_domain_grouping(self):
        """Test assumptions are grouped by domain correctly."""
        assumptions = [
            {"id": "1", "domains": ["political"], "priority_tier": "high"},
            {"id": "2", "domains": ["political"], "priority_tier": "medium"},
            {"id": "3", "domains": ["economic"], "priority_tier": "high"},
        ]

        groups = self.formatter._group_by_domain(assumptions)

        assert "political" in groups
        assert "economic" in groups
        assert len(groups["political"]) == 2
        assert len(groups["economic"]) == 1


class TestDomainTaxonomy:
    """Test domain taxonomy completeness."""

    def test_all_domains_have_keywords(self):
        """Ensure all domains have keyword lists."""
        for domain, config in DOMAIN_TAXONOMY.items():
            assert "keywords" in config
            assert len(config["keywords"]) > 0

    def test_all_domains_have_subcategories(self):
        """Ensure all domains have subcategories."""
        for domain, config in DOMAIN_TAXONOMY.items():
            assert "subcategories" in config
            assert len(config["subcategories"]) > 0

    def test_no_duplicate_keywords(self):
        """Check for duplicate keywords within domains."""
        for domain, config in DOMAIN_TAXONOMY.items():
            keywords = config["keywords"]
            assert len(keywords) == len(set(keywords)), f"Duplicate keywords in {domain}"


# Integration-style tests (require mocking or actual LLM)
@pytest.mark.skip(reason="Requires LLM provider - run manually")
class TestIntegration:
    """Integration tests requiring LLM provider."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete Sprint 2 pipeline."""
        from services.assumption_extractor import AssumptionExtractor
        from services.assumption_categorizer import AssumptionCategorizer
        from services.quality_scorer import AssumptionQualityScorer

        scenario_text = """
        The Federal Reserve is expected to maintain interest rates at current levels
        throughout 2024, assuming inflation continues to decline. This policy stance
        depends on stable employment figures and no major geopolitical disruptions.
        Market participants believe this will support continued economic growth.
        """

        # Extract
        extractor = AssumptionExtractor()
        extraction_result = await extractor.extract(scenario_text, validate_consistency=False)
        assumptions = extraction_result["assumptions"]

        assert len(assumptions) > 0

        # Categorize
        categorizer = AssumptionCategorizer()
        assumptions = categorizer.categorize_batch(assumptions)

        assert all("domains" in a for a in assumptions)

        # Score
        scorer = AssumptionQualityScorer()
        assumptions = scorer.score_batch(assumptions)

        assert all("quality_score" in a for a in assumptions)
        assert all("priority_tier" in a for a in assumptions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
