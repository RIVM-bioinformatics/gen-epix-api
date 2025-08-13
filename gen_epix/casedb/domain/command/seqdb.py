from typing import ClassVar
from uuid import UUID

from gen_epix.casedb.domain import enum
from gen_epix.common.domain.command import Command

# Non-CRUD


class RetrieveGeneticSequenceByIdCommand(Command):

    seq_ids: list[UUID]


# CRUD
