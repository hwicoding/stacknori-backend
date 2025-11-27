from fastapi import APIRouter, Depends, Query

from app.core.dependencies import (
    get_current_user,
    get_progress_overview_usecase,
    get_update_progress_usecase,
)
from app.domain.entities import User
from app.schemas import (
    ProgressOverviewResponse,
    ProgressUpdateRequest,
    ProgressUpdateResponse,
)
from app.usecases.progress import GetUserProgressUseCase, UpdateProgressUseCase

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post(
    "/{item_id}/complete",
    response_model=ProgressUpdateResponse,
)
async def update_progress(
    item_id: int,
    payload: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    usecase: UpdateProgressUseCase = Depends(get_update_progress_usecase),
) -> ProgressUpdateResponse:
    result = await usecase.execute(
        user_id=current_user.id,
        item_id=item_id,
        completed=payload.completed,
    )
    return ProgressUpdateResponse(
        success=True,
        item_id=result.roadmap_id,
        is_completed=result.is_completed,
    )


@router.get("", response_model=ProgressOverviewResponse)
async def get_progress_overview(
    category: str | None = Query(None, pattern="^(frontend|backend|devops)$"),
    current_user: User = Depends(get_current_user),
    usecase: GetUserProgressUseCase = Depends(get_progress_overview_usecase),
) -> ProgressOverviewResponse:
    result = await usecase.execute(
        user_id=current_user.id,
        category=category,
    )
    return ProgressOverviewResponse(**result)

