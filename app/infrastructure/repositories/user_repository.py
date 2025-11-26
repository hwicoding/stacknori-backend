from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.repositories import RepositoryProtocol


class UserRepository(RepositoryProtocol[User]):
    """Example repository to demonstrate dependency injection contract."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, obj: User) -> User:
        # TODO: implement persistence once models are defined.
        return obj

    async def get(self, **kwargs) -> User | None:
        # TODO: implement query logic.
        return None

