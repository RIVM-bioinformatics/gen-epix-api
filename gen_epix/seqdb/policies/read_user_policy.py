"""Implement SeqDB authorization policy behavior for policies.read_user_policy."""

from typing import Any

from gen_epix.commondb.policies import ReadUserPolicy as CommonReadUserPolicy
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.policy import COMMON_ROLE_MAP
from gen_epix.seqdb.domain.service import BaseAbacService


class ReadUserPolicy(CommonReadUserPolicy):
    """Authorize user reads with SeqDB roles and organization-admin commands."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Configure the shared policy with SeqDB authorization dependencies."""
        super().__init__(
            abac_service,
            role_map=COMMON_ROLE_MAP,  # type: ignore[arg-type]
            organization_admin_policy_crud_command_class=command.OrganizationAdminPolicyCrudCommand,
            **kwargs,
        )
