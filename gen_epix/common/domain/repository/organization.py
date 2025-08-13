import abc

from gen_epix.common.domain import model  # forces models to be registered now
from gen_epix.fastapp import BaseRepository, BaseUnitOfWork


class BaseOrganizationRepository(BaseRepository):
    def __init__(
        self,
        user_class: type[model.User] = model.User,
        user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
    ):
        super().__init__()
        self.user_class = user_class
        self.user_invitation_class = user_invitation_class

    @abc.abstractmethod
    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        raise NotImplementedError()
