"""
Rate limiting configuration using slowapi.
Limits are per guest_id (from JWT) with IP fallback.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request
from app.config import settings

def _get_rate_limit_key(request: Request) -> str:
    """
    Extract rate-limit key from the request.
    Uses guest_id from JWT if available, falls back to client IP.
    """
    # Try to extract guest_id from already-decoded auth state
    auth_user = getattr(request.state, "guest_id", None)
    if auth_user:
        return f"guest:{auth_user}"

    # Fallback: extract from Authorization header directly
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Import here to avoid circular dependency
        from app.core.security import verify_token
        payload = verify_token(token)
        if payload and "guest_id" in payload:
            return f"guest:{payload['guest_id']}"

    # Final fallback to IP
    return get_remote_address(request)

# Initialize the global limiter
limiter = Limiter(
    key_func=_get_rate_limit_key,
    default_limits=[settings.RATE_LIMIT],
    storage_uri="memory://",
)