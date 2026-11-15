import uuid

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models.company import Company
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_email_is_unique_ignoring_case(db):
    db.add(User(email="Ann@x.com", hashed_password="x"))
    await db.flush()

    db.add(User(email="ann@x.com", hashed_password="x"))
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_company_name_is_unique_per_user_ignoring_case(db):
    user = User(email="ann@x.com", hashed_password="x")
    db.add(user)
    await db.flush()

    db.add(Company(user_id=user.id, name="Acme"))
    await db.flush()

    db.add(Company(user_id=user.id, name="acme"))

    with pytest.raises(IntegrityError):
        await db.flush()


async def test_two_users_can_have_the_same_company_name(db):
    user_a = User(email="ann@x.com", hashed_password="x")
    user_b = User(email="bob@x.com", hashed_password="x")
    db.add_all([user_a, user_b])
    await db.flush()
    db.add(Company(user_id=user_a.id, name="Acme"))
    db.add(Company(user_id=user_b.id, name="Acme"))
    await db.flush()
    count = await db.scalar(
        select(func.count()).select_from(Company).where(Company.name == "Acme")
    )
    assert count == 2


async def test_deleting_user_deletes_their_companies(db):
    user = User(email="ann@x.com", hashed_password="x")
    db.add(user)
    await db.flush()

    company = Company(user_id=user.id, name="Acme")
    db.add(company)
    await db.flush()
    company_id = company.id

    await db.delete(user)
    await db.flush()

    found = await db.scalar(select(Company).where(Company.id == company_id))
    assert found is None


async def test_company_requires_existing_user(db):
    db.add(Company(user_id=uuid.uuid4(), name="Acme"))
    with pytest.raises(IntegrityError):
        await db.flush()
