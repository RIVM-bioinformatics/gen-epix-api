"""Define commondb commands for outages, licenses, and feature flags."""

from typing import ClassVar

import gen_epix.commondb.domain.model.system as model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD commands


class RetrieveOutagesCommand(Command):
    """Represents a request to retrieve current and scheduled system outages for public availability status."""

    pass


class RetrieveLicensesCommand(Command):
    """Represents a request to retrieve license metadata for installed application packages."""

    pass


class RetrieveFeatureFlagsCommand(Command):
    """Represents a request to retrieve feature flags exposed by the composed application."""

    pass


# CRUD commands


class OutageCrudCommand(CrudCommand):
    """Represents a request to manage persisted system outage windows and visibility information."""

    MODEL_CLASS: ClassVar = model.Outage
