"""
Trade Opportunities API — FastAPI Application Entry Point.
A FastAPI service that analyzes Indian market sectors using Groq AI
and real-time web data to generate structured trade opportunity reports.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.endpoints import router
from app.core.rate_limiter import limiter

# ── Lifespan Events ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("🚀 Trade Opportunities API starting up...")
    logger.info("📊 Endpoints: POST /auth/guest, GET /analyze/{{sector}}, GET /health")
    logger.info("📖 Documentation: http://localhost:8000/docs")
    yield
    logger.info("🛑 Trade Opportunities API shutting down...")

# ── FastAPI App ────────────────────────────────────────────────
app = FastAPI(
    title="Trade Opportunities API — India",
    description=(
        "Analyze Indian market sectors and discover trade opportunities "
        "using AI-powered analysis. Provides structured Markdown reports "
        "covering market sentiment, key players, opportunities, and risks.\n\n"
        "**How to use:**\n"
        "1. Call `POST /auth/guest` to get a JWT token\n"
        "2. Use the token in `Authorization: Bearer <token>` header\n"
        "3. Call `GET /analyze/{sector}` with a valid sector name\n"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Rate Limiter ───────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

import os

# ── CORS Middleware ────────────────────────────────────────────
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Include Routers ────────────────────────────────────────────
app.include_router(router)

# ── Custom Exception Handlers ─────────────────────────────────
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Custom handler for validation errors — cleaner messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error. Please check your input.",
            "error_code": "VALIDATION_ERROR",
        },
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom handler for unexpected server errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "error_code": "INTERNAL_ERROR",
        },
    )