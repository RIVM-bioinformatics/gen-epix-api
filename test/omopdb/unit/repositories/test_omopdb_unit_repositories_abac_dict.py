"""Test the dictionary-backed OmopDB ABAC repository adapter."""

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.omopdb.domain.repository import BaseAbacRepository
from gen_epix.omopdb.repositories.abac_dict import AbacDictRepository


def test_abac_dict_repository_implements_omopdb_and_dictionary_contracts() -> None:
    """Verify that the adapter implements both repository contracts."""
    assert issubclass(AbacDictRepository, DictRepository)
    assert issubclass(AbacDictRepository, BaseAbacRepository)
