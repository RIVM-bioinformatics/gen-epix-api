import abc
from collections.abc import Hashable
from typing import Any

from gen_epix.fastapp import model
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class BaseUserManager(abc.ABC):
    """
    Class that defines the interface for a user manager. This class should be
    subclassed and the methods implemented to provide the necessary functionality for
    the user manager to work with the system. The user manager is responsible for
    creating, retrieving, and managing users in the system.

    The claims passed to the methods in this class are e.g. the claims extracted from
    a JWT token.
    """

    def get_user_key_from_claims(self, claims: dict[str, Any]) -> str | None:
        """
        Get the user key, which uniquely identifies the user across systems, from the
        claims. The email claim is used here as the default user key, override this
        method if another key should be used.
        """
        email: str = claims["email"]
        return email.lower()

    @abc.abstractmethod
    def get_user_instance_from_claims(
        self, claims: dict[str, Any]
    ) -> model.User | None:
        raise NotImplementedError

    @abc.abstractmethod
    def create_root_user_from_claims(self, claims: dict[str, Any]) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def is_root_user_claims(self, claims: dict[str, Any]) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def is_root_user(self, user: model.User) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def create_user_from_claims(self, claims: dict[str, Any]) -> model.User | None:
        raise NotImplementedError

    @abc.abstractmethod
    def create_new_user_from_token(
        self, user: model.User, token: str, **kwargs: Any
    ) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def is_existing_user_by_key(
        self, user_key: str | None, uow: BaseUnitOfWork
    ) -> bool:
        """
        Check if a user exists by their key.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_key(self, user_key: str) -> model.User:
        """
        Retrieve an existing user by their key.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_id(self, user_id: Hashable) -> model.User:
        """
        Retrieve an existing user by their id.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_permissions(self, user: model.User) -> set[model.Permission]:
        """
        Retrieve the permissions for a user instance.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_user_name_from_claims(self, claims: dict[str, Any]) -> str | None:
        """
        Extract a user-friendly display name from raw claims (dict),
        mirroring the AuthService.get_name_from_claims priority and handling
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def update_user_name(self, user: model.User, new_name: str) -> model.User | None:
        """
        Update the user's name in the user manager.
        This method should be implemented to update the user's name in the user manager.
        """
        raise NotImplementedError()
