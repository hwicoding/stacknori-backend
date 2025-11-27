from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.entities.roadmap import RoadmapCategory


class UserProgress(BaseModel):
    id: int
    user_id: int
    item_id: int
    item_name: str
    category: RoadmapCategory
    is_completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

