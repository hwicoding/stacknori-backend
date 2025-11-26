from typing import Tuple

from fastapi import HTTPException, status

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    validate_token,
    verify_password,
)
from app.domain.entities import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.schemas import RefreshTokenRequest, TokenPair, UserCreate


class AuthService:
    """Application service orchestrating authentication logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register_user(self, payload: UserCreate) -> User:
        existing = await self.repository.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed_password = get_password_hash(payload.password)
        user = User(
            email=payload.email,
            hashed_password=hashed_password,
        )
        return await self.repository.add(user)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def create_token_pair(self, user: User) -> TokenPair:
        access_token, refresh_token = self._generate_tokens(user.id)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, payload: RefreshTokenRequest) -> TokenPair:
        try:
            token_payload = validate_token(payload.refresh_token, expected_type="refresh")
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

        user_id = token_payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
            )
        user = await self.repository.get(id=int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        token_pair = self._generate_tokens(user.id)
        return TokenPair(access_token=token_pair[0], refresh_token=token_pair[1])

    async def get_current_user(self, token: str) -> User:
        try:
            payload = validate_token(token, expected_type="access")
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        user = await self.repository.get(id=int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def _generate_tokens(self, user_id: int) -> Tuple[str, str]:
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))
        return access_token, refresh_token

