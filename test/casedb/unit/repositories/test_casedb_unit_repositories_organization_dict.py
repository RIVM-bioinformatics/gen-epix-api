"""Test casedb dictionary-backed organization repository composition."""

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.repository import BaseOrganizationRepository
from gen_epix.casedb.repositories import (
    OrganizationDictRepository as ExportedRepository,
)
from gen_epix.casedb.repositories.organization_dict import OrganizationDictRepository
from gen_epix.fastapp.repositories import DictRepository


def test_repository_combines_dict_storage_and_organization_contract() -> None:
    """The repository combines dictionary storage and organization behavior."""
    assert issubclass(OrganizationDictRepository, DictRepository)
    assert issubclass(OrganizationDictRepository, BaseOrganizationRepository)
    assert OrganizationDictRepository.__mro__.index(
        DictRepository
    ) < OrganizationDictRepository.__mro__.index(BaseOrganizationRepository)


def test_repository_uses_casedb_user_model_types() -> None:
    """The repository binds organization lookups to casedb's user models."""
    repository = OrganizationDictRepository(entities=[], db={})

    assert repository.user_class is model.User
    assert repository.user_invitation_class is model.UserInvitation


def test_repository_is_exported_from_package() -> None:
    """The package export resolves to the module's repository class."""
    assert ExportedRepository is OrganizationDictRepository
