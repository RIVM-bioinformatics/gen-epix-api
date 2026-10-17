from inspect import isabstract

from gen_epix.commondb.domain.repository.abac import BaseAbacRepository
from gen_epix.fastapp import BaseRepository


def test_base_abac_repository_preserves_abstract_repository_contract() -> None:
    assert issubclass(BaseAbacRepository, BaseRepository)
    assert isabstract(BaseAbacRepository)
