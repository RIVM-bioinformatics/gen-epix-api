from __future__ import annotations

from typing import Type

from gen_epix.fastapp.model import Command
from gen_epix.seqdb.domain.service import BaseAbacService


class AbacService(BaseAbacService):
    CACHE_INVALIDATION_COMMANDS: tuple[Type[Command], ...] = tuple()
