"""
End-to-End Workflow Integration Tests
Tests the complete five-phase workflow from input to strategic outcomes.
"""
import pytest
import asyncio
from typing import Dict, List, Any
import json
import time
from httpx import AsyncClient
from datetime import datetime

# Test scenario fixtures
from tests.test_scenarios import (
    GEOPOLITICAL_SCENARIOS,
    ECONOMIC_SCENARIOS,
    OPERATIONAL_SCENARIOS
)


class TestEndToEndWorkflow:
    """Test complete workflow execution across all 5 phases"""

    @pytest.mark.asyncio
    async def test_full_workflow_happy_path(self, api_client: AsyncClient, auth_token: str):
        """Test standard geopolitical crisis scenario through all phases"""
        scenario = GEOPOLITICAL_SCENARIOS[0]  # Taiwan Strait escalation

        # Phase 0: Create scenario
        response = await api_client.post(
            "/api/scenarios/",
            json={
                "title": scenario.title,
                "description": scenario.description
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        scenario_data = response.json()
        scenario_id = scenario_data["id"]

        # Phase 1: Surface Analysis
        start_time = time.time()
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assumptions = response.json()

        # Validate Phase 1 output
        assert len(assumptions) >= scenario.expected_assumptions * 0.8, \
            f"Expected at least {scenario.expected_assumptions * 0.8} assumptions"
        assert all("domain" in a for a in assumptions), "All assumptions must have domain"
        assert all("confidence" in a for a in assumptions), "All assumptions must have confidence"

        # Phase 2: Deep Questioning
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/deep-questions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        questions = response.json()

        # Validate Phase 2 output
        assert len(questions) >= 10, "Should generate at least 10 questions"
        dimensions = set(q.get("dimension") for q in questions)
        expected_dimensions = {"temporal", "structural", "actor", "resource"}
        assert len(dimensions & expected_dimensions) >= 3, \
            "Should cover at least 3 questioning dimensions"

        # Phase 3: Counterfactual Generation
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/counterfactuals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        counterfactuals = response.json()

        # Validate Phase 3 output
        assert len(counterfactuals) >= 6, "Should generate counterfactuals for 6 axes"
        assert all("breach_condition" in cf for cf in counterfactuals)
        assert all("consequences" in cf for cf in counterfactuals)
        assert all("severity" in cf for cf in counterfactuals)
        assert all("probability" in cf for cf in counterfactuals)

        # Phase 5: Strategic Outcomes
        counterfactual_id = counterfactuals[0]["id"]
        response = await api_client.post(
            f"/api/counterfactuals/{counterfactual_id}/outcomes",
            json={"timeframe_months": 24},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        outcomes = response.json()

        # Validate Phase 5 output
        assert "trajectories" in outcomes
        assert "decision_points" in outcomes
        assert "inflection_points" in outcomes
        assert len(outcomes["trajectories"]) > 0

        # Performance check: should complete in < 5 minutes
        elapsed = time.time() - start_time
        assert elapsed < 300, f"Workflow took {elapsed}s, should be <300s"

        print(f"✅ Full workflow completed in {elapsed:.2f}s")

    @pytest.mark.asyncio
    async def test_phase_transitions_data_integrity(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Verify data flows correctly between phases"""
        # Create scenario
        response = await api_client.post(
            "/api/scenarios/",
            json={
                "title": "Data Integrity Test",
                "description": "Testing assumption: Markets assume stability. Testing assumption: Supply chains are resilient."
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        scenario_id = response.json()["id"]

        # Phase 1: Extract assumptions
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assumptions = response.json()
        assumption_ids = [a["id"] for a in assumptions]

        # Phase 2: Generate questions
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/deep-questions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        questions = response.json()

        # Verify linkage: Questions should reference assumptions
        linked_assumption_ids = set()
        for q in questions:
            if "assumption_id" in q:
                linked_assumption_ids.add(q["assumption_id"])

        # At least 70% of assumptions should have questions
        linkage_rate = len(linked_assumption_ids) / len(assumption_ids)
        assert linkage_rate >= 0.7, \
            f"Only {linkage_rate*100}% of assumptions have questions, expected >70%"

        # Phase 3: Counterfactuals should reference scenario
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/counterfactuals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        counterfactuals = response.json()

        for cf in counterfactuals:
            assert cf["scenario_id"] == scenario_id, "Counterfactual must link to scenario"

        print("✅ Phase transitions maintain data integrity")

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Test workflow handles errors gracefully and can recover"""
        # Test 1: Invalid input handling
        response = await api_client.post(
            "/api/scenarios/",
            json={"title": "", "description": ""},  # Empty fields
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422, "Should reject empty input"

        # Test 2: Non-existent scenario
        response = await api_client.post(
            "/api/scenarios/99999/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404

        # Test 3: Recovery after failed phase
        response = await api_client.post(
            "/api/scenarios/",
            json={
                "title": "Recovery Test",
                "description": "Testing error recovery mechanisms in the analysis pipeline."
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        scenario_id = response.json()["id"]

        # Even if Phase 1 succeeds, we should be able to re-run it
        response1 = await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response1.status_code == 200

        response2 = await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response2.status_code == 200

        print("✅ Error recovery working correctly")

    @pytest.mark.asyncio
    async def test_concurrent_workflows(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Test system handles multiple concurrent analyses"""
        scenarios = [
            {"title": f"Concurrent Test {i}", "description": f"Testing concurrent analysis {i}"}
            for i in range(5)
        ]

        # Create all scenarios concurrently
        create_tasks = [
            api_client.post(
                "/api/scenarios/",
                json=scenario,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            for scenario in scenarios
        ]

        responses = await asyncio.gather(*create_tasks)
        scenario_ids = [r.json()["id"] for r in responses if r.status_code == 201]

        assert len(scenario_ids) == 5, "All scenarios should be created"

        # Run Phase 1 on all concurrently
        analysis_tasks = [
            api_client.post(
                f"/api/scenarios/{sid}/surface-analysis",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            for sid in scenario_ids
        ]

        start = time.time()
        analysis_responses = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        elapsed = time.time() - start

        successful = sum(1 for r in analysis_responses
                        if not isinstance(r, Exception) and r.status_code == 200)

        assert successful >= 4, f"At least 4/5 concurrent analyses should succeed"

        print(f"✅ {successful}/5 concurrent workflows completed in {elapsed:.2f}s")


class TestPhaseQuality:
    """Test output quality for each phase"""

    @pytest.mark.asyncio
    async def test_assumption_extraction_quality(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Validate Phase 1 assumption quality"""
        from tests.quality_rubrics import QualityRubric

        scenario = GEOPOLITICAL_SCENARIOS[0]
        response = await api_client.post(
            "/api/scenarios/",
            json={"title": scenario.title, "description": scenario.description},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        scenario_id = response.json()["id"]

        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assumptions = response.json()

        # Quality evaluation
        score = QualityRubric.evaluate_assumptions(assumptions)
        assert score >= 7.0, f"Assumption quality score {score} is below 7.0 threshold"

        # Check for vague language
        vague_words = ['might', 'could', 'possibly', 'maybe', 'perhaps']
        vague_count = sum(
            1 for a in assumptions
            if any(word in a.get("description", "").lower() for word in vague_words)
        )
        vague_rate = vague_count / len(assumptions)
        assert vague_rate < 0.3, f"Too many vague assumptions: {vague_rate*100}%"

        print(f"✅ Assumption quality score: {score:.2f}/10")

    @pytest.mark.asyncio
    async def test_question_depth_quality(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Validate Phase 2 question quality"""
        from tests.quality_rubrics import QualityRubric

        scenario = ECONOMIC_SCENARIOS[0]
        response = await api_client.post(
            "/api/scenarios/",
            json={"title": scenario.title, "description": scenario.description},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        scenario_id = response.json()["id"]

        # Run Phase 1 first
        await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Phase 2: Questions
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/deep-questions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        questions = response.json()

        score = QualityRubric.evaluate_questions(questions)
        assert score >= 7.0, f"Question quality score {score} is below 7.0 threshold"

        # Check for deep probing
        deep_indicators = ['why', 'how', 'what if', 'under what conditions']
        deep_count = sum(
            1 for q in questions
            if any(ind in q.get("text", "").lower() for ind in deep_indicators)
        )
        deep_rate = deep_count / len(questions)
        assert deep_rate >= 0.6, f"Only {deep_rate*100}% questions probe deeply"

        print(f"✅ Question quality score: {score:.2f}/10")

    @pytest.mark.asyncio
    async def test_counterfactual_plausibility(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Validate Phase 3 counterfactual quality"""
        from tests.quality_rubrics import QualityRubric

        scenario = GEOPOLITICAL_SCENARIOS[1]
        response = await api_client.post(
            "/api/scenarios/",
            json={"title": scenario.title, "description": scenario.description},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        scenario_id = response.json()["id"]

        # Run Phase 1 & 2
        await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        await api_client.post(
            f"/api/scenarios/{scenario_id}/deep-questions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Phase 3: Counterfactuals
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/counterfactuals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        counterfactuals = response.json()

        score = QualityRubric.evaluate_counterfactuals(counterfactuals)
        assert score >= 6.5, f"Counterfactual quality score {score} is below 6.5"

        # Check breach condition specificity (should be > 10 words)
        specific_breaches = sum(
            1 for cf in counterfactuals
            if len(cf.get("breach_condition", "").split()) >= 10
        )
        specificity_rate = specific_breaches / len(counterfactuals)
        assert specificity_rate >= 0.7, f"Only {specificity_rate*100}% have specific breach conditions"

        print(f"✅ Counterfactual quality score: {score:.2f}/10")


class TestPerformance:
    """Performance and scalability tests"""

    @pytest.mark.asyncio
    async def test_workflow_performance_baseline(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Measure baseline performance for optimization tracking"""
        scenario = {
            "title": "Performance Test",
            "description": "A standard scenario for performance benchmarking. " * 50  # ~500 words
        }

        # Create scenario
        start = time.time()
        response = await api_client.post(
            "/api/scenarios/",
            json=scenario,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        scenario_id = response.json()["id"]
        create_time = time.time() - start

        # Phase 1
        start = time.time()
        await api_client.post(
            f"/api/scenarios/{scenario_id}/surface-analysis",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        phase1_time = time.time() - start

        # Phase 2
        start = time.time()
        await api_client.post(
            f"/api/scenarios/{scenario_id}/deep-questions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        phase2_time = time.time() - start

        # Phase 3
        start = time.time()
        response = await api_client.post(
            f"/api/scenarios/{scenario_id}/counterfactuals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        phase3_time = time.time() - start

        total_time = create_time + phase1_time + phase2_time + phase3_time

        # Store baseline for comparison
        baseline = {
            "timestamp": datetime.now().isoformat(),
            "create_time": create_time,
            "phase1_time": phase1_time,
            "phase2_time": phase2_time,
            "phase3_time": phase3_time,
            "total_time": total_time
        }

        print(f"""
        📊 Performance Baseline:
        - Create: {create_time:.2f}s
        - Phase 1: {phase1_time:.2f}s
        - Phase 2: {phase2_time:.2f}s
        - Phase 3: {phase3_time:.2f}s
        - Total: {total_time:.2f}s
        """)

        # Save baseline to file
        with open("/Users/raminhedayatpour/Documents/VibeProjects/test/tests/performance_baseline.json", "w") as f:
            json.dump(baseline, f, indent=2)

        # Assert reasonable performance (not optimized yet)
        assert total_time < 180, f"Baseline total time {total_time}s exceeds 3 minutes"

    @pytest.mark.asyncio
    async def test_api_response_latency(
        self,
        api_client: AsyncClient,
        auth_token: str
    ):
        """Test API endpoint response times"""
        # List scenarios endpoint
        latencies = []
        for _ in range(10):
            start = time.time()
            response = await api_client.get(
                "/api/scenarios/",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"""
        📊 API Latency:
        - Average: {avg_latency*1000:.0f}ms
        - P95: {p95_latency*1000:.0f}ms
        """)

        # Target: P95 < 500ms (will improve with optimization)
        assert p95_latency < 1.0, f"P95 latency {p95_latency*1000}ms exceeds 1000ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
