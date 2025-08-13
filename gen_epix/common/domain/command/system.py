from typing import ClassVar

import gen_epix.common.domain.model.system as model
from gen_epix.common.domain.command.base import Command, CrudCommand

# Non-CRUD commands


class RetrieveOutagesCommand(Command):
    pass


# CRUD commands


class OutageCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Outage
