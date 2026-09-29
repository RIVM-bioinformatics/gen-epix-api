"""Configure shared user-read policy behavior for OmopDB roles and commands."""

from typing import Any

from gen_epix.commondb.policies import ReadUserPolicy as CommonReadUserPolicy
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.policy import COMMON_ROLE_MAP
from gen_epix.omopdb.domain.service import BaseAbacService


class ReadUserPolicy(CommonReadUserPolicy):
    """Encapsulates shared user-read checks with OmopDB role and command mappings."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Initialize the user-read policy with OmopDB dependencies."""
        super().__init__(
            abac_service,
            role_map=COMMON_ROLE_MAP,  # type: ignore[arg-type]
            organization_admin_policy_crud_command_class=command.OrganizationAdminPolicyCrudCommand,
            **kwargs,
        )
