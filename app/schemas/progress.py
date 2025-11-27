from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ProgressUpdateRequest(BaseModel):
    completed: bool


class ProgressItem(BaseModel):
    item_id: int
    item_name: str
    category: str
    is_completed: bool
    completed_at: Optional[datetime] = None


class ProgressStatistics(BaseModel):
    total_items: int
    completed_items: int
    completion_rate: float


class ProgressOverviewResponse(BaseModel):
    progress: List[ProgressItem]
    statistics: ProgressStatistics


class ProgressUpdateResponse(BaseModel):
    success: bool
    item_id: int
    is_completed: bool

