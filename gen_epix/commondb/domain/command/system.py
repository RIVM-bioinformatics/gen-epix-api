"""Define commondb commands for outages, licenses, and feature flags."""

from typing import ClassVar

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD commands


class DeleteAllOperationalDataCommand(Command):
    """Represents a request to delete all operational data in one application.

    This is intended as a maintenance operation or for use during development, and
    should only be executable under specific conditions. Non-operational data are
    not affected.
    """

    SORTED_OPERATIONAL_DATA_MODEL_CLASSES: ClassVar[list[type[model.ModelNoId]]] = (
        []
    )  # Persistable domain models for operational data, in deletion order so that foreign-key constraints do not fail (i.e. reverse DAG order on links)


class DeleteAllRefDataCommand(Command):
    """Request deletion of application reference data after ops data reset.

    Application domains subclass this command and provide their reference-data
    models in deletion order. The shared command deliberately has no model list;
    the composed application's domain determines the concrete command and model
    set.
    """

    SORTED_REF_DATA_MODEL_CLASSES: ClassVar[list[type[model.ModelNoId]]] = []


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
