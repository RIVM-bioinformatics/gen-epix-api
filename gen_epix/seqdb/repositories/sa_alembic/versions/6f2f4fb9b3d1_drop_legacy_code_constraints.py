"""drop legacy SeqDB code unique constraints

Revision ID: 6f2f4fb9b3d1
Revises: 973d81851aeb
Create Date: 2026-08-24
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6f2f4fb9b3d1"
down_revision = "973d81851aeb"
branch_labels = None
depends_on = None


def _drop_legacy_unique_constraint(table_name: str, constraint_name: str) -> None:
    """Drop a legacy unique constraint or index if it is present on SQL Server."""
    connection = op.get_bind()
    if connection.dialect.name != "mssql":
        return

    object_name = f"[seq].[{table_name}]"
    constraint_exists = connection.execute(
        sa.text(
            "SELECT 1 FROM sys.key_constraints "
            "WHERE parent_object_id = OBJECT_ID(:object_name) "
            "AND name = :constraint_name"
        ),
        {"object_name": object_name, "constraint_name": constraint_name},
    ).scalar()
    if constraint_exists:
        op.drop_constraint(
            constraint_name, table_name, schema="seq", type_="unique"
        )
        return

    index_exists = connection.execute(
        sa.text(
            "SELECT 1 FROM sys.indexes "
            "WHERE object_id = OBJECT_ID(:object_name) "
            "AND name = :constraint_name AND is_unique = 1"
        ),
        {"object_name": object_name, "constraint_name": constraint_name},
    ).scalar()
    if index_exists:
        op.drop_index(constraint_name, table_name=table_name, schema="seq")


def upgrade() -> None:
    """Remove LSP-3497 legacy uniqueness for operational sequence entities."""
    _drop_legacy_unique_constraint("sample", "uq_sample_code")
    _drop_legacy_unique_constraint("read_set", "uq_read_set_code")
    _drop_legacy_unique_constraint("seq", "uq_seq_code")


def downgrade() -> None:
    """Do not recreate constraints: duplicate codes may already exist."""
