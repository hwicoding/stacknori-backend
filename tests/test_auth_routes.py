import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(test_client: AsyncClient):
    """회원가입 API 성공 테스트"""
    response = await test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data  # 비밀번호는 응답에 포함되지 않음
    assert data["is_active"] is True
    assert data["is_superuser"] is False


@pytest.mark.asyncio
async def test_signup_duplicate_email(test_client: AsyncClient):
    """중복 이메일 회원가입 실패 테스트"""
    # 첫 번째 등록
    await test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    
    # 동일 이메일로 재등록 시도
    response = await test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_invalid_email(test_client: AsyncClient):
    """잘못된 이메일 형식 회원가입 실패 테스트"""
    response = await test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "invalid-email",
            "password": "password123",
        },
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_signup_short_password(test_client: AsyncClient):
    """짧은 비밀번호 회원가입 실패 테스트"""
    response = await test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "user@example.com",
            "password": "short",  # 8자 미만
        },
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, sample_user):
    """로그인 API 성공 테스트"""
    response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client: AsyncClient):
    """잘못된 자격증명으로 로그인 실패 테스트"""
    response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_tokens_success(test_client: AsyncClient, sample_user):
    """리프레시 토큰으로 새 토큰 쌍 발급 성공 테스트"""
    # 먼저 로그인하여 토큰 획득
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # 리프레시 토큰으로 새 토큰 쌍 발급
    response = await test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != login_response.json()["access_token"]
    assert data["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_refresh_tokens_invalid_token(test_client: AsyncClient):
    """잘못된 리프레시 토큰으로 실패 테스트"""
    response = await test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_success(test_client: AsyncClient, sample_user):
    """현재 사용자 조회 API 성공 테스트"""
    # 먼저 로그인하여 토큰 획득
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]
    
    # 현재 사용자 조회
    response = await test_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["id"] == sample_user.id
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_current_user_no_token(test_client: AsyncClient):
    """토큰 없이 현재 사용자 조회 실패 테스트"""
    response = await test_client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_client: AsyncClient):
    """잘못된 토큰으로 현재 사용자 조회 실패 테스트"""
    response = await test_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    
    assert response.status_code == 401

