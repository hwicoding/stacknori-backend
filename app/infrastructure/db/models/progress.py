from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.entities import ItemType


class UserProgressModel(Base):
    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "roadmap_id", name="uq_user_progress"),
        UniqueConstraint("user_id", "material_id", name="uq_user_material_progress"),
        CheckConstraint(
            "(item_type = 'roadmap' AND roadmap_id IS NOT NULL AND material_id IS NULL)"
            " OR (item_type = 'material' AND material_id IS NOT NULL AND roadmap_id IS NULL)",
            name="ck_user_progress_item_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    roadmap_id: Mapped[int | None] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=True, index=True
    )
    material_id: Mapped[int | None] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE"), nullable=True, index=True
    )
    item_type: Mapped[ItemType] = mapped_column(
        Enum(
            ItemType,
            name="progress_item_type",
            values_callable=lambda enum: [choice.value for choice in enum],
        ),
        nullable=False,
        default=ItemType.ROADMAP.value,
        server_default=ItemType.ROADMAP.value,
        index=True,
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    roadmap: Mapped["RoadmapModel"] = relationship(
        "RoadmapModel", back_populates="progress_entries"
    )
    material: Mapped["MaterialModel"] = relationship(
        "MaterialModel", back_populates="progress_entries"
    )
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="progress")


