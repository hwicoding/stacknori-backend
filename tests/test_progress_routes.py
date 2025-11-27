import pytest
from httpx import AsyncClient

from app.domain.entities.roadmap import RoadmapCategory
from app.infrastructure.db.models.material import MaterialDifficulty, MaterialModel, MaterialType
from app.infrastructure.db.models.roadmap import RoadmapModel


@pytest.mark.asyncio
async def test_progress_supports_materials(
    test_client: AsyncClient, test_db_session, sample_user
):
    roadmap = RoadmapModel(
        category=RoadmapCategory.FRONTEND,
        name="Frontend Basics",
        level=1,
        description="HTML/CSS",
    )
    material = MaterialModel(
        title="FastAPI Getting Started",
        url="https://example.com/fastapi",
        difficulty=MaterialDifficulty.BEGINNER,
        type=MaterialType.DOCUMENT,
        source="Stacknori",
        summary="Intro tutorial",
        keywords=["fastapi", "backend"],
    )
    test_db_session.add_all([roadmap, material])
    await test_db_session.flush()

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

    resp = await test_client.post(
        f"/api/v1/progress/{roadmap.id}/complete",
        json={"completed": True},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["item_type"] == "roadmap"
    assert data["item_id"] == roadmap.id
    assert data["is_completed"] is True

    resp = await test_client.post(
        f"/api/v1/progress/{material.id}/complete",
        params={"type": "material"},
        json={"completed": True},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["item_type"] == "material"
    assert data["item_id"] == material.id

    overview = await test_client.get("/api/v1/progress", headers=headers)
    assert overview.status_code == 200
    body = overview.json()
    assert len(body["progress"]) == 2
    stats = body["statistics"]
    assert stats["roadmap_completed"] == 1
    assert stats["material_completed"] == 1

    material_only = await test_client.get(
        "/api/v1/progress", params={"type": "material"}, headers=headers
    )
    assert material_only.status_code == 200
    items = material_only.json()["progress"]
    assert len(items) == 1
    assert items[0]["item_type"] == "material"

