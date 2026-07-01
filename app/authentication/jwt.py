from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.config import get_settings

settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token.
        expires_delta: Custom expiration time. If None, the default
                       ACCESS_TOKEN_EXPIRE_MINUTES is used.

    Returns:
        Encoded JWT access token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in the token.

    Returns:
        Encoded JWT refresh token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    Decode a JWT token.

    Args:
        token: JWT token to decode.

    Returns:
        Decoded payload if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload

    except JWTError:
        return None
