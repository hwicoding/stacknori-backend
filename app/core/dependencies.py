from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.database import get_db
from app.domain.entities import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.usecases.auth import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_user_repository(session=Depends(get_db)) -> UserRepository:
    return UserRepository(session)


async def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.get_current_user(token)

