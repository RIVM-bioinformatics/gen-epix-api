"""Provide the SQLAlchemy repository implementation for commondb system models."""

from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import SARepository


class SystemSARepository(SARepository, BaseSystemRepository):
    """Store system records using FastApp's SQLAlchemy repository backend."""

    pass
