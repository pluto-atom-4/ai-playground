"""Unit tests for security module."""

import pytest
from fastapi import HTTPException

from src.core.security import create_access_token, verify_token


@pytest.mark.unit
def test_create_access_token() -> None:
    """Test JWT token creation."""
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.unit
def test_verify_token() -> None:
    """Test JWT token verification."""
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["sub"] == "user@example.com"


@pytest.mark.unit
def test_verify_invalid_token() -> None:
    """Test verification of invalid token."""
    with pytest.raises(HTTPException):
        verify_token("invalid.token.here")

