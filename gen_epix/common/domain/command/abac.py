from typing import ClassVar

import gen_epix.common.domain.model.abac as model
from gen_epix.common.domain.command.base import CrudCommand

# Non-CRUD


# CRUD


class OrganizationAdminPolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy
