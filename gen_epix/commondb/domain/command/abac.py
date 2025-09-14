from typing import ClassVar

import gen_epix.common.domain.model.abac as model
from gen_epix.common.domain.command.base import Command, CrudCommand

# Non-CRUD


class RetrieveOrganizationsUnderAdminCommand(Command):
    """
    Retrieve the ids of all the organizations under administration by the user
    executing the command.
    """

    pass


# CRUD


class OrganizationAdminPolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy
