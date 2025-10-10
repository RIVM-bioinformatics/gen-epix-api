from collections.abc import Hashable
from typing import Any, Iterable, Type

from gen_epix.commondb.repositories import (
    OrganizationDictRepository as CommonOrganizationDictRepository,
)
from gen_epix.fastapp import Entity
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.model import Model


class OrganizationDictRepository(CommonOrganizationDictRepository):
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
        )
