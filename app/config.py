"""
Application configuration using Pydantic Settings.
Reads from environment variables and .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Central configuration for the Trade Opportunities API."""

    # ── API Keys ───────────────────────────────────────────────
    GROQ_API_KEY: str = Field(
        default="",
        description="Groq API key",
    )

    # ── JWT Authentication ─────────────────────────────────────
    JWT_SECRET_KEY: str = Field(
        default="trade-api-secret-key-change-in-production",
        description="Secret key for JWT token signing",
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Token expiry in minutes",
    )

    # ── Rate Limiting ──────────────────────────────────────────
    RATE_LIMIT: str = Field(
        default="5/minute",
        description="Rate limit for the analyze endpoint",
    )
    GUEST_TOKEN_RATE_LIMIT: str = Field(
        default="10/minute",
        description="Rate limit for guest token creation",
    )

    # ── Server ─────────────────────────────────────────────────
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=True)

    # ── Allowed Sectors ────────────────────────────────────────
    ALLOWED_SECTORS: list[str] = Field(
        default=[
            "pharmaceuticals",
            "technology",
            "agriculture",
            "textiles",
            "automotive",
            "chemicals",
            "steel",
            "electronics",
            "gems-and-jewellery",
            "petroleum",
            "renewable-energy",
            "fintech",
            "food-processing",
            "defence",
            "healthcare",
            "real-estate",
            "banking",
            "infrastructure",
            "telecom",
            "e-commerce",
        ],
        description="Valid sector names for analysis",
    )

    # ── Groq Model ───────────────────────────────────────────
    GROQ_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use for analysis",
    )

    # ── Cache ──────────────────────────────────────────────────
    CACHE_TTL_SECONDS: int = Field(
        default=900,  # 15 minutes
        description="Cache time-to-live for analysis results",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

settings = Settings()