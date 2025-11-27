from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import RoadmapCategory, UserProgress
from app.infrastructure.db.models import RoadmapModel, UserProgressModel


class UserProgressRepository:
    """Handles user roadmap progress state."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_progress_map(self, user_id: int) -> dict[int, bool]:
        stmt = select(
            UserProgressModel.roadmap_id, UserProgressModel.is_completed
        ).where(UserProgressModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return {roadmap_id: completed for roadmap_id, completed in result}

    async def upsert_progress(
        self, user_id: int, roadmap_id: int, completed: bool
    ) -> UserProgress:
        stmt = select(UserProgressModel).where(
            and_(
                UserProgressModel.user_id == user_id,
                UserProgressModel.roadmap_id == roadmap_id,
            )
        )
        progress = await self.session.scalar(stmt)

        if progress:
            progress.is_completed = completed
            progress.completed_at = datetime.utcnow() if completed else None
        else:
            progress = UserProgressModel(
                user_id=user_id,
                roadmap_id=roadmap_id,
                is_completed=completed,
                completed_at=datetime.utcnow() if completed else None,
            )
            self.session.add(progress)

        await self.session.flush()
        await self.session.refresh(progress)
        await self.session.commit()

        roadmap_stmt = select(RoadmapModel).where(RoadmapModel.id == roadmap_id)
        roadmap = await self.session.scalar(roadmap_stmt)
        category = (
            RoadmapCategory(
                roadmap.category.value
                if hasattr(roadmap.category, "value")
                else roadmap.category
            )
            if roadmap
            else RoadmapCategory.FRONTEND
        )
        name = roadmap.name if roadmap else ""
        return UserProgress(
            id=progress.id,
            user_id=user_id,
            item_id=roadmap_id,
            item_name=name,
            category=category,
            is_completed=progress.is_completed,
            completed_at=progress.completed_at,
        )

    async def list_by_user(
        self, user_id: int, category: Optional[RoadmapCategory] = None
    ) -> list[UserProgress]:
        stmt = (
            select(UserProgressModel, RoadmapModel)
            .join(RoadmapModel, UserProgressModel.roadmap_id == RoadmapModel.id)
            .where(UserProgressModel.user_id == user_id)
        )
        if category:
            stmt = stmt.where(RoadmapModel.category == category)
        result = await self.session.execute(stmt)
        progress_list: list[UserProgress] = []
        for progress, roadmap in result:
            progress_list.append(
                UserProgress(
                    id=progress.id,
                    user_id=user_id,
                    item_id=progress.roadmap_id,
                    item_name=roadmap.name,
                    category=RoadmapCategory(
                        roadmap.category.value if hasattr(roadmap.category, "value") else roadmap.category
                    ),
                    is_completed=progress.is_completed,
                    completed_at=progress.completed_at,
                )
            )
        return progress_list

    async def statistics(
        self, user_id: int, category: Optional[RoadmapCategory] = None
    ) -> dict[str, float]:
        stmt = select(func.count(RoadmapModel.id))
        stmt_completed = select(func.count(UserProgressModel.id)).where(
            and_(
                UserProgressModel.user_id == user_id,
                UserProgressModel.is_completed.is_(True),
            )
        ).join(RoadmapModel, UserProgressModel.roadmap_id == RoadmapModel.id)

        if category:
            stmt = stmt.where(RoadmapModel.category == category)
            stmt_completed = stmt_completed.where(RoadmapModel.category == category)

        total = (await self.session.execute(stmt)).scalar_one()
        completed = (await self.session.execute(stmt_completed)).scalar_one()
        completion_rate = (completed / total) if total else 0.0
        return {
            "total_items": total,
            "completed_items": completed,
            "completion_rate": completion_rate,
        }

