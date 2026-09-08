"""SQLAlchemy metadata managed by commondb migrations."""

import sqlalchemy as sa

from gen_epix.commondb.repositories import sa_model


def _get_target_metadata() -> tuple[sa.MetaData, ...]:
    metadata_by_id = {
        id(candidate.metadata): candidate.metadata
        for candidate in vars(sa_model).values()
        if isinstance(candidate, type)
        and isinstance(getattr(candidate, "metadata", None), sa.MetaData)
    }
    return tuple(metadata_by_id.values())


target_metadata = _get_target_metadata()
