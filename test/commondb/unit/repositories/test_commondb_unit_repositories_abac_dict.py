"""Test commondb dictionary ABAC repository composition."""

from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.commondb.repositories import AbacDictRepository as ExportedRepository
from gen_epix.commondb.repositories.abac_dict import AbacDictRepository
from gen_epix.fastapp.repositories import DictRepository


def test_repository_combines_dict_storage_and_abac_contract() -> None:
    """The repository is a dictionary repository implementing the ABAC contract."""
    assert issubclass(AbacDictRepository, DictRepository)
    assert issubclass(AbacDictRepository, BaseAbacRepository)
    assert AbacDictRepository.__mro__.index(
        DictRepository
    ) < AbacDictRepository.__mro__.index(BaseAbacRepository)


def test_repository_is_exported_from_package() -> None:
    """The package export resolves to the module's repository class."""
    assert ExportedRepository is AbacDictRepository
