"""Expose distinct SQLAlchemy metadata collections to commondb Alembic migrations."""

import sqlalchemy as sa

from gen_epix.commondb.repositories import sa_model


def _get_target_metadata() -> tuple[sa.MetaData, ...]:
    """Collect metadata objects exposed by commondb SQLAlchemy model classes.

    Returns:
        Distinct metadata objects in the order their classes are exported.
    """
    metadata_by_id = {
        id(candidate.metadata): candidate.metadata
        for candidate in vars(sa_model).values()
        if isinstance(candidate, type)
        and isinstance(getattr(candidate, "metadata", None), sa.MetaData)
    }
    return tuple(metadata_by_id.values())


target_metadata = _get_target_metadata()
