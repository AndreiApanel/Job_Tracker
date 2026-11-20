from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_the_password():
    assert hash_password("secret123") != "secret123"


def test_correct_password_verifies_and_wrong_one_does_not():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_same_password_hashes_differently():
    assert hash_password("secret123") != hash_password("secret123")


def test_token_round_trip():
    token = create_access_token("user-1")
    assert decode_access_token(token) == "user-1"


def test_expired_token_is_rejected():
    expired = jwt.encode(
        {"sub": "user-1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        get_settings().SECRET_KEY,
        algorithm="HS256",
    )
    assert decode_access_token(expired) is None


def test_token_signed_with_another_key_is_rejected():
    forged = jwt.encode(
        {"sub": "user-1", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "another-key-that-is-long-enough-123",
        algorithm="HS256",
    )
    assert decode_access_token(forged) is None


def test_token_without_exp_is_rejected():
    no_expiry = jwt.encode(
        {"sub": "user-1"},
        get_settings().SECRET_KEY,
        algorithm="HS256",
    )
    assert decode_access_token(no_expiry) is None
