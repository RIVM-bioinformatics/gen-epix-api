from __future__ import annotations

from gen_epix.fastapp.model import Command
from gen_epix.seqdb.domain.service import BaseAbacService


class AbacService(BaseAbacService):
    CACHE_INVALIDATION_COMMANDS: tuple[type[Command], ...] = tuple()
