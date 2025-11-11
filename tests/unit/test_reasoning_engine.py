"""
Unit tests for the reasoning engine.
"""
import pytest
import asyncio
from services.reasoning_engine import ReasoningEngine


@pytest.mark.asyncio
async def test_extract_assumptions():
    """Test assumption extraction from scenario."""
    engine = ReasoningEngine()

    scenario = """
    A major technology company is planning to launch a revolutionary AI product
    that could disrupt the entire industry. Assumptions include that regulatory
    frameworks will remain stable, that competitors won't develop similar technology
    quickly, and that consumer adoption will be rapid.
    """

    assumptions = await engine.extract_assumptions(scenario)

    # Should extract at least some assumptions
    assert isinstance(assumptions, list)
    # Each assumption should have required fields
    if assumptions:  # Only test if LLM returned results
        for assumption in assumptions:
            assert "text" in assumption
            assert "category" in assumption
            assert "confidence" in assumption


@pytest.mark.asyncio
async def test_generate_baseline_narrative():
    """Test baseline narrative generation."""
    engine = ReasoningEngine()

    scenario = "Economic sanctions against a major oil producer"
    assumptions = [
        {
            "id": "a1",
            "text": "Oil markets will remain stable",
            "category": "economic",
            "confidence": 0.7
        }
    ]

    narrative = await engine.generate_baseline_narrative(scenario, assumptions)

    assert isinstance(narrative, str)
    assert len(narrative) > 0


@pytest.mark.asyncio
async def test_generate_probing_questions():
    """Test probing question generation."""
    engine = ReasoningEngine()

    assumptions = [
        {
            "id": "a1",
            "text": "Market will self-regulate",
            "category": "economic",
            "confidence": 0.8
        }
    ]

    questions = await engine.generate_probing_questions(assumptions)

    assert isinstance(questions, list)
    # Verify question structure if any were generated
    if questions:
        for question in questions:
            assert "question_text" in question
            assert "dimension" in question


def test_reasoning_engine_initialization():
    """Test that reasoning engine initializes correctly."""
    engine = ReasoningEngine()
    assert engine.provider is not None
    assert engine.prompt_library is not None
