"""Test the OmopDB ABAC service specialization."""

from gen_epix.omopdb.services.abac import AbacService


def test_cache_invalidation_commands_are_empty():
    """Verify OmopDB does not register cache invalidation commands."""
    assert AbacService.CACHE_INVALIDATION_COMMANDS == ()
