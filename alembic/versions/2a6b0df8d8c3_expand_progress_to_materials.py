"""expand progress tracking to materials

Revision ID: 2a6b0df8d8c3
Revises: 0f3c1d4b9a2b
Create Date: 2025-11-27 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2a6b0df8d8c3"
down_revision: Union[str, Sequence[str], None] = "0f3c1d4b9a2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


progress_item_type = sa.Enum("roadmap", "material", name="progress_item_type")


def upgrade() -> None:
    bind = op.get_bind()
    progress_item_type.create(bind, checkfirst=True)

    op.alter_column(
        "user_progress",
        "roadmap_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.add_column(
        "user_progress",
        sa.Column(
            "item_type",
            progress_item_type,
            nullable=False,
            server_default="roadmap",
        ),
    )
    op.add_column(
        "user_progress",
        sa.Column("material_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_user_progress_item_type",
        "user_progress",
        ["item_type"],
    )
    op.create_foreign_key(
        "fk_user_progress_material_id_materials",
        source_table="user_progress",
        referent_table="materials",
        local_cols=["material_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_user_material_progress",
        "user_progress",
        ["user_id", "material_id"],
    )
    op.create_check_constraint(
        "ck_user_progress_item_type",
        "user_progress",
        "(item_type = 'roadmap' AND roadmap_id IS NOT NULL AND material_id IS NULL)"
        " OR (item_type = 'material' AND material_id IS NOT NULL AND roadmap_id IS NULL)",
    )

    op.execute(
        "UPDATE user_progress SET item_type = 'roadmap' WHERE item_type IS NULL"
    )


def downgrade() -> None:
    op.alter_column(
        "user_progress",
        "roadmap_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_constraint(
        "ck_user_progress_item_type",
        "user_progress",
        type_="check",
    )
    op.drop_constraint(
        "uq_user_material_progress",
        "user_progress",
        type_="unique",
    )
    op.drop_constraint(
        "fk_user_progress_material_id_materials",
        "user_progress",
        type_="foreignkey",
    )
    op.drop_index("ix_user_progress_item_type", table_name="user_progress")
    op.drop_column("user_progress", "material_id")
    op.drop_column("user_progress", "item_type")

    bind = op.get_bind()
    progress_item_type.drop(bind, checkfirst=True)

