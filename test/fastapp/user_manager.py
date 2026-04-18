from collections.abc import Hashable
from typing import Any

from pydantic import BaseModel

from gen_epix.fastapp import BaseUnitOfWork, BaseUserManager, exc
from gen_epix.fastapp.model import Permission, User


class MockUser(BaseModel):
    id: str
    key: str
    email: str
    name: str


MOCK_USER = MockUser(
    id="id1", key="user1@org1.org", email="user1@org1.org", name="user1"
)


class UserManager(BaseUserManager):

    def __init__(self, user_class: type[User] = User) -> None:
        self.user_class = user_class
        self.users: dict[Hashable, User] = {}
        self.root_users: dict[Hashable, User] = {}

    def construct_user_instance_from_claims(self, claims: dict[str, Any]) -> User:
        return self.user_class(**claims)

    def is_root_user_claims(self, claims: dict[str, Any]) -> bool:
        return self.get_user_key_from_claims(claims) in self.root_users

    def is_root_user(self, user: User) -> bool:
        return user.id in self.root_users

    def create_root_user_from_claims(self, claims: dict[str, Any]) -> User:
        user = self.auto_create_new_user(claims)
        assert user.id is not None
        self.root_users[user.id] = user
        return user

    def auto_create_new_user(
        self, claims: dict[str, Any], user_id: Hashable = None
    ) -> User | None:
        if not user_id:
            user_id = claims.pop("id", self.get_user_key_from_claims(claims))
        if not user_id:
            raise exc.NoResultsError("c31ff1e1")
        new_user = self.user_class(id=user_id, **claims)
        if new_user.id in self.users:
            raise exc.AlreadyExistingIdsError(
                "1d92f264", f"{new_user.id} already exists"
            )
        self.users[new_user.id] = new_user
        return new_user

    def create_new_user_from_token(self, user: User, token: str, **kwargs: Any) -> User:
        if user.id in self.users:
            raise exc.AlreadyExistingIdsError("999b7823", f"{user.id} already exists")
        self.users[user.id] = user
        return user

    def retrieve_user_by_key(self, key: str) -> User:
        if key in self.users:
            return self.users[key]
        raise exc.NoResultsError("44c86617")

    def is_existing_user_by_key(
        self, user_key: str | None, uow: BaseUnitOfWork
    ) -> bool:
        return user_key is not None and user_key in self.users

    def retrieve_user_by_id(self, user_id: Hashable) -> User:
        if user_id in self.users:
            return self.users[user_id]
        raise exc.NoResultsError("976c7db0")

    def retrieve_user_permissions(self, user: User) -> set[Permission]:
        raise NotImplementedError()

    def update_user_name(  # type: ignore[override]
        self, user: MockUser, new_name: str
    ) -> MockUser | None:
        if user.name == new_name:
            return user
        user.name = new_name
        updated_user: MockUser = user
        return updated_user

    def get_user_name_from_claims(self, claims: dict[str, Any]) -> str | None:
        return claims.get("name")
