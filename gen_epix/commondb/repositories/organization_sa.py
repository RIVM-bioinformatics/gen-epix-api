"""Provide the SQLAlchemy repository implementation for commondb organizations."""

from typing import Any

from sqlalchemy import Engine, select

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.repository.organization import BaseOrganizationRepository
from gen_epix.commondb.repositories.sa_model.organization import User, UserInvitation
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation, exc
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork


class OrganizationSARepository(SARepository, BaseOrganizationRepository):
    """Store organization records and resolve users by normalized key in SQL."""

    def __init__(
        self,
        engine: Engine,
        user_class: type[model.User] = model.User,
        user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
        sa_user_class: type[User] = User,
        sa_user_invitation_class: type[UserInvitation] = UserInvitation,
        **kwargs: Any,
    ):
        """Initialize the SQL backend and commondb domain and SQL model types.

        Args:
            engine: SQLAlchemy engine used to create unit-of-work sessions.
            user_class: Domain model representing users.
            user_invitation_class: Domain model representing user invitations.
            sa_user_class: SQLAlchemy row model representing users.
            sa_user_invitation_class: SQLAlchemy row model representing invitations.
            **kwargs: Additional SQL repository configuration.
        """
        self.sa_user_class = sa_user_class
        self.sa_user_invitation_class = sa_user_invitation_class
        BaseOrganizationRepository.__init__(
            self, user_class=user_class, user_invitation_class=user_invitation_class
        )
        SARepository.__init__(self, engine, **kwargs)

    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        """Determine whether a user exists for a case-insensitive key.

        Args:
            uow: Active SQLAlchemy unit of work for the lookup.
            user_key: Candidate user key, or None when no key is available.

        Returns:
            True when the normalized key identifies a stored user; otherwise False.
        """
        if user_key is None:
            return False
        assert isinstance(uow, SAUnitOfWork)
        user_row = uow.session.execute(
            select(self.sa_user_class.id).where(
                self.sa_user_class.key == user_key.lower()
            )
        ).all()
        return True if user_row else False

    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        """Retrieve a user by a case-insensitive key.

        Args:
            uow: Active SQLAlchemy unit of work for the lookup.
            user_key: User key to normalize and resolve.

        Returns:
            The matching user.

        Raises:
            NoResultsError: If no stored user has the normalized key.
        """
        # TODO: add filter to crud method instead of retrieving all users
        users: list[model.User] = self.crud(  # type: ignore[assignment]
            uow,
            None,
            self.user_class,
            CrudOperation.READ_ALL,
        )
        for user in users:
            if user.key == user_key.lower():
                return user
        raise exc.NoResultsError("cdc4af04")
