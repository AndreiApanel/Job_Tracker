from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import users as users_repo
from app.schemas.auth import RegisterRequest


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


_DUMMY_HASH = hash_password("not-a-real-password")


async def register(db: AsyncSession, data: RegisterRequest) -> User:
    if await users_repo.get_by_email(db, data.email) is not None:
        raise EmailAlreadyRegisteredError

    user = users_repo.add(
        db, email=data.email, hashed_password=hash_password(data.password)
    )
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise EmailAlreadyRegisteredError from None
    await db.refresh(user)
    return user


async def login(db: AsyncSession, email: str, password: str) -> str:
    user = await users_repo.get_by_email(db, email)
    if user is None:
        verify_password(password, _DUMMY_HASH)
        raise InvalidCredentialsError
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError
    return create_access_token(str(user.id))
