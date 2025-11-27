from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RoadmapNode(BaseModel):
    id: int
    category: str
    name: str
    level: int
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_completed: bool = False
    children: List["RoadmapNode"] = Field(default_factory=list)


class RoadmapListResponse(BaseModel):
    roadmaps: List[RoadmapNode]

