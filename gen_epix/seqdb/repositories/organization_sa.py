from typing import Any

from sqlalchemy import Engine

from gen_epix.commondb.repositories import (
    OrganizationSARepository as CommonOrganizationSARepository,
)
from gen_epix.commondb.repositories import (
    sa_model,
)
from gen_epix.seqdb.domain import model


class OrganizationSARepository(CommonOrganizationSARepository):
    def __init__(
        self,
        engine: Engine,
        **kwargs: Any,
    ):
        super().__init__(
            engine,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            sa_user_class=sa_model.User,
            sa_user_invitation_class=sa_model.UserInvitation,
            **kwargs,
        )
