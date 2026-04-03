"""
Tests for service layer — search and analyzer.
Uses mocks to avoid actual API calls.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.models.schemas import SearchResult
from app.services.search import (
    _build_search_queries,
    _extract_domain,
    format_search_results_for_prompt,
)


# ── Search Queries ─────────────────────────────────────────────


class TestBuildSearchQueries:
    """Tests for query construction."""

    def test_returns_multiple_queries(self):
        """Multiple search queries should be generated."""
        queries = _build_search_queries("pharmaceuticals")
        assert len(queries) >= 3

    def test_queries_contain_sector(self):
        """All queries should mention the sector."""
        queries = _build_search_queries("technology")
        for q in queries:
            assert "Technology" in q or "technology" in q

    def test_queries_mention_india(self):
        """All queries should target India."""
        queries = _build_search_queries("agriculture")
        for q in queries:
            assert "India" in q

    def test_hyphenated_sector_cleaned(self):
        """Hyphens should be converted to spaces."""
        queries = _build_search_queries("gems-and-jewellery")
        assert any("Gems And Jewellery" in q for q in queries)


# ── Domain Extraction ──────────────────────────────────────────


class TestExtractDomain:
    """Tests for URL domain extraction."""

    def test_extracts_domain(self):
        assert _extract_domain("https://www.example.com/page") == "example.com"

    def test_strips_www(self):
        assert _extract_domain("https://www.reuters.com/article") == "reuters.com"

    def test_handles_invalid_url(self):
        result = _extract_domain("not-a-url")
        assert isinstance(result, str)


# ── Prompt Formatting ──────────────────────────────────────────


class TestFormatSearchResults:
    """Tests for converting search results to prompt text."""

    def test_empty_results(self):
        """Empty list should return a fallback message."""
        result = format_search_results_for_prompt([])
        assert "No recent market data" in result

    def test_formats_results_with_numbers(self):
        """Each result should be numbered."""
        results = [
            SearchResult(
                title="Test Article",
                snippet="Some content here",
                url="https://example.com/article",
                source="example.com",
            ),
        ]
        formatted = format_search_results_for_prompt(results)
        assert "[1]" in formatted
        assert "Test Article" in formatted
        assert "example.com" in formatted

    def test_multiple_results_numbered_sequentially(self):
        """Multiple results should be numbered 1, 2, 3..."""
        results = [
            SearchResult(
                title=f"Article {i}",
                snippet=f"Content {i}",
                url=f"https://example.com/{i}",
                source="example.com",
            )
            for i in range(3)
        ]
        formatted = format_search_results_for_prompt(results)
        assert "[1]" in formatted
        assert "[2]" in formatted
        assert "[3]" in formatted


# ── Analyzer ───────────────────────────────────────────────────


class TestAnalyzer:
    """Tests for the Groq analyzer service (mocked)."""

    @patch("app.services.analyzer.settings")
    def test_analyze_without_api_key_raises(self, mock_settings):
        """Should raise RuntimeError if GROQ_API_KEY is not set."""
        mock_settings.GROQ_API_KEY = ""

        from app.services.analyzer import analyze_sector

        import asyncio

        with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
            asyncio.run(analyze_sector("test", []))

    @patch("app.services.analyzer._run_groq_analysis")
    @patch("app.services.analyzer.settings")
    def test_analyze_returns_groq_output(self, mock_settings, mock_groq):
        """Should return whatever Groq produces."""
        mock_settings.GROQ_API_KEY = "fake-key"
        mock_settings.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_groq.return_value = "# Mock Report\n\nContent here"

        from app.services.analyzer import analyze_sector

        import asyncio

        result = asyncio.run(analyze_sector("pharmaceuticals", []))
        assert "# Mock Report" in result
