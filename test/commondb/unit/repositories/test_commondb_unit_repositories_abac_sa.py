from gen_epix.commondb.domain.repository.abac import BaseAbacRepository
from gen_epix.commondb.repositories.abac_sa import AbacSARepository
from gen_epix.fastapp.repositories import SARepository


def test_abac_sa_repository_uses_sa_backend_and_abac_contract() -> None:
    assert AbacSARepository.__bases__ == (SARepository, BaseAbacRepository)
