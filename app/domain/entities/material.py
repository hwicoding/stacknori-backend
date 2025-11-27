from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MaterialDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"


class MaterialType(str, Enum):
    DOCUMENT = "document"
    VIDEO = "video"


class Material(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    difficulty: MaterialDifficulty
    type: MaterialType
    source: Optional[str] = None
    summary: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    is_scrapped: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

