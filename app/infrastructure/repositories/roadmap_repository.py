from __future__ import annotations

from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models import RoadmapModel


class RoadmapRepository:
    """Data access for roadmap nodes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[RoadmapModel]:
        stmt = select(RoadmapModel).options(selectinload(RoadmapModel.children))
        result = await self.session.scalars(stmt)
        return list(result)

    async def exists(self, roadmap_id: int) -> bool:
        stmt = select(RoadmapModel.id).where(RoadmapModel.id == roadmap_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    @staticmethod
    def flatten(models: Iterable[RoadmapModel]) -> list[RoadmapModel]:
        ordered: list[RoadmapModel] = []

        def _traverse(node: RoadmapModel) -> None:
            ordered.append(node)
            for child in node.children:
                _traverse(child)

        for roadmap in models:
            _traverse(roadmap)
        return ordered

