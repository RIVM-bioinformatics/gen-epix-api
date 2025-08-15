from typing import Any, Hashable, Iterable, Type

from gen_epix.common.domain import model
from gen_epix.common.domain.model import Model
from gen_epix.common.domain.repository.organization import BaseOrganizationRepository
from gen_epix.fastapp import Entity, exc
from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class OrganizationDictRepository(DictRepository, BaseOrganizationRepository):
    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[Type[Model], dict[Hashable, Model]],
        user_class: type[model.User] = model.User,
        user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
        **kwargs: Any,
    ):
        BaseOrganizationRepository.__init__(
            self, user_class=user_class, user_invitation_class=user_invitation_class
        )
        DictRepository.__init__(self, entities, db, **kwargs)

    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        if user_key is None:
            return False
        for user in self._db[self.user_class].values():
            assert isinstance(user, self.user_class)
            if user.email == user_key:
                return True
        return False

    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        for user in self._db[self.user_class].values():
            assert isinstance(user, self.user_class)
            if user.email == user_key.lower():
                return user
        raise exc.NoResultsError()
