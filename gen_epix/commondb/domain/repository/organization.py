import abc

from gen_epix.commondb.domain import model
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
        """Check if a user exists by their unique key (e.g., email)."""
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        """Retrieve a user by their unique key (e.g., email)."""
        raise NotImplementedError()
