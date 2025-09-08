from typing import Any

from gen_epix.casedb.domain import command, enum
from gen_epix.common.domain.service.abac import BaseAbacService
from gen_epix.common.policies import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)


class ReadSelfResultsOnlyPolicy(CommonReadSelfResultsOnlyPolicy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            exempt_roles=enum.RoleSet.GE_ORG_ADMIN.value,  # type: ignore[arg-type]
            **kwargs,
        )
        self.id_attr_by_command_class = {
            command.UserCrudCommand: "id",
            command.UserInvitationCrudCommand: "invited_by_user_id",
            command.UserAccessCasePolicyCrudCommand: "user_id",
            command.UserShareCasePolicyCrudCommand: "user_id",
        }
