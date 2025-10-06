from collections.abc import Hashable
from typing import Any, Iterable, Type

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.model import Model
from gen_epix.commondb.repositories import (
    OrganizationSARepository as CommonOrganizationSARepository,
)
from gen_epix.commondb.repositories import sa_model
from gen_epix.fastapp import Entity


class OrganizationSARepository(CommonOrganizationSARepository):
    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[Type[Model], dict[Hashable, Model]],
        **kwargs: Any,
    ):
        super().__init__(
            entities,
            db,
            **kwargs,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            sa_user_class=sa_model.User,
            sa_user_invitation_class=sa_model.UserInvitation,
        )
