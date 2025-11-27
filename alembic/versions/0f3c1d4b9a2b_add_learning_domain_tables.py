"""add learning domain tables

Revision ID: 0f3c1d4b9a2b
Revises: c830aa068904
Create Date: 2025-11-27 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f3c1d4b9a2b"
down_revision: Union[str, Sequence[str], None] = "c830aa068904"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roadmap_category = sa.Enum(
        "frontend", "backend", "devops", name="roadmap_category"
    )
    material_difficulty = sa.Enum(
        "beginner", "intermediate", name="material_difficulty"
    )
    material_type = sa.Enum("document", "video", name="material_type")

    roadmap_category.create(op.get_bind(), checkfirst=True)
    material_difficulty.create(op.get_bind(), checkfirst=True)
    material_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "roadmaps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", roadmap_category, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["roadmaps.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_roadmaps_category", "roadmaps", ["category"])
    op.create_index("ix_roadmaps_id", "roadmaps", ["id"])

    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("difficulty", material_difficulty, nullable=False),
        sa.Column("type", material_type, nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_materials_id", "materials", ["id"])
    op.create_index("ix_materials_difficulty", "materials", ["difficulty"])
    op.create_index("ix_materials_type", "materials", ["type"])

    op.create_table(
        "user_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("roadmap_id", sa.Integer(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["roadmap_id"], ["roadmaps.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "roadmap_id", name="uq_user_progress"),
    )
    op.create_index("ix_user_progress_id", "user_progress", ["id"])
    op.create_index("ix_user_progress_user_id", "user_progress", ["user_id"])

    op.create_table(
        "material_scraps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["material_id"], ["materials.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("user_id", "material_id", name="uq_material_scrap"),
    )
    op.create_index("ix_material_scraps_id", "material_scraps", ["id"])


def downgrade() -> None:
    op.drop_index("ix_material_scraps_id", table_name="material_scraps")
    op.drop_table("material_scraps")

    op.drop_index("ix_user_progress_user_id", table_name="user_progress")
    op.drop_index("ix_user_progress_id", table_name="user_progress")
    op.drop_table("user_progress")

    op.drop_index("ix_materials_type", table_name="materials")
    op.drop_index("ix_materials_difficulty", table_name="materials")
    op.drop_index("ix_materials_id", table_name="materials")
    op.drop_table("materials")

    op.drop_index("ix_roadmaps_id", table_name="roadmaps")
    op.drop_index("ix_roadmaps_category", table_name="roadmaps")
    op.drop_table("roadmaps")

    material_type = sa.Enum(
        "document", "video", name="material_type"
    )
    material_difficulty = sa.Enum(
        "beginner", "intermediate", name="material_difficulty"
    )
    roadmap_category = sa.Enum(
        "frontend", "backend", "devops", name="roadmap_category"
    )

    material_type.drop(op.get_bind(), checkfirst=True)
    material_difficulty.drop(op.get_bind(), checkfirst=True)
    roadmap_category.drop(op.get_bind(), checkfirst=True)

