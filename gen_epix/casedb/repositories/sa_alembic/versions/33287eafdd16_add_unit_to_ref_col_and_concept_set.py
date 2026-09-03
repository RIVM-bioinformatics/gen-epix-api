"""add unit to ref_col and concept_set

Revision ID: 33287eafdd16
Revises: bbc386e12a58
Create Date: 2026-09-03 11:32:21.530165
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "33287eafdd16"
down_revision = "bbc386e12a58"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    op.drop_column("concept_set", "unit", schema="ontology")
    op.drop_column("ref_col", "unit", schema="case")
