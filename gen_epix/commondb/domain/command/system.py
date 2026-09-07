"""Define commondb commands for outages, licenses, and feature flags."""

from typing import ClassVar

import gen_epix.commondb.domain.model.system as model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD commands


class DeleteOperationalDataCommand(Command):
    """Represents a request to delete all operational data in one application.

    Only ROOT and APP_ADMIN may execute this maintenance operation, and only
    when ALLOW_DELETE_OPERATIONAL_DATA is enabled. Writers must be paused by
    the operator. Reference data, common organization data, and external files
    are retained. Each application supplies its own handler.
    """


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
