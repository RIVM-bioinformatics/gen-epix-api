"""Test the SQLAlchemy-backed OmopDB ABAC repository adapter."""

from gen_epix.fastapp.repositories import SARepository
from gen_epix.omopdb.domain.repository import BaseAbacRepository
from gen_epix.omopdb.repositories.abac_sa import AbacSARepository


def test_abac_sa_repository_implements_omopdb_and_sqlalchemy_contracts() -> None:
    """Verify that the adapter implements both repository contracts."""
    assert issubclass(AbacSARepository, SARepository)
    assert issubclass(AbacSARepository, BaseAbacRepository)
