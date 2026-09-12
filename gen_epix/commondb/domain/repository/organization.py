"""Define the repository interface for commondb organization data."""

import abc

from gen_epix.commondb.domain import model
from gen_epix.fastapp import BaseRepository, BaseUnitOfWork


class BaseOrganizationRepository(BaseRepository):
    """Encapsulates organization-specific user lookup operations for services."""

    def __init__(
        self,
        user_class: type[model.User] = model.User,
        user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
    ):
        """Initialize the repository with its user and invitation model classes.

        Args:
            user_class: Persisted model used for users.
            user_invitation_class: Persisted model used for user invitations.
        """
        super().__init__()
        self.user_class = user_class
        self.user_invitation_class = user_invitation_class

    @abc.abstractmethod
    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        """Determine whether a user exists for a normalized unique key.

        Args:
            uow: Unit of work that scopes the repository operation.
            user_key: User key to look up, such as an email address.

        Returns:
            True when a matching user exists.

        Raises:
            NotImplementedError: Always; concrete repositories implement lookup.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        """Retrieve the user associated with a normalized unique key.

        Args:
            uow: Unit of work that scopes the repository operation.
            user_key: User key to look up, such as an email address.

        Returns:
            The matching user.

        Raises:
            NotImplementedError: Always; concrete repositories implement lookup.
        """
        raise NotImplementedError()
