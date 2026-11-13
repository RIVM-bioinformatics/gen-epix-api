"""Provide the SeqDB ABAC service specialization.

`AbacService` inherits shared policy and command behavior from `BaseAbacService`
while defining this application's cache-invalidation command set.
"""

from __future__ import annotations

from gen_epix.fastapp.model import Command
from gen_epix.seqdb.domain.service import BaseAbacService


class AbacService(BaseAbacService):
    """Encapsulates SeqDB's ABAC service specialization.

    It inherits policy and command handling from `BaseAbacService` and declares
    the command classes that trigger cache invalidation.
    """

    CACHE_INVALIDATION_COMMANDS: tuple[type[Command], ...] = tuple()
