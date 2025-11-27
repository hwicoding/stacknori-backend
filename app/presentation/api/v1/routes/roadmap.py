from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_current_user,
    get_roadmap_usecase,
)
from app.domain.entities import User
from app.schemas import RoadmapListResponse
from app.usecases.roadmap import GetRoadmapsUseCase

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


@router.get("", response_model=RoadmapListResponse)
async def list_roadmaps(
    current_user: User = Depends(get_current_user),
    usecase: GetRoadmapsUseCase = Depends(get_roadmap_usecase),
) -> RoadmapListResponse:
    roadmaps = await usecase.execute(user_id=current_user.id)
    return RoadmapListResponse(roadmaps=roadmaps)

