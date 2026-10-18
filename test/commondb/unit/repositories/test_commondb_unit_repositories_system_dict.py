"""Check the concrete dictionary-backed repository for system records."""

from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.commondb.repositories.system_dict import SystemDictRepository
from gen_epix.fastapp.repositories import DictRepository


def test_create_repository_returns_system_dict_repository():
    """Return a repository implementing both the system and dictionary contracts."""
    repository = SystemDictRepository.create_repository()

    assert isinstance(repository, SystemDictRepository)
    assert isinstance(repository, DictRepository)
    assert isinstance(repository, BaseSystemRepository)
