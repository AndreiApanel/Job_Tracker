import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services import auth as auth_service

pytestmark = pytest.mark.asyncio

GOOD_PASSWORD = "correct-horse-battery"


@pytest_asyncio.fixture
async def registered_user(db: AsyncSession) -> User:
    return await auth_service.register(
        db, RegisterRequest(email="ann@example.com", password=GOOD_PASSWORD)
    )


async def test_register_stores_hash_not_password(db: AsyncSession) -> None:
    user = await auth_service.register(
        db, RegisterRequest(email="ann@example.com", password=GOOD_PASSWORD)
    )

    assert user.id is not None  # also checks the expire-on-commit point
    assert user.hashed_password != GOOD_PASSWORD
    assert verify_password(GOOD_PASSWORD, user.hashed_password)


async def test_register_rejects_duplicate_email_ignoring_case(db: AsyncSession) -> None:
    await auth_service.register(
        db, RegisterRequest(email="ANN@example.com", password=GOOD_PASSWORD)
    )

    with pytest.raises(auth_service.EmailAlreadyRegisteredError):
        await auth_service.register(
            db, RegisterRequest(email="ann@example.com", password=GOOD_PASSWORD)
        )


async def test_login_success(db: AsyncSession, registered_user: User) -> None:
    token = await auth_service.login(db, "ann@example.com", GOOD_PASSWORD)
    assert decode_access_token(token) == str(registered_user.id)


async def test_wrong_password(db: AsyncSession, registered_user: User) -> None:
    with pytest.raises(auth_service.InvalidCredentialsError):
        await auth_service.login(db, "ann@example.com", "not-the-password")


async def test_unknown_email(db: AsyncSession) -> None:
    with pytest.raises(auth_service.InvalidCredentialsError):
        await auth_service.login(db, "anna@example.com", GOOD_PASSWORD)
