from typing import Any

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.policy import COMMON_ROLE_MAP
from gen_epix.casedb.domain.service import BaseAbacService
from gen_epix.commondb.policies import (
    ReadOrganizationResultsOnlyPolicy as CommonReadOrganizationResultsOnlyPolicy,
)


class ReadOrganizationResultsOnlyPolicy(CommonReadOrganizationResultsOnlyPolicy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            role_map=COMMON_ROLE_MAP,  # type: ignore[arg-type]
            **kwargs,
        )
        self.user_crud_command_class = command.UserCrudCommand
        self.has_organization_id_attr_command_classes = {
            command.UserCrudCommand,
            command.OrganizationAdminPolicyCrudCommand,
            command.OrganizationAccessCasePolicyCrudCommand,
            command.OrganizationShareCasePolicyCrudCommand,
            command.UserInvitationCrudCommand,
        }
        self.has_user_id_attr_command_classes = {
            command.UserAccessCasePolicyCrudCommand,
            command.UserShareCasePolicyCrudCommand,
        }
