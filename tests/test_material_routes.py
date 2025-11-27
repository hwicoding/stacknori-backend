import pytest
from httpx import AsyncClient

from app.domain.entities.material import MaterialDifficulty, MaterialType
from app.infrastructure.db.models.material import MaterialModel


@pytest.mark.asyncio
async def test_search_materials_success(test_client: AsyncClient, test_db_session, sample_user):
    """자료 검색 성공 테스트"""
    # 자료 데이터 생성
    material1 = MaterialModel(
        title="FastAPI Tutorial",
        url="https://example.com/fastapi",
        difficulty=MaterialDifficulty.BEGINNER,
        type=MaterialType.DOCUMENT,
        summary="FastAPI introduction",
        keywords=["fastapi", "python", "api"],
    )
    material2 = MaterialModel(
        title="React Video Course",
        url="https://example.com/react",
        difficulty=MaterialDifficulty.INTERMEDIATE,
        type=MaterialType.VIDEO,
        summary="React fundamentals",
        keywords=["react", "frontend"],
    )
    test_db_session.add_all([material1, material2])
    await test_db_session.commit()

    # 로그인
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 자료 검색
    response = await test_client.get("/api/v1/materials", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "materials" in data
    assert "pagination" in data
    assert len(data["materials"]) >= 2
    assert data["pagination"]["total"] >= 2


@pytest.mark.asyncio
async def test_search_materials_with_keyword(test_client: AsyncClient, test_db_session, sample_user):
    """키워드로 자료 검색 테스트"""
    material = MaterialModel(
        title="FastAPI Advanced",
        url="https://example.com/fastapi-adv",
        difficulty=MaterialDifficulty.INTERMEDIATE,
        type=MaterialType.DOCUMENT,
        summary="Advanced FastAPI patterns",
        keywords=["fastapi", "advanced"],
    )
    test_db_session.add(material)
    await test_db_session.commit()

    # 로그인
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 키워드 검색
    response = await test_client.get(
        "/api/v1/materials", params={"keyword": "FastAPI"}, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert any("FastAPI" in m["title"] for m in data["materials"])


@pytest.mark.asyncio
async def test_search_materials_with_filters(test_client: AsyncClient, test_db_session, sample_user):
    """필터로 자료 검색 테스트"""
    material = MaterialModel(
        title="Python Basics",
        url="https://example.com/python",
        difficulty=MaterialDifficulty.BEGINNER,
        type=MaterialType.DOCUMENT,
        summary="Python introduction",
        keywords=["python"],
    )
    test_db_session.add(material)
    await test_db_session.commit()

    # 로그인
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 난이도 필터
    response = await test_client.get(
        "/api/v1/materials",
        params={"difficulty": "beginner", "type": "document"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(m["difficulty"] == "beginner" for m in data["materials"])
    assert all(m["type"] == "document" for m in data["materials"])


@pytest.mark.asyncio
async def test_search_materials_pagination(test_client: AsyncClient, test_db_session, sample_user):
    """자료 검색 페이지네이션 테스트"""
    # 여러 자료 생성
    materials = [
        MaterialModel(
            title=f"Material {i}",
            url=f"https://example.com/material{i}",
            difficulty=MaterialDifficulty.BEGINNER,
            type=MaterialType.DOCUMENT,
            keywords=["test"],
        )
        for i in range(25)
    ]
    test_db_session.add_all(materials)
    await test_db_session.commit()

    # 로그인
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 첫 페이지
    response = await test_client.get(
        "/api/v1/materials", params={"page": 1, "limit": 10}, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["materials"]) == 10
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["limit"] == 10
    assert data["pagination"]["total"] >= 25
    assert data["pagination"]["total_pages"] >= 3


@pytest.mark.asyncio
async def test_scrap_material_success(test_client: AsyncClient, test_db_session, sample_user):
    """자료 스크랩 성공 테스트"""
    material = MaterialModel(
        title="Scrap Test",
        url="https://example.com/scrap",
        difficulty=MaterialDifficulty.BEGINNER,
        type=MaterialType.DOCUMENT,
    )
    test_db_session.add(material)
    await test_db_session.flush()

    # 로그인
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 스크랩
    response = await test_client.post(
        f"/api/v1/materials/{material.id}/scrap", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_scrapped"] is True

    # 스크랩 해제
    response = await test_client.delete(
        f"/api/v1/materials/{material.id}/scrap", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_scrapped"] is False


@pytest.mark.asyncio
async def test_scrap_material_not_found(test_client: AsyncClient, test_db_session, sample_user):
    """존재하지 않는 자료 스크랩 실패 테스트"""
    # 로그인
    login_response = await test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 존재하지 않는 자료 스크랩
    response = await test_client.post("/api/v1/materials/99999/scrap", headers=headers)
    assert response.status_code == 404
    assert "자료를 찾을 수 없습니다" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_materials_no_auth(test_client: AsyncClient):
    """인증 없이 자료 검색 실패 테스트"""
    response = await test_client.get("/api/v1/materials")
    assert response.status_code == 401

