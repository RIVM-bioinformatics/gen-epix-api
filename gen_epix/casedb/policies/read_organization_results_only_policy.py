from typing import Any

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.service import BaseAbacService
from gen_epix.commondb.policies import \
    ReadOrganizationResultsOnlyPolicy as \
    CommonReadOrganizationResultsOnlyPolicy


class ReadOrganizationResultsOnlyPolicy(CommonReadOrganizationResultsOnlyPolicy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            **kwargs,
        )
        self.has_organization_id_attr_command_classes.update(
            {
                command.OrganizationAccessCasePolicyCrudCommand,
                command.OrganizationShareCasePolicyCrudCommand,
            }
        )
        self.has_user_id_attr_command_classes.update(
            {
                command.UserAccessCasePolicyCrudCommand,
                command.UserShareCasePolicyCrudCommand,
            }
        )
