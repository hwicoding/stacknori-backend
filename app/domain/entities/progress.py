from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ItemType(str, Enum):
    ROADMAP = "roadmap"
    MATERIAL = "material"


class UserProgress(BaseModel):
    id: int
    user_id: int
    item_id: int
    item_name: str
    item_type: ItemType
    category: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

