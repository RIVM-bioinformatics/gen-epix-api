"""Verify the SQLAlchemy-backed system repository's declared contracts."""

from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.commondb.repositories.system_sa import SystemSARepository
from gen_epix.fastapp.repositories import SARepository


def test_system_sa_repository_implements_system_contract_with_sqlalchemy_backend():
    """Verify the repository combines the system and SQLAlchemy contracts."""
    assert issubclass(SystemSARepository, SARepository)
    assert issubclass(SystemSARepository, BaseSystemRepository)
