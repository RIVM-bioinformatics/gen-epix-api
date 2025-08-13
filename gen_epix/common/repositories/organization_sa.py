from typing import Any, Type

from sqlalchemy import Engine, select

from gen_epix.common.domain import model
from gen_epix.common.domain.repository.organization import BaseOrganizationRepository
from gen_epix.common.repositories import sa_model
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation, exc
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork


class OrganizationSARepository(SARepository, BaseOrganizationRepository):
    def __init__(
        self,
        engine: Engine,
        user_class: Type[model.User] = model.User,
        user_invitation_class: Type[model.UserInvitation] = model.UserInvitation,
        sa_user_class: Type = sa_model.UserMixin,
        sa_user_invitation_class: Type = sa_model.UserInvitationMixin,
        **kwargs: Any,
    ):
        self.sa_user_class = sa_user_class
        self.sa_user_invitation_class = sa_user_invitation_class
        BaseOrganizationRepository.__init__(
            self, user_class=user_class, user_invitation_class=user_invitation_class
        )
        SARepository.__init__(self, engine, **kwargs)

    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        if user_key is None:
            return False
        assert isinstance(uow, SAUnitOfWork)
        user_row = uow.session.execute(
            select(self.sa_user_class.id).where(self.user_class.email == user_key)
        ).all()
        return True if user_row else False

    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        # TODO: add filter to crud method instead of retrieving all users
        users: list[model.User] = self.crud(  # type:ignore[assignment]
            uow,
            None,
            self.user_class,
            None,
            None,
            CrudOperation.READ_ALL,
        )
        for user in users:
            if user.email == user_key.lower():
                return user
        raise exc.NoResultsError()
