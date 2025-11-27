from __future__ import annotations

from math import ceil
from typing import Optional

from fastapi import HTTPException, status

from app.domain.entities import MaterialDifficulty, MaterialType
from app.infrastructure.repositories.material_repository import (
    MaterialRepository,
    MaterialScrapRepository,
)


class SearchMaterialsUseCase:
    def __init__(self, repository: MaterialRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        *,
        user_id: int,
        keyword: Optional[str] = None,
        difficulty: Optional[str] = None,
        resource_type: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        difficulty_enum = (
            MaterialDifficulty(difficulty) if difficulty else None
        )
        type_enum = MaterialType(resource_type) if resource_type else None
        materials, total = await self.repository.search(
            keyword=keyword,
            difficulty=difficulty_enum,
            type_=type_enum,
            page=page,
            limit=limit,
            user_id=user_id,
        )
        total_pages = ceil(total / limit) if limit else 1
        return {
            "materials": materials,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
            },
        }


class ToggleMaterialScrapUseCase:
    def __init__(
        self,
        scrap_repository: MaterialScrapRepository,
        material_repository: MaterialRepository,
    ) -> None:
        self.scrap_repository = scrap_repository
        self.material_repository = material_repository

    async def execute(
        self, *, user_id: int, material_id: int, scrap: bool
    ) -> bool:
        material = await self.material_repository.get_by_id(material_id)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="자료를 찾을 수 없습니다.",
            )
        return await self.scrap_repository.set_scrap(
            user_id=user_id, material_id=material_id, scrap=scrap
        )

