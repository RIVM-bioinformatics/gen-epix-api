"""Add the system.upload_job table for background upload jobs.

The Alembic ``upgrade`` and ``downgrade`` functions create and drop the table
that tracks uploads submitted for background processing.

Revision ID: 16cce2d4967f
Revises: 4c60bf3993c5
Create Date: 2026-11-26 12:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

import gen_epix.fastapp.repositories.sa.util

# revision identifiers, used by Alembic.
revision = "16cce2d4967f"
down_revision = "4c60bf3993c5"
branch_labels = None
depends_on = None


def _utc_timestamp_default_sql() -> str:
    """Return the dialect-specific SQL expression for the current UTC time."""
    dialect_name = op.get_bind().dialect.name
    expressions = {
        "mssql": "GETUTCDATE()",
        "postgresql": "TIMEZONE('utc', CURRENT_TIMESTAMP)",
        "sqlite": "CURRENT_TIMESTAMP",
    }
    return expressions.get(dialect_name, "CURRENT_TIMESTAMP")


def upgrade() -> None:
    """Create the upload job table."""
    default_utc_timestamp_sql = _utc_timestamp_default_sql()
    op.create_table(
        "upload_job",
        sa.Column("user_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("job_type", sa.Unicode(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("QUEUED", "RUNNING", "SUCCEEDED", "FAILED", name="uploadjobstatus"),
            nullable=False,
        ),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(), nullable=True),
        sa.Column("worker_id", sa.Unicode(length=255), nullable=True),
        sa.Column("result_json", sa.UnicodeText(), nullable=True),
        sa.Column("error_status_code", sa.Integer(), nullable=True),
        sa.Column("error_detail", sa.Unicode(length=2000), nullable=True),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "created_at",
            gen_epix.fastapp.repositories.sa.util.UTCDateTime(),
            server_default=sa.text(default_utc_timestamp_sql),
            nullable=False,
        ),
        sa.Column(
            "modified_at",
            gen_epix.fastapp.repositories.sa.util.UTCDateTime(),
            server_default=sa.text(default_utc_timestamp_sql),
            nullable=False,
        ),
        sa.Column("modified_by", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="system",
    )


def downgrade() -> None:
    """Drop the upload job table."""
    op.drop_table("upload_job", schema="system")
