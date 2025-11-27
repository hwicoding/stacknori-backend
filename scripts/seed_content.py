#!/usr/bin/env python3
"""
Seed script for initial roadmap/material data.

Usage:
    python scripts/seed_content.py

Environment variables (optional):
    DATABASE_URL - overrides the default settings.database_url
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure project root on sys.path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.domain.entities.roadmap import RoadmapCategory
from app.domain.entities.material import MaterialDifficulty, MaterialType
from app.infrastructure.db.models import (
    MaterialModel,
    RoadmapModel,
)


ROADMAP_DATA: list[dict[str, Any]] = [
    {
        "category": RoadmapCategory.FRONTEND,
        "name": "Frontend Fundamentals",
        "level": 1,
        "description": "브라우저 렌더링과 기본 웹 기술 이해",
        "children": [
            {
                "name": "HTML & CSS",
                "level": 1,
                "description": "시맨틱 마크업과 레이아웃 기초",
                "children": [
                    {
                        "name": "Responsive Layout",
                        "level": 2,
                        "description": "Flex/Grid를 활용한 반응형 구성",
                    }
                ],
            },
            {
                "name": "Javascript Core",
                "level": 1,
                "description": "ES6+, 비동기 흐름 이해",
                "children": [
                    {
                        "name": "React",
                        "level": 2,
                        "description": "컴포넌트 기반 SPA",
                        "children": [
                            {
                                "name": "React Hooks",
                                "level": 3,
                                "description": "상태/사이드이펙트 패턴",
                            }
                        ],
                    }
                ],
            },
        ],
    },
    {
        "category": RoadmapCategory.BACKEND,
        "name": "Backend Fundamentals",
        "level": 1,
        "description": "API 서버와 데이터 저장소 기초",
        "children": [
            {
                "name": "Python Web Framework",
                "level": 2,
                "description": "FastAPI, Flask 등 비교",
                "children": [
                    {
                        "name": "FastAPI Clean Architecture",
                        "level": 3,
                        "description": "유즈케이스/도메인 분리",
                    }
                ],
            },
            {
                "name": "Database Design",
                "level": 2,
                "description": "정규화, ORM, 마이그레이션",
            },
        ],
    },
    {
        "category": RoadmapCategory.DEVOPS,
        "name": "DevOps Essentials",
        "level": 1,
        "description": "CI/CD와 모니터링 기초",
        "children": [
            {
                "name": "Docker & Compose",
                "level": 2,
                "description": "컨테이너 기반 배포",
            },
            {
                "name": "GitHub Actions",
                "level": 2,
                "description": "워크플로우 자동화",
            },
        ],
    },
]

MATERIAL_DATA: list[dict[str, Any]] = [
    {
        "title": "React 공식 문서",
        "url": "https://react.dev",
        "difficulty": MaterialDifficulty.BEGINNER,
        "type": MaterialType.DOCUMENT,
        "source": "React Team",
        "summary": "최신 React 훅과 컴포넌트 패턴 정리",
        "keywords": ["react", "frontend", "javascript"],
    },
    {
        "title": "FastAPI 공식 튜토리얼",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "difficulty": MaterialDifficulty.BEGINNER,
        "type": MaterialType.DOCUMENT,
        "source": "FastAPI",
        "summary": "FastAPI 핵심 개념과 예제",
        "keywords": ["fastapi", "python", "backend"],
    },
    {
        "title": "Docker Compose 로컬 배포",
        "url": "https://docs.docker.com/compose/",
        "difficulty": MaterialDifficulty.INTERMEDIATE,
        "type": MaterialType.DOCUMENT,
        "source": "Docker Docs",
        "summary": "멀티 컨테이너 환경 구성 가이드",
        "keywords": ["docker", "devops", "compose"],
    },
    {
        "title": "클라우드에서 GitHub Actions로 배포 자동화",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "difficulty": MaterialDifficulty.INTERMEDIATE,
        "type": MaterialType.VIDEO,
        "source": "Livbee Dev",
        "summary": "실전 CI/CD 파이프라인 구축",
        "keywords": ["github-actions", "ci-cd", "devops"],
    },
]


async def upsert_roadmap(
    session: AsyncSession,
    data: dict[str, Any],
    *,
    category: RoadmapCategory,
    parent_id: int | None = None,
) -> RoadmapModel:
    name = data["name"]
    conditions = [
        RoadmapModel.name == name,
        RoadmapModel.category == category,
    ]
    if parent_id is None:
        conditions.append(RoadmapModel.parent_id.is_(None))
    else:
        conditions.append(RoadmapModel.parent_id == parent_id)
    stmt = select(RoadmapModel).where(*conditions)
    existing = await session.scalar(stmt)
    if existing:
        existing.description = data.get("description")
        existing.level = data.get("level", existing.level)
        existing.parent_id = parent_id
        node = existing
    else:
        node = RoadmapModel(
            name=name,
            category=category,
            level=data.get("level", 1),
            description=data.get("description"),
            parent_id=parent_id,
        )
        session.add(node)
        await session.flush()

    for child in data.get("children", []):
        await upsert_roadmap(
            session,
            child,
            category=category,
            parent_id=node.id,
        )
    return node


async def seed_roadmaps(session: AsyncSession) -> None:
    for entry in ROADMAP_DATA:
        await upsert_roadmap(
            session,
            entry,
            category=entry["category"],
            parent_id=None,
        )
    await session.commit()


async def seed_materials(session: AsyncSession) -> None:
    for entry in MATERIAL_DATA:
        stmt = select(MaterialModel).where(MaterialModel.title == entry["title"])
        existing = await session.scalar(stmt)
        if existing:
            existing.url = entry["url"]
            existing.difficulty = entry["difficulty"]
            existing.type = entry["type"]
            existing.source = entry.get("source")
            existing.summary = entry.get("summary")
            existing.keywords = entry.get("keywords", [])
        else:
            material = MaterialModel(
                title=entry["title"],
                url=entry["url"],
                difficulty=entry["difficulty"],
                type=entry["type"],
                source=entry.get("source"),
                summary=entry.get("summary"),
                keywords=entry.get("keywords", []),
            )
            session.add(material)
    await session.commit()


async def main() -> None:
    settings = get_settings()
    database_url = os.getenv("DATABASE_URL", settings.database_url)
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        print("🌱 Seeding roadmaps...")
        await seed_roadmaps(session)
        print("🌱 Seeding materials...")
        await seed_materials(session)
        print("✨ Seeding completed.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

