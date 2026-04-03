"""
Tests for API endpoints.
Covers: health check, guest auth, sector analysis (200, 401, 422, 429).
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


# ── Health Check ───────────────────────────────────────────────


class TestHealthCheck:
    """Tests for GET /health."""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint returns 200 with status info."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "groq_configured" in data


# ── Guest Authentication ──────────────────────────────────────


class TestGuestAuth:
    """Tests for POST /auth/guest."""

    def test_create_guest_token(self, client: TestClient):
        """Guest token creation returns 201 with valid JWT."""
        response = client.post("/auth/guest")
        assert response.status_code == 201

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        assert len(data["access_token"]) > 20  # JWT should be substantial

    def test_guest_token_is_unique(self, client: TestClient):
        """Each call generates a unique token."""
        r1 = client.post("/auth/guest")
        r2 = client.post("/auth/guest")
        assert r1.json()["access_token"] != r2.json()["access_token"]


# ── Sector Analysis ───────────────────────────────────────────


class TestSectorAnalysis:
    """Tests for GET /analyze/{sector}."""

    def test_analyze_without_auth_returns_401(self, client: TestClient):
        """Accessing /analyze without a token returns 401."""
        response = client.get("/analyze/pharmaceuticals")
        assert response.status_code == 401

    def test_analyze_with_expired_token_returns_401(
        self, client: TestClient, expired_token: str
    ):
        """Using an expired token returns 401."""
        response = client.get(
            "/analyze/pharmaceuticals",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_analyze_invalid_sector_returns_422(
        self, client: TestClient, auth_headers: dict
    ):
        """Invalid sector name returns 422 with allowed sectors list."""
        response = client.get(
            "/analyze/invalid-sector-xyz",
            headers=auth_headers,
        )
        assert response.status_code == 422

    @patch("app.api.endpoints.analyze_sector", new_callable=AsyncMock)
    @patch("app.api.endpoints.search_sector_data", new_callable=AsyncMock)
    def test_analyze_valid_sector_returns_200(
        self,
        mock_search,
        mock_analyze,
        client: TestClient,
        auth_headers: dict,
    ):
        """Valid request returns 200 with structured Markdown report."""
        # Mock search results
        mock_search.return_value = []

        # Mock Groq response
        mock_analyze.return_value = (
            "# Trade Opportunity Report: Pharmaceuticals — India\n\n"
            "## Executive Summary\n\n"
            "The pharmaceutical sector in India is booming..."
        )

        response = client.get(
            "/analyze/pharmaceuticals",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["sector"] == "pharmaceuticals"
        assert "# Trade Opportunity Report" in data["report"]
        assert "generated_at" in data
        assert data["model_used"] is not None

    @patch("app.api.endpoints.analyze_sector", new_callable=AsyncMock)
    @patch("app.api.endpoints.search_sector_data", new_callable=AsyncMock)
    def test_analyze_response_is_markdown(
        self,
        mock_search,
        mock_analyze,
        client: TestClient,
        auth_headers: dict,
    ):
        """Response report field contains valid Markdown content."""
        mock_search.return_value = []
        mock_analyze.return_value = (
            "# Report\n\n## Section 1\n\nContent here.\n\n"
            "## Section 2\n\n| Col1 | Col2 |\n|------|------|\n| A | B |"
        )

        response = client.get(
            "/analyze/technology",
            headers=auth_headers,
        )
        data = response.json()
        report = data["report"]

        # Verify Markdown structure
        assert report.startswith("#")
        assert "##" in report
        assert len(report) > 50

    @patch("app.api.endpoints.analyze_sector", new_callable=AsyncMock)
    @patch("app.api.endpoints.search_sector_data", new_callable=AsyncMock)
    def test_analyze_groq_failure_returns_500(
        self,
        mock_search,
        mock_analyze,
        client: TestClient,
        auth_headers: dict,
    ):
        """Groq API failure returns 500 with error message."""
        mock_search.return_value = []
        mock_analyze.side_effect = RuntimeError("Groq API key invalid")

        response = client.get(
            "/analyze/agriculture",
            headers=auth_headers,
        )
        assert response.status_code == 500


# ── Rate Limiting ──────────────────────────────────────────────


class TestRateLimiting:
    """Tests for rate limiting behavior."""

    @patch("app.api.endpoints.analyze_sector", new_callable=AsyncMock)
    @patch("app.api.endpoints.search_sector_data", new_callable=AsyncMock)
    def test_rate_limit_exceeded_returns_429(
        self,
        mock_search,
        mock_analyze,
        client: TestClient,
        auth_headers: dict,
    ):
        """Exceeding 5 requests/minute returns 429."""
        mock_search.return_value = []
        mock_analyze.return_value = "# Mocked Report"

        # Make 6 requests quickly — the 6th should be rate-limited
        responses = []
        for _ in range(7):
            r = client.get(
                "/analyze/pharmaceuticals",
                headers=auth_headers,
            )
            responses.append(r.status_code)

        # At least one response should be 429
        assert 429 in responses, (
            f"Expected at least one 429 response, got: {responses}"
        )
