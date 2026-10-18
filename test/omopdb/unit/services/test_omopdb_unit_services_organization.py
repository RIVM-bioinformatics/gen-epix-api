"""Validate OMOP-specific model wiring for the shared organization service."""

from gen_epix.commondb.services import OrganizationService as CommonOrganizationService
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.services.organization import OrganizationService


def test_initializes_common_service_with_omop_models(monkeypatch):
    """Pass OMOP identity models and caller configuration to shared handling."""
    captured = {}

    def capture_init(_service, *args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

    monkeypatch.setattr(CommonOrganizationService, "__init__", capture_init)

    app = object()
    props = {"setting": "value"}
    OrganizationService(app, name="omop", props=props)

    assert captured["args"] == (app,)
    assert captured["kwargs"] == {
        "name": "omop",
        "props": props,
        "user_class": model.User,
        "user_invitation_class": model.UserInvitation,
        "user_invitation_constraints_class": model.UserInvitationConstraints,
    }
