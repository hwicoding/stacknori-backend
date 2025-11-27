from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MaterialScrapModel(Base):
    __tablename__ = "material_scraps"
    __table_args__ = (
        UniqueConstraint("user_id", "material_id", name="uq_material_scrap"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    material: Mapped["MaterialModel"] = relationship(
        "MaterialModel", back_populates="scraps"
    )
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="scraps")


