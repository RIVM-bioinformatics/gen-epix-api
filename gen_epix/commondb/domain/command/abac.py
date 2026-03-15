from typing import ClassVar

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD


class RetrieveOrganizationsUnderAdminCommand(Command):
    """
    Retrieve the ids of all the organizations under administration by the user
    executing the command.
    """

    pass


# CRUD


class OrganizationAdminPolicyCrudCommand(CrudCommand):
    """Manage policies that define which organizations an administrator can manage across the platform."""

    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy
