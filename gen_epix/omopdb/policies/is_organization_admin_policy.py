"""Configure the shared organization-administrator policy for OmopDB roles."""

from typing import Any

from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies import (
    IsOrganizationAdminPolicy as CommonIsOrganizationAdminPolicy,
)


class IsOrganizationAdminPolicy(CommonIsOrganizationAdminPolicy):
    """Encapsulates organization-administrator checks using the OmopDB role map."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Initialize the policy with OmopDB users and role mappings."""
        super().__init__(
            abac_service,
            **kwargs,
        )
