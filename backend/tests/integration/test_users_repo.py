import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import users as users_repo

pytestmark = pytest.mark.asyncio


async def test_get_by_email_finds_user_ignoring_case(db: AsyncSession) -> None:
    created = users_repo.add(db, email="Ann@Example.com", hashed_password="x")
    await db.flush()
    found = await users_repo.get_by_email(db, "ANN@example.COM")

    assert found is not None
    assert found.id == created.id


async def test_get_by_email_does_not_return_other_users(db: AsyncSession) -> None:
    users_repo.add(db, email="ann@example.com", hashed_password="x")
    await db.flush()

    assert await users_repo.get_by_email(db, "bob@example.com") is None


async def test_get_by_email_returns_none_for_unknown_email(db: AsyncSession) -> None:
    assert await users_repo.get_by_email(db, "nobody@example.com") is None
