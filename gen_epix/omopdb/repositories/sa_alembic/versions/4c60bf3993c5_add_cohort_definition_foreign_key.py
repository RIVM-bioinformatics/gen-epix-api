"""Add the cohort definition foreign key.

Revision ID: 4c60bf3993c5
Revises: 252f23d99c89
Create Date: 2026-09-02
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "4c60bf3993c5"
down_revision = "252f23d99c89"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_cohort_cohort_definition_id",
        "cohort",
        "cohort_definition",
        ["cohort_definition_id"],
        ["cohort_definition_id"],
        source_schema="omop",
        referent_schema="omop",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_cohort_cohort_definition_id",
        "cohort",
        schema="omop",
        type_="foreignkey",
    )
