from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_auth_service, get_current_user
from app.domain.entities import User
from app.schemas import RefreshTokenRequest, TokenPair, UserCreate, UserRead
from app.usecases.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    user = await auth_service.register_user(payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    user = await auth_service.authenticate(form_data.username, form_data.password)
    return await auth_service.create_token_pair(user)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    return await auth_service.refresh_tokens(payload)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)

