"""
API endpoints for the Trade Opportunities service.
Routes:
  POST /auth/guest          → Generate guest JWT token
  GET  /analyze/{sector}    → Analyze sector and return Markdown report
  GET  /health              → Health check
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from app.api.dependencies import get_current_user
from app.config import settings
from app.core.rate_limiter import limiter
from app.core.security import generate_guest_token
from app.models.schemas import (
    AnalysisResponse,
    ErrorResponse,
    GuestTokenResponse,
    HealthResponse,
)
from app.services.analyzer import analyze_sector
from app.services.search import search_sector_data
from app.storage.memory import (
    get_cached_analysis,
    register_session,
    set_cached_analysis,
    track_request,
)

router = APIRouter()

# ── Authentication ─────────────────────────────────────────────
@router.post(
    "/auth/guest",
    response_model=GuestTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Guest Token",
    description="Create an anonymous JWT token for API access. No credentials required.",
    tags=["Authentication"],
    responses={
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
@limiter.limit(settings.GUEST_TOKEN_RATE_LIMIT)
async def create_guest_token(request: Request) -> GuestTokenResponse:
    """Generate a guest JWT token for anonymous API access."""
    access_token, guest_id, expires_in = generate_guest_token()
    # Register the session in memory
    register_session(guest_id)
    logger.info(f"Guest token created: {guest_id[:8]}...")
    return GuestTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )

# ── Sector Analysis ───────────────────────────────────────────
@router.get(
    "/analyze/{sector}",
    response_model=AnalysisResponse,
    summary="Analyze Trade Sector",
    description=(
        "Analyze an Indian market sector and return a comprehensive "
        "Markdown trade opportunity report. Requires a valid guest JWT token."
    ),
    tags=["Analysis"],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        422: {"model": ErrorResponse, "description": "Invalid sector name"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Analysis failed"},
    },
)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_trade_sector(
    request: Request,
    sector: str,
    current_user: dict = Depends(get_current_user),
) -> AnalysisResponse:
    """
    Analyze a specific Indian market sector for trade opportunities.
    **Flow:**
    1. Validate sector name against allowed list
    2. Check cache for recent analysis
    3. Collect real-time market data via DuckDuckGo
    4. Send data to Groq for AI analysis
    5. Return structured Markdown report
    **Allowed sectors:** pharmaceuticals, technology, agriculture, textiles,
    automotive, chemicals, steel, electronics, gems-and-jewellery, petroleum,
    renewable-energy, fintech, food-processing, defence, healthcare,
    real-estate, banking, infrastructure, telecom, e-commerce
    """
    # ── 1. Validate sector ─────────────────────────────────
    sector_clean = sector.lower().strip().replace(" & ", " and ").replace(" ", "-")

    if sector_clean not in settings.ALLOWED_SECTORS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid sector '{sector}'. "
                f"Allowed sectors: {', '.join(settings.ALLOWED_SECTORS)}"
            ),
        )
    guest_id = current_user.get("guest_id", "unknown")
    logger.info(f"Analysis requested: sector='{sector_clean}', user={guest_id[:8]}...")

    # ── 2. Check cache ─────────────────────────────────────
    cached = get_cached_analysis(sector_clean)
    if cached:
        track_request(guest_id, sector_clean)
        return AnalysisResponse(
            sector=sector_clean,
            report=cached["report"],
            generated_at=datetime.fromisoformat(cached["generated_at"]),
            sources_count=cached["sources_count"],
            model_used=cached["model_used"],
            cached=True,
        )

    # ── 3. Collect market data ─────────────────────────────
    try:
        search_results = await search_sector_data(sector_clean)
    except Exception as e:
        logger.error(f"Data collection failed for '{sector_clean}': {e}")
        search_results = []

    # ── 4. AI Analysis ─────────────────────────────────────
    try:
        report = await analyze_sector(sector_clean, search_results)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected analysis error for '{sector_clean}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis. Please try again.",
        )

    # ── 5. Cache and respond ───────────────────────────────
    set_cached_analysis(
        sector=sector_clean,
        report=report,
        sources_count=len(search_results),
        model_used=settings.GROQ_MODEL,
    )

    track_request(guest_id, sector_clean)

    return AnalysisResponse(
        sector=sector_clean,
        report=report,
        generated_at=datetime.now(timezone.utc),
        sources_count=len(search_results),
        model_used=settings.GROQ_MODEL,
        cached=False,
    )

# ── Health Check ───────────────────────────────────────────────
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and Groq is configured.",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """Return the health status of the API."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
        groq_configured=bool(settings.GROQ_API_KEY),
    )