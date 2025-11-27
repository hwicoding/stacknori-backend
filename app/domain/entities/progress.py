from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemType(str, Enum):
    ROADMAP = "roadmap"
    MATERIAL = "material"


class UserProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    item_id: int
    item_name: str
    item_type: ItemType
    category: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None

