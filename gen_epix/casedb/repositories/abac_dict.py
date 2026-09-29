"""Provide casedb dictionary persistence behavior for ABAC policy data."""

from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import DictRepository


class AbacDictRepository(DictRepository, BaseAbacRepository):
    """Provide dictionary-backed persistence for casedb ABAC policy data."""

    pass
