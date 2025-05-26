from typing import Any, Hashable, Type

from gen_epix.fastapp import BaseUnitOfWork, BaseUserManager, exc
from gen_epix.fastapp.model import Permission, User


class UserManager(BaseUserManager):

    def __init__(self, user_class: Type[User] = User) -> None:
        self.user_class = user_class
        self.users: dict[Hashable, User] = {}
        self.root_users: dict[Hashable, User] = {}

    def get_user_instance_from_claims(self, claims: dict[str, Any]) -> User:
        return self.user_class(**claims)

    def is_root_user(self, claims: dict[str, Any]) -> bool:
        return self.get_user_key_from_claims(claims) in self.root_users

    def create_root_user_from_claims(self, claims: dict[str, Any]) -> User:
        user = self.create_user_from_claims(claims)
        self.root_users[user.id] = user
        return user

    def create_user_from_claims(
        self, claims: dict[str, Any], user_id: Hashable = None
    ) -> User | None:
        if not user_id:
            user_id = claims.pop("id", self.get_user_key_from_claims(claims))
        if not user_id:
            raise exc.NoResultsError()
        new_user = self.user_class(id=user_id, **claims)
        if new_user.id in self.users:
            raise exc.AlreadyExistingIdsError(f"{user.id} already exists")
        self.users[new_user.id] = new_user
        return new_user

    def create_new_user_from_token(
        self, user: User, token: str, **kwargs: dict
    ) -> User:
        if user.id in self.users:
            raise exc.AlreadyExistingIdsError(f"{user.id} already exists")
        self.users[user.id] = user
        return user

    def retrieve_user_by_key(self, key: str) -> User:
        if key in self.users:
            return self.users[key]
        raise exc.NoResultsError()

    def is_existing_user_by_key(
        self, user_key: str | None, uow: BaseUnitOfWork
    ) -> bool:
        return user_key is not None and user_key in self.users

    def retrieve_user_by_id(self, user_id: Hashable) -> User:
        if user_id in self.users:
            return self.users[user_id]
        raise exc.NoResultsError()

    def retrieve_user_permissions(self, user: User) -> set[Permission]:
        raise NotImplementedError()
