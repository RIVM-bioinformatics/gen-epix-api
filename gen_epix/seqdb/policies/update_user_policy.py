from typing import Any

from gen_epix.commondb.policies import UpdateUserPolicy as CommonUpdateUserPolicy
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.policy import COMMON_ROLE_MAP
from gen_epix.seqdb.domain.service import BaseAbacService


class UpdateUserPolicy(CommonUpdateUserPolicy):
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
