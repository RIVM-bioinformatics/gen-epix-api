"""Test casedb dictionary geographic repository composition."""

from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.casedb.repositories import GeoDictRepository as ExportedRepository
from gen_epix.casedb.repositories.geo_dict import GeoDictRepository
from gen_epix.fastapp.repositories import DictRepository


def test_repository_combines_dict_storage_and_geo_contract() -> None:
    """The repository is dictionary-backed and implements the geo contract."""
    assert issubclass(GeoDictRepository, DictRepository)
    assert issubclass(GeoDictRepository, BaseGeoRepository)
    assert GeoDictRepository.__mro__.index(
        DictRepository
    ) < GeoDictRepository.__mro__.index(BaseGeoRepository)


def test_repository_is_exported_from_package() -> None:
    """The package export resolves to the module's repository class."""
    assert ExportedRepository is GeoDictRepository
