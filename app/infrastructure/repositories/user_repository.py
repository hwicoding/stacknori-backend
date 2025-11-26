from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.repositories import RepositoryProtocol
from app.infrastructure.db.models import UserModel


class UserRepository(RepositoryProtocol[User]):
    """Repository implementing CRUD operations for the User aggregate."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, obj: User) -> User:
        model = UserModel(
            email=obj.email,
            hashed_password=obj.hashed_password,
            is_active=obj.is_active,
            is_superuser=obj.is_superuser,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return User.model_validate(model)

    async def get(self, **kwargs: Any) -> User | None:
        stmt = select(UserModel)
        for key, value in kwargs.items():
            column = getattr(UserModel, key, None)
            if column is not None:
                stmt = stmt.where(column == value)

        result = await self.session.execute(stmt.limit(1))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return User.model_validate(model)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get(email=email)

