from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ItemType, RoadmapCategory, UserProgress
from app.infrastructure.db.models import (
    MaterialModel,
    RoadmapModel,
    UserProgressModel,
)


class UserProgressRepository:
    """Handles user roadmap progress state."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_progress_map(self, user_id: int) -> dict[int, bool]:
        stmt = (
            select(
                UserProgressModel.roadmap_id,
                UserProgressModel.is_completed,
            )
            .where(
                and_(
                    UserProgressModel.user_id == user_id,
                    UserProgressModel.item_type == ItemType.ROADMAP.value,
                )
            )
        )
        result = await self.session.execute(stmt)
        return {roadmap_id: completed for roadmap_id, completed in result if roadmap_id}

    async def upsert_progress(
        self,
        *,
        user_id: int,
        item_id: int,
        completed: bool,
        item_type: ItemType,
    ) -> UserProgress:
        target_column = (
            UserProgressModel.roadmap_id
            if item_type == ItemType.ROADMAP
            else UserProgressModel.material_id
        )
        stmt = select(UserProgressModel).where(
            and_(
                UserProgressModel.user_id == user_id,
                UserProgressModel.item_type == item_type.value,
                target_column == item_id,
            )
        )
        progress = await self.session.scalar(stmt)

        if progress:
            progress.is_completed = completed
            progress.completed_at = datetime.now(timezone.utc) if completed else None
        else:
            progress = UserProgressModel(
                user_id=user_id,
                roadmap_id=item_id if item_type == ItemType.ROADMAP else None,
                material_id=item_id if item_type == ItemType.MATERIAL else None,
                item_type=item_type.value,
                is_completed=completed,
                completed_at=datetime.now(timezone.utc) if completed else None,
            )
            self.session.add(progress)

        await self.session.flush()
        await self.session.refresh(progress)
        await self.session.commit()

        return await self._to_entity(progress)

    async def list_by_user(
        self,
        user_id: int,
        category: Optional[RoadmapCategory] = None,
        item_type: Optional[ItemType] = None,
    ) -> list[UserProgress]:
        stmt = (
            select(UserProgressModel, RoadmapModel, MaterialModel)
            .join(
                RoadmapModel,
                and_(
                    UserProgressModel.roadmap_id == RoadmapModel.id,
                    UserProgressModel.item_type == ItemType.ROADMAP.value,
                ),
                isouter=True,
            )
            .join(
                MaterialModel,
                and_(
                    UserProgressModel.material_id == MaterialModel.id,
                    UserProgressModel.item_type == ItemType.MATERIAL.value,
                ),
                isouter=True,
            )
            .where(UserProgressModel.user_id == user_id)
        )
        if item_type:
            stmt = stmt.where(UserProgressModel.item_type == item_type.value)
        if category and item_type not in (ItemType.MATERIAL,):
            stmt = stmt.where(
                and_(
                    UserProgressModel.item_type == ItemType.ROADMAP.value,
                    RoadmapModel.category == category,
                )
            )
        result = await self.session.execute(stmt)
        progress_list: list[UserProgress] = []
        for progress, roadmap, material in result:
            progress_list.append(
                await self._to_entity(progress, roadmap=roadmap, material=material)
            )
        return progress_list

    async def statistics(
        self,
        user_id: int,
        category: Optional[RoadmapCategory] = None,
        item_type: Optional[ItemType] = None,
    ) -> dict[str, float]:
        include_roadmap = item_type in (None, ItemType.ROADMAP)
        include_material = item_type in (None, ItemType.MATERIAL)

        roadmap_total = 0
        if include_roadmap:
            stmt_roadmap_total = select(func.count(RoadmapModel.id))
            if category:
                stmt_roadmap_total = stmt_roadmap_total.where(
                    RoadmapModel.category == category
                )
            roadmap_total = (await self.session.execute(stmt_roadmap_total)).scalar_one()

        material_total = 0
        if include_material:
            stmt_material_total = select(func.count(MaterialModel.id))
            material_total = (
                await self.session.execute(stmt_material_total)
            ).scalar_one()

        roadmap_completed = 0
        if include_roadmap:
            stmt_roadmap_completed = (
                select(func.count(UserProgressModel.id))
                .join(RoadmapModel, UserProgressModel.roadmap_id == RoadmapModel.id)
                .where(
                    and_(
                        UserProgressModel.user_id == user_id,
                        UserProgressModel.item_type == ItemType.ROADMAP.value,
                        UserProgressModel.is_completed.is_(True),
                    )
                )
            )
            if category:
                stmt_roadmap_completed = stmt_roadmap_completed.where(
                    RoadmapModel.category == category
                )
            roadmap_completed = (
                await self.session.execute(stmt_roadmap_completed)
            ).scalar_one()

        material_completed = 0
        if include_material:
            stmt_material_completed = (
                select(func.count(UserProgressModel.id))
                .where(
                    and_(
                        UserProgressModel.user_id == user_id,
                        UserProgressModel.item_type == ItemType.MATERIAL.value,
                        UserProgressModel.is_completed.is_(True),
                    )
                )
            )
            material_completed = (
                await self.session.execute(stmt_material_completed)
            ).scalar_one()

        total_items = roadmap_total + material_total
        completed_items = roadmap_completed + material_completed
        completion_rate = (completed_items / total_items) if total_items else 0.0
        return {
            "total_items": total_items,
            "completed_items": completed_items,
            "completion_rate": completion_rate,
            "roadmap_total": roadmap_total,
            "roadmap_completed": roadmap_completed,
            "material_total": material_total,
            "material_completed": material_completed,
        }

    async def _to_entity(
        self,
        progress: UserProgressModel,
        roadmap: RoadmapModel | None = None,
        material: MaterialModel | None = None,
    ) -> UserProgress:
        if progress.item_type == ItemType.ROADMAP:
            roadmap = roadmap or await self.session.scalar(
                select(RoadmapModel).where(RoadmapModel.id == progress.roadmap_id)
            )
            category = (
                roadmap.category.value
                if roadmap and hasattr(roadmap.category, "value")
                else roadmap.category if roadmap else None
            )
            item_name = roadmap.name if roadmap else ""
            item_id = progress.roadmap_id or 0
        else:
            material = material or await self.session.scalar(
                select(MaterialModel).where(MaterialModel.id == progress.material_id)
            )
            category = (
                material.type.value
                if material and hasattr(material.type, "value")
                else material.type if material else None
            )
            item_name = material.title if material else ""
            item_id = progress.material_id or 0

        return UserProgress(
            id=progress.id,
            user_id=progress.user_id,
            item_id=item_id,
            item_name=item_name,
            item_type=progress.item_type,
            category=category,
            is_completed=progress.is_completed,
            completed_at=progress.completed_at,
        )

