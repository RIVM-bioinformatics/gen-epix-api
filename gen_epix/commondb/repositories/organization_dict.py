"""Provide the in-memory repository implementation for commondb organizations."""

from collections.abc import Hashable, Iterable
from typing import Any

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.repository.organization import BaseOrganizationRepository
from gen_epix.fastapp import Entity, exc
from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class OrganizationDictRepository(DictRepository, BaseOrganizationRepository):
    """Encapsulates in-memory organization storage and normalized user lookup."""

    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[type[Model], dict[Hashable, Model]],
        user_class: type[model.User] = model.User,
        user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
        **kwargs: Any,
    ):
        """Initialize the dictionary backend and commondb user model types.

        Args:
            entities: Domain entities that can be stored by this repository.
            db: In-memory model tables indexed by model type and ID.
            user_class: Domain model representing users.
            user_invitation_class: Domain model representing user invitations.
            **kwargs: Additional dictionary repository configuration.
        """
        BaseOrganizationRepository.__init__(
            self, user_class=user_class, user_invitation_class=user_invitation_class
        )
        DictRepository.__init__(self, entities, db, **kwargs)

    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        """Determine whether a user exists for a case-insensitive key.

        Args:
            uow: Active unit of work for the lookup.
            user_key: Candidate user key, or None when no key is available.

        Returns:
            True when the normalized key identifies a stored user; otherwise False.
        """
        if user_key is None:
            return False
        for user in self._db[self.user_class].values():
            assert isinstance(user, self.user_class)
            if user.key == user_key.lower():
                return True
        return False

    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        """Retrieve a user by a case-insensitive key.

        Args:
            uow: Active unit of work for the lookup.
            user_key: User key to normalize and resolve.

        Returns:
            The matching user.

        Raises:
            NoResultsError: If no stored user has the normalized key.
        """
        for user in self._db[self.user_class].values():
            assert isinstance(user, self.user_class)
            if user.key == user_key.lower():
                return user
        raise exc.NoResultsError("ead06bf5")
