"""Provide seqdb persistence behavior for repositories.abac_sa."""

from gen_epix.fastapp.repositories import SARepository
from gen_epix.seqdb.domain.repository import BaseAbacRepository


class AbacSARepository(SARepository, BaseAbacRepository):
    """Provide SQLAlchemy-backed persistence for seqdb ABAC data."""

    pass
