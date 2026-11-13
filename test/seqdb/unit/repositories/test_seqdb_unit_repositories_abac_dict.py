from gen_epix.fastapp.repositories import DictRepository
from gen_epix.seqdb.domain.repository import BaseAbacRepository
from gen_epix.seqdb.repositories.abac_dict import AbacDictRepository


def test_repository_combines_dict_storage_and_abac_contract() -> None:
    """Compose dictionary storage with the seqdb ABAC repository interface."""
    assert issubclass(AbacDictRepository, DictRepository)
    assert issubclass(AbacDictRepository, BaseAbacRepository)
    assert AbacDictRepository.__mro__.index(
        DictRepository
    ) < AbacDictRepository.__mro__.index(BaseAbacRepository)
