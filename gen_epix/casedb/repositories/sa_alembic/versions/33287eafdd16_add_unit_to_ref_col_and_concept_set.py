"""Add and remove unit columns for reference columns and concept sets.

The Alembic ``upgrade`` and ``downgrade`` functions manage nullable unit enum
columns on ``case.ref_col`` and ``ontology.concept_set``.

Revision ID: 33287eafdd16
Revises: bbc386e12a58
Create Date: 2026-09-03 11:32:21.530165
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "33287eafdd16"
down_revision = "bbc386e12a58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add unit columns to reference columns and concept sets."""
    op.add_column(
        "ref_col",
        sa.Column(
            "unit",
            sa.Enum(
                "SECOND",
                "MINUTE",
                "HOUR",
                "DAY",
                "WEEK",
                "MONTH",
                "QUARTER",
                "YEAR",
                "BASE_PAIR",
                "DOSE",
                "OTHER",
                name="unit",
            ),
            nullable=True,
        ),
        schema="case",
    )
    op.add_column(
        "concept_set",
        sa.Column(
            "unit",
            sa.Enum(
                "SECOND",
                "MINUTE",
                "HOUR",
                "DAY",
                "WEEK",
                "MONTH",
                "QUARTER",
                "YEAR",
                "BASE_PAIR",
                "DOSE",
                "OTHER",
                name="unit",
            ),
            nullable=True,
        ),
        schema="ontology",
    )


def downgrade() -> None:
    """Remove the unit columns from reference columns and concept sets."""
    op.drop_column("concept_set", "unit", schema="ontology")
    op.drop_column("ref_col", "unit", schema="case")
