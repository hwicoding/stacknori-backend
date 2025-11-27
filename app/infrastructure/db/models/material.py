from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    JSON,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MaterialDifficulty(str, PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"


class MaterialType(str, PyEnum):
    DOCUMENT = "document"
    VIDEO = "video"


class MaterialModel(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    difficulty: Mapped[MaterialDifficulty] = mapped_column(
        SqlEnum(MaterialDifficulty, name="material_difficulty"),
        nullable=False,
        default=MaterialDifficulty.BEGINNER,
    )
    type: Mapped[MaterialType] = mapped_column(
        SqlEnum(MaterialType, name="material_type"),
        nullable=False,
        default=MaterialType.DOCUMENT,
    )
    source: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text())
    keywords: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    scraps: Mapped[list["MaterialScrapModel"]] = relationship(
        "MaterialScrapModel",
        back_populates="material",
        cascade="all, delete-orphan",
    )
    progress_entries: Mapped[list["UserProgressModel"]] = relationship(
        "UserProgressModel",
        back_populates="material",
        cascade="all, delete-orphan",
    )


