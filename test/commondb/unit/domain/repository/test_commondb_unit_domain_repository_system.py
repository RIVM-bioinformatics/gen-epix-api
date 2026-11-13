"""Test the commondb system repository interface."""

from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp import BaseRepository


def test_base_system_repository_extends_base_repository() -> None:
    """Keep the system repository within the FastApp repository contract."""
    assert issubclass(BaseSystemRepository, BaseRepository)
