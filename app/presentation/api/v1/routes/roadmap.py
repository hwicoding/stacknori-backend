from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_current_user,
    get_roadmap_usecase,
)
from app.domain.entities import User
from app.schemas import RoadmapListResponse, RoadmapNode
from app.usecases.roadmap import GetRoadmapsUseCase

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


def _roadmap_to_node(roadmap) -> RoadmapNode:
    """Roadmap 엔티티를 RoadmapNode 스키마로 변환"""
    return RoadmapNode(
        id=roadmap.id,
        category=roadmap.category.value if hasattr(roadmap.category, "value") else roadmap.category,
        name=roadmap.name,
        level=roadmap.level,
        description=roadmap.description,
        parent_id=roadmap.parent_id,
        is_completed=roadmap.is_completed,
        children=[_roadmap_to_node(child) for child in roadmap.children],
    )


@router.get("", response_model=RoadmapListResponse)
async def list_roadmaps(
    current_user: User = Depends(get_current_user),
    usecase: GetRoadmapsUseCase = Depends(get_roadmap_usecase),
) -> RoadmapListResponse:
    roadmaps = await usecase.execute(user_id=current_user.id)
    nodes = [_roadmap_to_node(rm) for rm in roadmaps]
    return RoadmapListResponse(roadmaps=nodes)

