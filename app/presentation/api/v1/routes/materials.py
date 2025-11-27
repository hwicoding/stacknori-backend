from fastapi import APIRouter, Depends, Query

from app.core.dependencies import (
    get_current_user,
    get_material_scrap_usecase,
    get_material_search_usecase,
)
from app.domain.entities import User
from app.schemas import MaterialItem, MaterialListResponse, ScrapResponse
from app.usecases.material import SearchMaterialsUseCase, ToggleMaterialScrapUseCase

router = APIRouter(prefix="/materials", tags=["Materials"])


def _material_to_item(material) -> MaterialItem:
    """Material 엔티티를 MaterialItem 스키마로 변환"""
    return MaterialItem(
        id=material.id,
        title=material.title,
        url=material.url,
        difficulty=material.difficulty.value if hasattr(material.difficulty, "value") else material.difficulty,
        type=material.type.value if hasattr(material.type, "value") else material.type,
        source=material.source,
        summary=material.summary,
        keywords=material.keywords or [],
        is_scrapped=material.is_scrapped,
    )


@router.get("", response_model=MaterialListResponse)
async def search_materials(
    keyword: str | None = Query(None, description="검색 키워드"),
    difficulty: str | None = Query(None, pattern="^(beginner|intermediate)$"),
    material_type: str | None = Query(
        None, alias="type", pattern="^(document|video)$"
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    usecase: SearchMaterialsUseCase = Depends(get_material_search_usecase),
) -> MaterialListResponse:
    result = await usecase.execute(
        user_id=current_user.id,
        keyword=keyword,
        difficulty=difficulty,
        resource_type=material_type,
        page=page,
        limit=limit,
    )
    items = [_material_to_item(m) for m in result["materials"]]
    return MaterialListResponse(
        materials=items,
        pagination=result["pagination"],
    )


@router.post("/{material_id}/scrap", response_model=ScrapResponse)
async def scrap_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    usecase: ToggleMaterialScrapUseCase = Depends(get_material_scrap_usecase),
) -> ScrapResponse:
    is_scrapped = await usecase.execute(
        user_id=current_user.id, material_id=material_id, scrap=True
    )
    return ScrapResponse(success=True, is_scrapped=is_scrapped)


@router.delete("/{material_id}/scrap", response_model=ScrapResponse)
async def unscrap_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    usecase: ToggleMaterialScrapUseCase = Depends(get_material_scrap_usecase),
) -> ScrapResponse:
    is_scrapped = await usecase.execute(
        user_id=current_user.id, material_id=material_id, scrap=False
    )
    return ScrapResponse(success=True, is_scrapped=is_scrapped)

