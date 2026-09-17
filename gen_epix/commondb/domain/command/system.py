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
    )  # Persistable domain models for operational data, in order of deletion so that constraints do not fail (i.e. DAG sort order on links)


class DeleteAllRefDataCommand(Command):
    """Represents a request to delete all data except users and organizations.

    Deletes all persistable domain data (operational and reference data such as
    cases, case sets, sequences, ontology, and geo data) while preserving the
    identity and access-control backbone: users, organizations, and everything
    they depend on. Preservation is expressed as a set of service-type values;
    every persistable model whose service type is not preserved is deleted in
    reverse DAG order so foreign-key constraints do not fail.

    This is intended as a maintenance operation or for use during development, and
    should only be executable under specific conditions.
    """

    PRESERVED_SERVICE_TYPE_VALUES: ClassVar[frozenset[str]] = frozenset(
        {"AUTH", "ORGANIZATION", "RBAC"}
    )  # Service-type values whose persistable models are preserved (identity/access backbone)


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
