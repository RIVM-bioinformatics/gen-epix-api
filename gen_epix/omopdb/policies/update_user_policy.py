"""Configure shared user-update policy behavior for OmopDB roles."""

from typing import Any

from gen_epix.commondb.policies import UpdateUserPolicy as CommonUpdateUserPolicy
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.domain.policy import COMMON_ROLE_MAP
from gen_epix.omopdb.domain.service import BaseAbacService


class UpdateUserPolicy(CommonUpdateUserPolicy):
    """Apply shared user-update checks with OmopDB role and user mappings."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Initialize the user-update policy with OmopDB dependencies."""
        super().__init__(
            abac_service,
            role_map=COMMON_ROLE_MAP,  # type: ignore[arg-type]
            user_class=model.User,
            **kwargs,
        )
