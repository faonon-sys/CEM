"""
API client for communicating with the backend.
"""
import httpx
import os
from typing import Dict, Any, List, Optional

# Get backend URL from environment or default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api"


class APIClient:
    """Client for backend API communication."""

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    # Auth endpoints
    async def register(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/auth/register",
                json={"email": email, "password": password}
            )
            response.raise_for_status()
            return response.json()

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/auth/login",
                json={"email": email, "password": password}
            )
            response.raise_for_status()
            return response.json()

    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user info."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/auth/me",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    # Scenario endpoints
    async def create_scenario(self, title: str, description: str) -> Dict[str, Any]:
        """Create a new scenario."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/scenarios/",
                json={"title": title, "description": description},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def list_scenarios(self) -> List[Dict[str, Any]]:
        """List all scenarios."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/scenarios/",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Get a specific scenario."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/scenarios/{scenario_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    # Phase 1: Surface Analysis
    async def create_surface_analysis(self, scenario_id: str) -> Dict[str, Any]:
        """Generate surface analysis for a scenario."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/scenarios/{scenario_id}/surface-analysis",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_surface_analysis(self, scenario_id: str) -> Dict[str, Any]:
        """Get surface analysis for a scenario."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/scenarios/{scenario_id}/surface-analysis",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    # Phase 2: Deep Questions
    async def generate_deep_questions(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Generate deep probing questions."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/scenarios/{scenario_id}/deep-questions",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_deep_questions(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Get deep questions for a scenario."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/scenarios/{scenario_id}/deep-questions",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def respond_to_question(
        self,
        scenario_id: str,
        question_id: str,
        user_response: str,
        relevance_score: Optional[int] = None
    ) -> Dict[str, Any]:
        """Submit response to a deep question."""
        async with httpx.AsyncClient() as client:
            payload = {"user_response": user_response}
            if relevance_score:
                payload["relevance_score"] = relevance_score

            response = await client.post(
                f"{API_BASE}/scenarios/{scenario_id}/deep-questions/{question_id}/respond",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    # Phase 3: Counterfactuals
    async def generate_counterfactuals(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Generate counterfactual scenarios."""
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{API_BASE}/scenarios/{scenario_id}/counterfactuals",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_counterfactuals(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Get counterfactuals for a scenario."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/scenarios/{scenario_id}/counterfactuals",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    # Phase 5: Strategic Outcomes
    async def generate_strategic_outcome(self, counterfactual_id: str) -> Dict[str, Any]:
        """Generate strategic outcome for a counterfactual."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/counterfactuals/{counterfactual_id}/outcomes",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_strategic_outcome(self, counterfactual_id: str) -> Dict[str, Any]:
        """Get strategic outcome for a counterfactual."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/counterfactuals/{counterfactual_id}/outcomes",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
