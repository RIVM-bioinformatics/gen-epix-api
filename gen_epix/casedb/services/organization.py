from typing import Any

from gen_epix.casedb.domain import model
from gen_epix.commondb.services import OrganizationService as CommonOrganizationService


class OrganizationService(CommonOrganizationService):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            user_invitation_constraints_class=model.UserInvitationConstraints,
        )
