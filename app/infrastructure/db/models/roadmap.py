from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RoadmapCategory(str, PyEnum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"


class RoadmapModel(Base):
    __tablename__ = "roadmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[RoadmapCategory] = mapped_column(
        SqlEnum(RoadmapCategory, name="roadmap_category"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str | None] = mapped_column(Text())
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    parent: Mapped["RoadmapModel"] = relationship(
        "RoadmapModel", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["RoadmapModel"]] = relationship(
        "RoadmapModel",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    progress_entries: Mapped[list["UserProgressModel"]] = relationship(
        "UserProgressModel",
        back_populates="roadmap",
        cascade="all, delete-orphan",
    )


