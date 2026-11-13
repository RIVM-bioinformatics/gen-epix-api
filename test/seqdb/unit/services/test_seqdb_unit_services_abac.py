"""Verify SeqDB's ABAC service cache-invalidation configuration."""

from gen_epix.seqdb.services.abac import AbacService


def test_cache_invalidation_commands_are_empty() -> None:
    """The SeqDB specialization registers no cache invalidation commands."""
    assert not AbacService.CACHE_INVALIDATION_COMMANDS
