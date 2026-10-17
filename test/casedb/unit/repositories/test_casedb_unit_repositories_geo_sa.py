"""Test casedb SQLAlchemy geographic repository composition."""

from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.casedb.repositories import GeoSARepository as ExportedRepository
from gen_epix.casedb.repositories.geo_sa import GeoSARepository
from gen_epix.fastapp.repositories import SARepository


def test_repository_combines_sa_storage_and_geo_contract() -> None:
    """The repository is SQLAlchemy-backed and implements the geo contract."""
    assert issubclass(GeoSARepository, SARepository)
    assert issubclass(GeoSARepository, BaseGeoRepository)
    assert GeoSARepository.__mro__.index(SARepository) < GeoSARepository.__mro__.index(
        BaseGeoRepository
    )


def test_repository_is_exported_from_package() -> None:
    """The package export resolves to the module's repository class."""
    assert ExportedRepository is GeoSARepository
