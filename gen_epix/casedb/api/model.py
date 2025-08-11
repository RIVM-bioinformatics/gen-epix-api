from enum import Enum

from gen_epix.casedb.domain import DOMAIN

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc]
