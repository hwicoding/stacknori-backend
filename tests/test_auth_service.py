import pytest
from fastapi import HTTPException, status

from app.domain.entities import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.schemas import RefreshTokenRequest, UserCreate
from app.usecases.auth import AuthService


@pytest.mark.asyncio
async def test_register_user_success(test_db_session):
    """사용자 등록 성공 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    payload = UserCreate(email="newuser@example.com", password="password123")
    user = await service.register_user(payload)
    
    assert user.email == "newuser@example.com"
    assert user.hashed_password != "password123"  # 해시된 비밀번호
    assert user.is_active is True
    assert user.is_superuser is False


@pytest.mark.asyncio
async def test_register_user_duplicate_email(test_db_session):
    """중복 이메일 등록 실패 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    payload = UserCreate(email="duplicate@example.com", password="password123")
    await service.register_user(payload)
    
    # 동일 이메일로 재등록 시도
    with pytest.raises(HTTPException) as exc_info:
        await service.register_user(payload)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_authenticate_success(test_db_session, sample_user):
    """인증 성공 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    user = await service.authenticate("test@example.com", "testpassword123")
    
    assert user.email == "test@example.com"
    assert user.id == sample_user.id


@pytest.mark.asyncio
async def test_authenticate_invalid_email(test_db_session):
    """존재하지 않는 이메일 인증 실패 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.authenticate("nonexistent@example.com", "password123")
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid credentials" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_authenticate_invalid_password(test_db_session, sample_user):
    """잘못된 비밀번호 인증 실패 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.authenticate("test@example.com", "wrongpassword")
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid credentials" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_create_token_pair(test_db_session, sample_user):
    """토큰 쌍 생성 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    from app.domain.entities import User
    user_entity = User.model_validate(sample_user)
    
    token_pair = await service.create_token_pair(user_entity)
    
    assert token_pair.access_token is not None
    assert token_pair.refresh_token is not None
    assert token_pair.token_type == "bearer"
    assert len(token_pair.access_token) > 0
    assert len(token_pair.refresh_token) > 0


@pytest.mark.asyncio
async def test_refresh_tokens_success(test_db_session, sample_user):
    """리프레시 토큰으로 새 토큰 쌍 발급 성공 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    from app.domain.entities import User
    user_entity = User.model_validate(sample_user)
    
    # 초기 토큰 쌍 생성
    initial_pair = await service.create_token_pair(user_entity)
    
    # 리프레시 토큰으로 새 토큰 쌍 발급
    refresh_payload = RefreshTokenRequest(refresh_token=initial_pair.refresh_token)
    new_pair = await service.refresh_tokens(refresh_payload)
    
    assert new_pair.access_token != initial_pair.access_token
    assert new_pair.refresh_token != initial_pair.refresh_token
    assert new_pair.token_type == "bearer"


@pytest.mark.asyncio
async def test_refresh_tokens_invalid_token(test_db_session):
    """잘못된 리프레시 토큰으로 실패 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    refresh_payload = RefreshTokenRequest(refresh_token="invalid.token.here")
    
    with pytest.raises(HTTPException) as exc_info:
        await service.refresh_tokens(refresh_payload)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_success(test_db_session, sample_user):
    """현재 사용자 조회 성공 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    from app.domain.entities import User
    user_entity = User.model_validate(sample_user)
    
    token_pair = await service.create_token_pair(user_entity)
    current_user = await service.get_current_user(token_pair.access_token)
    
    assert current_user.id == sample_user.id
    assert current_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_db_session):
    """잘못된 액세스 토큰으로 현재 사용자 조회 실패 테스트"""
    repository = UserRepository(test_db_session)
    service = AuthService(repository)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_current_user("invalid.token.here")
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

