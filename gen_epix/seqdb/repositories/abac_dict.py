"""Provide seqdb persistence behavior for repositories.abac_dict."""

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.seqdb.domain.repository import BaseAbacRepository


class AbacDictRepository(DictRepository, BaseAbacRepository):
    """Provide dictionary-backed persistence for seqdb ABAC data."""

    pass
