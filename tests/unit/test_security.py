import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import timedelta

from src.backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


def test_password_hashing():
    password = "test_password_123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_access_token():
    data = {"sub": "testuser", "role": "admin"}
    token = create_access_token(data, expires_delta=timedelta(hours=1))
    assert token is not None

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "admin"


def test_expired_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))

    decoded = decode_access_token(token)
    assert decoded is None


def test_invalid_token():
    decoded = decode_access_token("invalid_token")
    assert decoded is None
