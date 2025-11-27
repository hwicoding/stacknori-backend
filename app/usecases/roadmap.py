from __future__ import annotations

from typing import List

from app.domain.entities import Roadmap, RoadmapCategory
from app.infrastructure.db.models import RoadmapModel
from app.infrastructure.repositories.progress_repository import (
    UserProgressRepository,
)
from app.infrastructure.repositories.roadmap_repository import RoadmapRepository


class GetRoadmapsUseCase:
    """Returns roadmap tree with user progress applied."""

    def __init__(
        self,
        roadmap_repository: RoadmapRepository,
        progress_repository: UserProgressRepository,
    ) -> None:
        self.roadmap_repository = roadmap_repository
        self.progress_repository = progress_repository

    async def execute(self, *, user_id: int) -> List[Roadmap]:
        models = await self.roadmap_repository.list_all()
        progress_map = await self.progress_repository.get_progress_map(user_id)

        node_map: dict[int, Roadmap] = {}
        for model in models:
            node_map[model.id] = self._to_entity(
                model, is_completed=progress_map.get(model.id, False)
            )

        roots: list[Roadmap] = []
        for model in models:
            node = node_map[model.id]
            if model.parent_id is None:
                roots.append(node)
            else:
                parent = node_map.get(model.parent_id)
                if parent:
                    parent.children.append(node)
        return roots

    def _to_entity(self, model: RoadmapModel, *, is_completed: bool) -> Roadmap:
        category_value = (
            model.category.value if hasattr(model.category, "value") else model.category
        )
        return Roadmap(
            id=model.id,
            category=RoadmapCategory(category_value),
            name=model.name,
            level=model.level,
            description=model.description,
            parent_id=model.parent_id,
            is_completed=is_completed,
            children=[],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

