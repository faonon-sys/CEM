"""
Pytest configuration and fixtures for integration tests.
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.database import Base
from backend.main import app

# Use test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://reasoning_user:reasoning_pass@localhost:5432/reasoning_test_db"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a new database session for a test."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_scenario():
    """Provide a sample scenario for testing."""
    return {
        "title": "Test Scenario",
        "description": "A test scenario for unit testing the reasoning system."
    }


@pytest.fixture
async def api_client():
    """Create async HTTP client for API testing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user(api_client: AsyncClient):
    """Create a test user and return user data"""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }

    response = await api_client.post("/api/auth/register", json=user_data)

    if response.status_code == 201:
        return response.json()
    elif response.status_code == 400:  # User already exists
        # Login instead
        login_response = await api_client.post(
            "/api/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )
        return login_response.json()
    else:
        pytest.fail(f"Failed to create test user: {response.status_code}")


@pytest.fixture
async def auth_token(test_user):
    """Get authentication token for test user"""
    return test_user.get("access_token")


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing without API calls"""
    return {
        "assumptions": [
            {
                "description": "Markets assume stability",
                "domain": "economic",
                "confidence": 0.7,
                "category": "market_dynamics"
            },
            {
                "description": "Supply chains are resilient",
                "domain": "operational",
                "confidence": 0.6,
                "category": "infrastructure"
            }
        ],
        "questions": [
            {
                "text": "What evidence supports the stability assumption?",
                "dimension": "structural",
                "assumption_id": "1"
            },
            {
                "text": "How quickly can supply chains adapt?",
                "dimension": "temporal",
                "assumption_id": "2"
            }
        ]
    }


# Configure pytest-asyncio
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test collection hook
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "e2e" in item.name or "workflow" in item.name:
            item.add_marker(pytest.mark.slow)
