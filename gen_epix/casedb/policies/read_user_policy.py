from typing import Any

from gen_epix.casedb.domain import command, enum
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.commondb.policies import ReadUserPolicy as CommonReadUserPolicy


class ReadUserPolicy(CommonReadUserPolicy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            root_role=enum.Role.ROOT,
            app_admin_roles=enum.RoleSet.GE_APP_ADMIN.value,  # type:ignore[arg-type]
            org_admin_roles=enum.RoleSet.GE_ORG_ADMIN.value,  # type:ignore[arg-type]
            organization_admin_policy_crud_command_class=command.OrganizationAdminPolicyCrudCommand,
            **kwargs,
        )
