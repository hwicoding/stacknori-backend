import pytest
from httpx import AsyncClient

from app.domain.entities.roadmap import RoadmapCategory
from app.infrastructure.db.models.roadmap import RoadmapModel


@pytest.mark.asyncio
async def test_list_roadmaps_success(test_client: AsyncClient, test_db_session, sample_user):
    """로드맵 목록 조회 성공 테스트"""
    # 로드맵 데이터 생성
    root = RoadmapModel(
        category=RoadmapCategory.FRONTEND,
        name="Frontend Basics",
        level=1,
        description="Frontend fundamentals",
    )
    child = RoadmapModel(
        category=RoadmapCategory.FRONTEND,
        name="HTML/CSS",
        level=2,
        description="HTML and CSS basics",
        parent_id=None,  # Will be set after root is saved
    )
    test_db_session.add(root)
    await test_db_session.flush()
    child.parent_id = root.id
    test_db_session.add(child)
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

    # 로드맵 조회
    response = await test_client.get("/api/v1/roadmaps", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "roadmaps" in data
    assert len(data["roadmaps"]) > 0
    assert any(rm["name"] == "Frontend Basics" for rm in data["roadmaps"])


@pytest.mark.asyncio
async def test_list_roadmaps_with_progress(test_client: AsyncClient, test_db_session, sample_user):
    """진도가 있는 로드맵 조회 테스트"""
    roadmap = RoadmapModel(
        category=RoadmapCategory.BACKEND,
        name="Backend Basics",
        level=1,
        description="Backend fundamentals",
    )
    test_db_session.add(roadmap)
    await test_db_session.flush()

    # Progress 생성
    from app.infrastructure.db.models.progress import UserProgressModel
    from app.domain.entities.progress import ItemType

    progress = UserProgressModel(
        user_id=sample_user.id,
        roadmap_id=roadmap.id,
        item_type=ItemType.ROADMAP.value,
        is_completed=True,
    )
    test_db_session.add(progress)
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

    # 로드맵 조회
    response = await test_client.get("/api/v1/roadmaps", headers=headers)
    assert response.status_code == 200
    data = response.json()
    roadmap_item = next((rm for rm in data["roadmaps"] if rm["name"] == "Backend Basics"), None)
    assert roadmap_item is not None
    assert roadmap_item["is_completed"] is True


@pytest.mark.asyncio
async def test_list_roadmaps_no_auth(test_client: AsyncClient):
    """인증 없이 로드맵 조회 실패 테스트"""
    response = await test_client.get("/api/v1/roadmaps")
    assert response.status_code == 401

