"""Provide the SQLAlchemy repository implementation for commondb ABAC models."""

from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import SARepository


class AbacSARepository(SARepository, BaseAbacRepository):
    """Encapsulates storage of ABAC policy records using FastApp's SQLAlchemy repository backend."""

    pass
