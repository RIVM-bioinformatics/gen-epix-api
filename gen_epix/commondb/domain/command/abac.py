"""Define commondb commands for organization-administration policies."""

from typing import ClassVar

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD


class RetrieveOrganizationsUnderAdminCommand(Command):
    """Retrieve IDs of organizations administered by the executing user."""

    pass


# CRUD


class OrganizationAdminPolicyCrudCommand(CrudCommand):
    """Manage policies that grant organization-administration rights to users."""

    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy
