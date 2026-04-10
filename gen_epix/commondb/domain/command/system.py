from typing import ClassVar

from pydantic import Field

import gen_epix.commondb.domain.model.system as model
from gen_epix.commondb.domain.command.base import Command, CrudCommand
from gen_epix.commondb.domain.enum import LogLevel

# Non-CRUD commands


class RetrieveOutagesCommand(Command):
    pass


class RetrieveLicensesCommand(Command):
    pass


class RetrieveFeatureFlagsCommand(Command):
    pass


class UpdateLogLevelCommand(Command):

    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="The log level to set for the application.",
    )


# CRUD commands


class OutageCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Outage
