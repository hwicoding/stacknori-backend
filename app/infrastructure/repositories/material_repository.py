from __future__ import annotations

import json
from typing import Sequence

from sqlalchemy import and_, func, or_, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Material, MaterialDifficulty, MaterialType
from app.infrastructure.db.models import MaterialModel, MaterialScrapModel


class MaterialRepository:
    """Data access for learning materials."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(
        self,
        *,
        keyword: str | None = None,
        difficulty: MaterialDifficulty | None = None,
        type_: MaterialType | None = None,
        page: int = 1,
        limit: int = 20,
        user_id: int | None = None,
    ) -> tuple[list[Material], int]:
        stmt = select(MaterialModel)
        count_stmt = select(func.count(MaterialModel.id))

        filters = []
        if keyword:
            ilike = f"%{keyword}%"
            # title과 summary만 DB 레벨에서 검색
            # keywords는 Python 레벨에서 필터링 (SQLite JSON 검색 이슈 회피)
            filters.append(
                or_(
                    MaterialModel.title.ilike(ilike),
                    MaterialModel.summary.ilike(ilike),
                )
            )
        if difficulty:
            filters.append(MaterialModel.difficulty == difficulty)
        if type_:
            filters.append(MaterialModel.type == type_)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        stmt = stmt.order_by(MaterialModel.created_at.desc())
        total = (await self.session.execute(count_stmt)).scalar_one()

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        materials_result = await self.session.scalars(stmt)
        materials_list = list(materials_result)
        
        # keywords 검색은 Python 레벨에서 필터링
        if keyword:
            keyword_lower = keyword.lower()
            materials_list = [
                m for m in materials_list
                if keyword_lower in m.title.lower()
                or (m.summary and keyword_lower in m.summary.lower())
                or (m.keywords and any(keyword_lower in str(k).lower() for k in (m.keywords or [])))
            ]
            # Python 필터링 후 total 재계산
            total = len(materials_list)
        
        scrap_ids: set[int] = set()
        if user_id:
            scrap_stmt = select(MaterialScrapModel.material_id).where(
                MaterialScrapModel.user_id == user_id
            )
            scrap_ids = set((await self.session.execute(scrap_stmt)).scalars().all())

        return (
            [
                self._to_entity(model, is_scrapped=model.id in scrap_ids)
                for model in materials_list
            ],
            total,
        )

    async def get_by_id(self, material_id: int) -> MaterialModel | None:
        stmt = select(MaterialModel).where(MaterialModel.id == material_id)
        return await self.session.scalar(stmt)

    def _to_entity(self, model: MaterialModel, *, is_scrapped: bool) -> Material:
        keywords = model.keywords or []
        return Material(
            id=model.id,
            title=model.title,
            url=model.url,
            difficulty=MaterialDifficulty(
                model.difficulty.value if hasattr(model.difficulty, "value") else model.difficulty
            ),
            type=MaterialType(
                model.type.value if hasattr(model.type, "value") else model.type
            ),
            source=model.source,
            summary=model.summary,
            keywords=list(keywords),
            is_scrapped=is_scrapped,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class MaterialScrapRepository:
    """Handles user scrap state for materials."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def set_scrap(
        self, user_id: int, material_id: int, scrap: bool
    ) -> bool:
        stmt = select(MaterialScrapModel).where(
            and_(
                MaterialScrapModel.user_id == user_id,
                MaterialScrapModel.material_id == material_id,
            )
        )
        scrap_entry = await self.session.scalar(stmt)

        if scrap:
            if scrap_entry is None:
                scrap_entry = MaterialScrapModel(
                    user_id=user_id, material_id=material_id
                )
                self.session.add(scrap_entry)
                await self.session.flush()
        else:
            if scrap_entry:
                await self.session.delete(scrap_entry)

        await self.session.commit()
        return scrap

