"""
FastAPI dependencies for authentication and request validation.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import verify_token
# HTTP Bearer scheme for Swagger UI integration
_bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """
    Dependency that extracts and validates the JWT token.
    Raises 401 if:
    - No Authorization header is present
    - Token is invalid or expired
    - Token is missing required claims
    Returns:
        Decoded JWT payload dict containing at least 'guest_id'.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Get a token via POST /auth/guest",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please request a new one via POST /auth/guest",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload