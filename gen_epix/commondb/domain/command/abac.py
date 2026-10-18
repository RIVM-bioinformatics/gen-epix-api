"""Define commands for commondb organization-administration access control.

`RetrieveOrganizationsUnderAdminCommand` requests administered organization IDs,
and `OrganizationAdminPolicyCrudCommand` manages the corresponding policies.
Both specialize shared command types used by application dispatch.
"""

from typing import ClassVar

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD


class RetrieveOrganizationsUnderAdminCommand(Command):
    """Represents a request to retrieve IDs of organizations administered by the executing user."""

    pass


# CRUD


class OrganizationAdminPolicyCrudCommand(CrudCommand):
    """Represents a request to manage policies that grant organization-administration rights to users."""

    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy
