"""Security and authentication utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel


class TokenData(BaseModel):
    """Token payload data model."""

    sub: str
    exp: datetime
    iat: datetime
    type: str


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None, secret_key: str = "your-secret-key"
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing token claims
        expires_delta: Optional expiration time delta
        secret_key: Secret key for signing the token

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")

    return encoded_jwt


def verify_token(token: str, secret_key: str = "your-secret-key") -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string
        secret_key: Secret key for verifying the token

    Returns:
        Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload: dict[str, Any] = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e

