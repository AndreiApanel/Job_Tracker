import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, RegisterRequest, UserRead

GOOD_PASSWORD = "correct-horse-battery"


def test_register_accepts_valid_input() -> None:
    req = RegisterRequest(email="a@example.com", password=GOOD_PASSWORD)
    assert req.email == "a@example.com"


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("not-an-email", GOOD_PASSWORD),
        ("a@example.com", "short"),
        ("a@example.com", "x" * 129),
    ],
)
def test_register_rejects_invalid_input(email: str, password: str) -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(email=email, password=password)


def test_login_rejects_huge_password() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="a@example.com", password="x" * 129)


def test_user_read_has_no_password_field() -> None:
    assert "hashed_password" not in UserRead.model_fields


def test_user_read_from_orm_object() -> None:
    fake_user = SimpleNamespace(
        id=uuid.uuid4(),
        email="a@example.com",
        created_at=datetime.now(UTC),
        hashed_password="secret-hash",
    )
    data = UserRead.model_validate(fake_user).model_dump()
    assert "hashed_password" not in data
