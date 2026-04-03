"""
JWT-based guest authentication.
No credentials required — generates anonymous guest tokens.
"""
import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from loguru import logger
from app.config import settings

def create_guest_id() -> str:
    """Generate a unique guest identifier."""
    return str(uuid.uuid4())

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT token.
    Args:
        data: Claims to encode in the token.
        expires_delta: Custom expiry. Defaults to JWT_EXPIRE_MINUTES.
    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    logger.debug(f"Token created for guest_id={data.get('guest_id', 'unknown')[:8]}...")
    return encoded_jwt

def verify_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.
    Args:
        token: The raw JWT string (without 'Bearer ' prefix).
    Returns:
        Decoded payload dict, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        guest_id: str | None = payload.get("guest_id")
        if guest_id is None:
            logger.warning("Token missing guest_id claim")
            return None
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None

def generate_guest_token() -> tuple[str, str, int]:
    """
    Generate a complete guest token package.
    Returns:
        Tuple of (access_token, guest_id, expires_in_seconds).
    """
    guest_id = create_guest_id()
    expires_in = settings.JWT_EXPIRE_MINUTES * 60
    access_token = create_access_token({"guest_id": guest_id})
    return access_token, guest_id, expires_in