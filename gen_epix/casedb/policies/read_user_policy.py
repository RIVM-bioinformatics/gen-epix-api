from typing import Any

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.policy import COMMON_ROLE_MAP
from gen_epix.casedb.domain.service import BaseAbacService
from gen_epix.commondb.policies import ReadUserPolicy as CommonReadUserPolicy


class ReadUserPolicy(CommonReadUserPolicy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            role_map=COMMON_ROLE_MAP,  # type: ignore[arg-type]
            organization_admin_policy_crud_command_class=command.OrganizationAdminPolicyCrudCommand,
            **kwargs,
        )
