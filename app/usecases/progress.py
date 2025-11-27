from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status

from app.domain.entities import RoadmapCategory, UserProgress
from app.infrastructure.repositories.progress_repository import UserProgressRepository
from app.infrastructure.repositories.roadmap_repository import RoadmapRepository


class UpdateProgressUseCase:
    def __init__(
        self,
        roadmap_repository: RoadmapRepository,
        progress_repository: UserProgressRepository,
    ) -> None:
        self.roadmap_repository = roadmap_repository
        self.progress_repository = progress_repository

    async def execute(
        self, *, user_id: int, item_id: int, completed: bool
    ) -> UserProgress:
        exists = await self.roadmap_repository.exists(item_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="로드맵 항목을 찾을 수 없습니다.",
            )
        return await self.progress_repository.upsert_progress(
            user_id=user_id, roadmap_id=item_id, completed=completed
        )


class GetUserProgressUseCase:
    def __init__(self, progress_repository: UserProgressRepository) -> None:
        self.progress_repository = progress_repository

    async def execute(
        self, *, user_id: int, category: Optional[str] = None
    ) -> dict:
        category_enum = RoadmapCategory(category) if category else None
        items = await self.progress_repository.list_by_user(
            user_id=user_id, category=category_enum
        )
        stats = await self.progress_repository.statistics(
            user_id=user_id, category=category_enum
        )
        return {
            "progress": items,
            "statistics": stats,
        }

