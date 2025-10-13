from typing import Any

from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.policy import COMMON_ROLE_MAP


class ReadSelfResultsOnlyPolicy(CommonReadSelfResultsOnlyPolicy):
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
        self.id_attr_by_command_class = {
            command.UserCrudCommand: "id",
            command.UserInvitationCrudCommand: "invited_by_user_id",
        }
