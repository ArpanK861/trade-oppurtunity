"""
Pydantic models for request validation and response serialization.
"""
from datetime import datetime
from pydantic import BaseModel, Field

# ── Authentication ─────────────────────────────────────────────
class GuestTokenResponse(BaseModel):
    """Response returned when a guest JWT token is created."""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(description="Token lifetime in seconds")

class TokenPayload(BaseModel):
    """Internal model representing decoded JWT claims."""
    guest_id: str
    exp: datetime | None = None

# ── Analysis ───────────────────────────────────────────────────
class AnalysisResponse(BaseModel):
    """Structured response wrapping the Markdown analysis report."""
    sector: str = Field(description="Analyzed sector name")
    report: str = Field(description="Full Markdown analysis report")
    generated_at: datetime = Field(description="Timestamp of report generation")
    sources_count: int = Field(description="Number of sources used")
    model_used: str = Field(description="AI model used for analysis")
    cached: bool = Field(
        default=False,
        description="Whether the result was served from cache",
    )

class SearchResult(BaseModel):
    """Single search result from data collection."""
    title: str
    snippet: str
    url: str
    source: str = ""

# ── Errors ─────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str = Field(description="Human-readable error message")
    error_code: str = Field(description="Machine-readable error code")

# ── Health ─────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime
    groq_configured: bool