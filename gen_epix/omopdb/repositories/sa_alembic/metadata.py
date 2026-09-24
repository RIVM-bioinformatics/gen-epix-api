"""SQLAlchemy metadata managed by omopdb migrations, including common models."""

import sqlalchemy as sa

from gen_epix.omopdb.repositories import sa_model


def _get_target_metadata() -> tuple[sa.MetaData, ...]:
    metadata_by_id = {
        id(candidate.metadata): candidate.metadata
        for candidate in vars(sa_model).values()
        if isinstance(candidate, type)
        and isinstance(getattr(candidate, "metadata", None), sa.MetaData)
    }
    return tuple(metadata_by_id.values())


target_metadata = _get_target_metadata()

# SQL Server makes every primary-key column NOT NULL, even when the legacy
# domain-model annotation resulted in nullable=True on the mapped column. Use
# SQL Server's actual invariant for migration comparison so Alembic does not
# propose an invalid ALTER COLUMN for every OMOP primary key.
for metadata in target_metadata:
    for table in metadata.tables.values():
        for column in table.primary_key.columns:
            column.nullable = False
