"""Implement SeqDB authorization policy behavior for policies.is_organization_admin_policy."""

from typing import Any

from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies import (
    IsOrganizationAdminPolicy as CommonIsOrganizationAdminPolicy,
)
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.policy import COMMON_ROLE_MAP


class IsOrganizationAdminPolicy(CommonIsOrganizationAdminPolicy):

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            role_map=COMMON_ROLE_MAP,  # type: ignore[arg-type]
            user_class=model.User,
            **kwargs,
        )
