"""Test the OMOP dictionary-backed organization repository adapter."""

from gen_epix.omopdb.domain import model
from gen_epix.omopdb.repositories.organization_dict import OrganizationDictRepository


def test_uses_omopdb_user_models() -> None:
    """Configure the shared repository with OMOP's user model exports."""
    repository = OrganizationDictRepository([], {})

    assert repository.user_class is model.User
    assert repository.user_invitation_class is model.UserInvitation
