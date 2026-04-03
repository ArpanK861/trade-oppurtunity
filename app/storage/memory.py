"""
In-memory storage for sessions, usage tracking, and analysis caching.
No external database required — all data lives in Python dictionaries.
"""
import time
from datetime import datetime, timezone

from loguru import logger

from app.config import settings


# ── Session Store ──────────────────────────────────────────────
# guest_id → { created_at, request_count, last_request, sectors_queried }
_sessions: dict[str, dict] = {}

# ── Analysis Cache ─────────────────────────────────────────────
# sector → { report, generated_at, sources_count, model_used, cached_at }
_analysis_cache: dict[str, dict] = {}


# ── Session Management ─────────────────────────────────────────


def register_session(guest_id: str) -> None:
    """Register a new guest session."""
    _sessions[guest_id] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request_count": 0,
        "last_request": None,
        "sectors_queried": [],
    }
    logger.info(f"New guest session registered: {guest_id[:8]}...")


def track_request(guest_id: str, sector: str) -> None:
    """Record an analysis request for a guest session."""
    if guest_id not in _sessions:
        register_session(guest_id)

    session = _sessions[guest_id]
    session["request_count"] += 1
    session["last_request"] = datetime.now(timezone.utc).isoformat()
    if sector not in session["sectors_queried"]:
        session["sectors_queried"].append(sector)

    logger.debug(
        f"Request tracked for {guest_id[:8]}...: "
        f"sector={sector}, total={session['request_count']}"
    )


def get_session(guest_id: str) -> dict | None:
    """Retrieve session data for a guest."""
    return _sessions.get(guest_id)


def get_all_sessions_count() -> int:
    """Return total number of active sessions."""
    return len(_sessions)


# ── Analysis Cache ─────────────────────────────────────────────


def get_cached_analysis(sector: str) -> dict | None:
    """
    Return cached analysis for a sector if still fresh.
    Returns None if cache is stale or missing.
    """
    cached = _analysis_cache.get(sector)
    if cached is None:
        return None

    age = time.time() - cached["cached_at"]
    if age > settings.CACHE_TTL_SECONDS:
        logger.info(f"Cache expired for sector '{sector}' (age={age:.0f}s)")
        del _analysis_cache[sector]
        return None

    logger.info(f"Cache hit for sector '{sector}' (age={age:.0f}s)")
    return cached


def set_cached_analysis(
    sector: str,
    report: str,
    sources_count: int,
    model_used: str,
) -> None:
    """Cache an analysis result."""
    _analysis_cache[sector] = {
        "report": report,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources_count": sources_count,
        "model_used": model_used,
        "cached_at": time.time(),
    }
    logger.info(f"Cached analysis for sector '{sector}'")


def clear_cache() -> None:
    """Clear the entire analysis cache."""
    _analysis_cache.clear()
    logger.info("Analysis cache cleared")
