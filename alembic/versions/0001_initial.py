"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-03
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("number", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=256), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_table(
        "family_files",
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("status", sa.String(length=128), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("version_id", sa.Uuid(), nullable=True),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("path"),
    )
    op.create_table(
        "family_types",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["family_files.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "spec_param_sets",
        sa.Column("ADSK_Наименование", sa.String(length=1024), nullable=True),
        sa.Column("ADSK_Количество", sa.Integer(), nullable=True),
        sa.Column("ADSK_Марка", sa.String(length=256), nullable=True),
        sa.Column("ADSK_Код изделия", sa.String(length=256), nullable=True),
        sa.Column("ADSK_Завод-изготовитель", sa.String(length=128), nullable=True),
        sa.Column("ADSK_Техническая характеристика", sa.String(length=1024), nullable=True),
        sa.Column("ADSK_Единица измерения", sa.String(length=128), nullable=True),
        sa.Column("ADSK_Масса", sa.String(length=128), nullable=True),
        sa.Column("ADSK_Версия семейства", sa.String(length=256), nullable=True),
        sa.Column("ADSK_URL документации изделия", sa.String(length=256), nullable=True),
        sa.Column("type_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["type_id"], ["family_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("spec_param_sets")
    op.drop_table("family_types")
    op.drop_table("family_files")
    op.drop_table("categories")
