"""Test casedb SQLAlchemy ABAC repository composition."""

from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.casedb.repositories import AbacSARepository as ExportedRepository
from gen_epix.casedb.repositories.abac_sa import AbacSARepository
from gen_epix.fastapp.repositories import SARepository


def test_repository_combines_sa_storage_and_abac_contract() -> None:
    """The repository is a SQLAlchemy repository implementing the ABAC contract."""
    assert issubclass(AbacSARepository, SARepository)
    assert issubclass(AbacSARepository, BaseAbacRepository)
    assert AbacSARepository.__mro__.index(
        SARepository
    ) < AbacSARepository.__mro__.index(BaseAbacRepository)


def test_repository_is_exported_from_package() -> None:
    """The package export resolves to the module's repository class."""
    assert ExportedRepository is AbacSARepository
