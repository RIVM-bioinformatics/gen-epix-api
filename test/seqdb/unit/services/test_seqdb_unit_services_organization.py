"""Check SeqDB model bindings in its shared organization service."""

from test.util.mock_compat import Mock

from gen_epix.seqdb.domain import model
from gen_epix.seqdb.services.organization import OrganizationService


def test_organization_service_uses_seqdb_user_and_invitation_models():
    """Bind the SeqDB model classes while preserving shared service setup."""
    app = Mock()
    app.impl.get_mapped_class.side_effect = {
        model.User: model.User,
        model.UserInvitation: model.UserInvitation,
        model.UserInvitationConstraints: model.UserInvitationConstraints,
    }.__getitem__

    service = OrganizationService(app, register_handlers=False, name="seqdb-org")

    assert service.user_class is model.User
    assert service.user_invitation_class is model.UserInvitation
    assert service.user_invitation_constraints_class is model.UserInvitationConstraints
    assert service.name == "seqdb-org"
