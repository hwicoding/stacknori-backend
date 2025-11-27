from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class MaterialItem(BaseModel):
    id: int
    title: str
    url: str
    difficulty: str
    type: str
    source: Optional[str] = None
    summary: Optional[str] = None
    keywords: List[str]
    is_scrapped: bool


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class MaterialListResponse(BaseModel):
    materials: List[MaterialItem]
    pagination: PaginationMeta


class ScrapResponse(BaseModel):
    success: bool
    is_scrapped: bool

