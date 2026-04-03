"""
Data collection service using DuckDuckGo search.
Gathers real-time market news and trade data for Indian sectors.
"""
import asyncio
from typing import Any
from duckduckgo_search import DDGS
from loguru import logger
from app.models.schemas import SearchResult

# ── Search Queries ─────────────────────────────────────────────
def _build_search_queries(sector: str) -> list[str]:
    """
    Build a set of targeted search queries for an Indian sector.
    Multiple queries ensure broad coverage of trade information.
    """
    clean_sector = sector.replace("-", " ").title()
    return [
        f"India {clean_sector} trade opportunities 2026",
        f"India {clean_sector} market analysis export import",
        f"India {clean_sector} industry news latest",
        f"India {clean_sector} sector growth investment trends",
        f"{clean_sector} India government policy regulation",
    ]

# ── Search Execution ──────────────────────────────────────────
def _execute_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Execute a single DuckDuckGo search query synchronously.
    Returns a list of result dicts with title, snippet, and URL.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return results
    except Exception as e:
        logger.warning(f"Search failed for query '{query[:50]}...': {e}")
        return []

# ── Main Collection Function ──────────────────────────────────
async def search_sector_data(sector: str) -> list[SearchResult]:
    """
    Collect market data for a sector from DuckDuckGo search.
    Runs multiple queries concurrently through asyncio.to_thread
    (since duckduckgo_search is synchronous), deduplicates results,
    and returns structured SearchResult objects.
    Args:
        sector: The sector name to search for (e.g., "pharmaceuticals").
    Returns:
        List of SearchResult objects with title, snippet, URL, and source.
    """
    queries = _build_search_queries(sector)
    logger.info(f"Searching for sector '{sector}' with {len(queries)} queries")
    # Run all queries concurrently using thread pool
    tasks = [
        asyncio.to_thread(_execute_search, query)
        for query in queries
    ]
    all_results = await asyncio.gather(*tasks, return_exceptions=True)
    # Flatten and deduplicate by URL
    seen_urls: set[str] = set()
    unique_results: list[SearchResult] = []
    for i, result_batch in enumerate(all_results):
        if isinstance(result_batch, Exception):
            logger.warning(f"Query {i + 1} raised an exception: {result_batch}")
            continue
        for item in result_batch:
            url = item.get("href", item.get("link", ""))
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(
                    SearchResult(
                        title=item.get("title", "Untitled"),
                        snippet=item.get("body", item.get("snippet", "")),
                        url=url,
                        source=_extract_domain(url),
                    )
                )
    logger.info(
        f"Collected {len(unique_results)} unique results for sector '{sector}'"
    )
    return unique_results

# ── Helpers ────────────────────────────────────────────────────
def _extract_domain(url: str) -> str:
    """Extract the domain name from a URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain
    except Exception:
        return ""

def format_search_results_for_prompt(results: list[SearchResult]) -> str:
    """
    Format search results into a clean text block for the AI prompt.
    """
    if not results:
        return "No recent market data available."
    lines: list[str] = []
    for i, result in enumerate(results, 1):
        lines.append(f"[{i}] {result.title}")
        lines.append(f"    Source: {result.source}")
        lines.append(f"    Summary: {result.snippet}")
        lines.append(f"    URL: {result.url}")
        lines.append("")
    return "\n".join(lines)