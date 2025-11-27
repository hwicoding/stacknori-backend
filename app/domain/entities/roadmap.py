from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RoadmapCategory(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"


class Roadmap(BaseModel):
    id: int
    category: RoadmapCategory
    name: str
    level: int
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_completed: bool = False
    children: List["Roadmap"] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

