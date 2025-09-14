from typing import ClassVar

import gen_epix.commondb.domain.command as common_command
from gen_epix.seqdb.domain import model


class OrganizationAdminPolicyCrudCommand(
    common_command.OrganizationAdminPolicyCrudCommand
):
    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy
