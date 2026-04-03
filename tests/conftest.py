"""
Pytest fixtures for the Trade Opportunities API test suite.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app


@pytest.fixture()
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture()
def guest_token() -> str:
    """Create a valid guest JWT token for testing."""
    return create_access_token({"guest_id": "test-guest-001"})


@pytest.fixture()
def auth_headers(guest_token: str) -> dict[str, str]:
    """Create authorization headers with a valid guest token."""
    return {"Authorization": f"Bearer {guest_token}"}


@pytest.fixture()
def expired_token() -> str:
    """Create an expired JWT token for testing auth failures."""
    from datetime import timedelta

    return create_access_token(
        {"guest_id": "expired-guest"},
        expires_delta=timedelta(seconds=-1),
    )
