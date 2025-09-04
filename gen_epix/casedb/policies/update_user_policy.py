from typing import Any

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.common.policies import UpdateUserPolicy as CommonUpdateUserPolicy


class UpdateUserPolicy(CommonUpdateUserPolicy):
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
            **kwargs,
        )
