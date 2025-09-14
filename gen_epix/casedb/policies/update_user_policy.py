from typing import Any

from gen_epix.casedb.domain.policy import COMMON_ROLE_MAP
from gen_epix.casedb.domain.service import BaseAbacService
from gen_epix.commondb.policies import UpdateUserPolicy as CommonUpdateUserPolicy


class UpdateUserPolicy(CommonUpdateUserPolicy):
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
