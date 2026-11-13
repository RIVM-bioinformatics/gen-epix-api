"""Define shared commondb commands for system-level operations.

The public types cover operational and reference-data resets, outage CRUD, and
retrieval of outage, license, and feature-flag metadata. They are dispatched
through the application layer; transport and persistence remain outside this
module.
"""

from typing import ClassVar

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD commands


class DeleteAllOperationalDataCommand(Command):
    """Represents a request to execute deletion of one application's operational data.

    This is intended as a maintenance operation or for use during development, and
    should only be executable under specific conditions. Non-operational data are
    not affected.
    """

    SORTED_OPERATIONAL_DATA_MODEL_CLASSES: ClassVar[list[type[model.ModelNoId]]] = (
        []
    )  # Persistable domain models for operational data, in deletion order so that foreign-key constraints do not fail (i.e. reverse DAG order on links)


class DeleteAllRefDataCommand(Command):
    """Represents a request to execute deletion of application reference data.

    Application domains subclass this command and provide their reference-data
    models in deletion order after the operational-data reset. The shared command
    deliberately has no model list; application composition determines the
    concrete command and model set.
    """

    SORTED_REF_DATA_MODEL_CLASSES: ClassVar[list[type[model.ModelNoId]]] = []


class RetrieveOutagesCommand(Command):
    """Represents a request to execute retrieval of system outage information."""

    pass


class RetrieveLicensesCommand(Command):
    """Represents a request to execute retrieval of installed-package licenses."""

    pass


class RetrieveFeatureFlagsCommand(Command):
    """Represents a request to execute retrieval of composed-application flags."""

    pass


# CRUD commands


class OutageCrudCommand(CrudCommand):
    """Represents a request to execute CRUD operations on system outage windows."""

    MODEL_CLASS: ClassVar = model.Outage
