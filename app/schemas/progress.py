from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class ProgressItemType(str, Enum):
    ROADMAP = "roadmap"
    MATERIAL = "material"


class ProgressUpdateRequest(BaseModel):
    completed: bool


class ProgressItem(BaseModel):
    item_id: int
    item_name: str
    item_type: ProgressItemType
    category: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None


class ProgressStatistics(BaseModel):
    total_items: int
    completed_items: int
    completion_rate: float
    roadmap_total: int
    roadmap_completed: int
    material_total: int
    material_completed: int


class ProgressOverviewResponse(BaseModel):
    progress: List[ProgressItem]
    statistics: ProgressStatistics


class ProgressUpdateResponse(BaseModel):
    success: bool
    item_id: int
    item_type: ProgressItemType
    is_completed: bool

