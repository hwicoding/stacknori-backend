from fastapi import Depends, HTTPException, status
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


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to require admin (superuser) access."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
