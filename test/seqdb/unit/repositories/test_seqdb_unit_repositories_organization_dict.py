"""Test seqdb model selection in the dictionary organization repository."""

from gen_epix.seqdb.domain import model
from gen_epix.seqdb.repositories.organization_dict import OrganizationDictRepository


def test_init_uses_seqdb_user_and_invitation_models() -> None:
    """Bind organization lookups to the seqdb model subclasses."""
    repository = OrganizationDictRepository(entities=[], db={})

    assert repository.user_class is model.User
    assert repository.user_invitation_class is model.UserInvitation
