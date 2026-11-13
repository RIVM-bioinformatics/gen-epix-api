"""Expose SQLAlchemy metadata registries to casedb Alembic migrations.

`target_metadata` contains the distinct metadata registries exposed by casedb's
SQLAlchemy models. Alembic uses them for offline and online migration
autogeneration.
"""

import sqlalchemy as sa

from gen_epix.casedb.repositories import sa_model


def _get_target_metadata() -> tuple[sa.MetaData, ...]:
    """Collect distinct metadata registries from exported SQLAlchemy models.

    Returns:
        The registries in the order their model classes appear in `sa_model`.
    """
    metadata_by_id = {
        id(candidate.metadata): candidate.metadata
        for candidate in vars(sa_model).values()
        if isinstance(candidate, type)
        and isinstance(getattr(candidate, "metadata", None), sa.MetaData)
    }
    return tuple(metadata_by_id.values())


target_metadata = _get_target_metadata()
