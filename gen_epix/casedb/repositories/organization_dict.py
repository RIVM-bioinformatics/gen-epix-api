from collections.abc import Hashable, Iterable
from typing import Any

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.model import Model
from gen_epix.commondb.repositories import \
    OrganizationDictRepository as CommonOrganizationDictRepository
from gen_epix.fastapp import Entity


class OrganizationDictRepository(CommonOrganizationDictRepository):
    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[type[Model], dict[Hashable, Model]],
        **kwargs: Any,
    ):
        super().__init__(
            entities,
            db,
            **kwargs,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
        )
