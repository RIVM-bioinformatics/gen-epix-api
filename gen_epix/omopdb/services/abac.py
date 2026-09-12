"""OmopDB attribute-based access service specialization."""

from __future__ import annotations

from gen_epix.fastapp.model import Command
from gen_epix.omopdb.domain.service import BaseAbacService


class AbacService(BaseAbacService):
    """Encapsulates the OmopDB ABAC service with no extra cache invalidation commands."""

    CACHE_INVALIDATION_COMMANDS: tuple[type[Command], ...] = tuple()
