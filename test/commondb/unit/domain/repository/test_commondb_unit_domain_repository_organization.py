"""Test the commondb organization repository interface."""

from inspect import isabstract
from typing import cast

import pytest

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.repository.organization import BaseOrganizationRepository
from gen_epix.fastapp import BaseRepository, BaseUnitOfWork


class _ConcreteOrganizationRepository(BaseOrganizationRepository):
    @classmethod
    def create_repository(cls, **kwargs: object) -> BaseRepository:
        raise NotImplementedError

    def crud(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    def read_fields(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    def split_filter(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError

    def verify_valid_ids(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError

    def uow(self, **kwargs: object) -> BaseUnitOfWork:
        raise NotImplementedError

    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        return super().is_existing_user_by_key(uow, user_key)

    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        return super().retrieve_user_by_key(uow, user_key)


def test_base_organization_repository_preserves_abstract_repository_contract() -> None:
    assert issubclass(BaseOrganizationRepository, BaseRepository)
    assert isabstract(BaseOrganizationRepository)


def test_base_organization_repository_uses_default_model_classes() -> None:
    repository = _ConcreteOrganizationRepository()

    assert repository.user_class is model.User
    assert repository.user_invitation_class is model.UserInvitation


def test_is_existing_user_by_key_abstract_stub_raises() -> None:
    repository = _ConcreteOrganizationRepository()

    with pytest.raises(NotImplementedError):
        repository.is_existing_user_by_key(cast(BaseUnitOfWork, None), None)


def test_retrieve_user_by_key_abstract_stub_raises() -> None:
    repository = _ConcreteOrganizationRepository()

    with pytest.raises(NotImplementedError):
        repository.retrieve_user_by_key(cast(BaseUnitOfWork, None), "user@example.org")
