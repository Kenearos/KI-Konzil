"""Create council_runs table for persistent run history

Revision ID: 002
Revises: 001
Create Date: 2026-02-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "council_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("blueprint_id", sa.String(36), nullable=True),
        sa.Column("input_topic", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "execution_mode",
            sa.String(20),
            nullable=False,
            server_default="auto-pilot",
        ),
        sa.Column("final_draft", sa.Text(), nullable=True),
        sa.Column("critic_score", sa.Float(), nullable=True),
        sa.Column("iteration_count", sa.Integer(), nullable=True),
        sa.Column("active_node", sa.String(255), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("council_runs")
