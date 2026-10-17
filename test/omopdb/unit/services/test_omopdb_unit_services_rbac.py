"""Verify the OmopDB RBAC service specialization."""

from gen_epix.commondb.services import RbacService as CommonRbacService
from gen_epix.omopdb.domain import enum
from gen_epix.omopdb.services.rbac import RbacService


def test_initializes_common_service_with_omop_roles(monkeypatch):
    """Forward app configuration and the OmopDB role enum to the base service."""
    captured = {}

    def capture_init(service, app, **kwargs):
        captured["service"] = service
        captured["app"] = app
        captured["kwargs"] = kwargs

    monkeypatch.setattr(CommonRbacService, "__init__", capture_init)

    app = object()
    logger = object()
    properties = {"setting": "value"}
    RbacService(app, logger=logger, properties=properties)

    assert isinstance(captured["service"], RbacService)
    assert captured["app"] is app
    assert captured["kwargs"] == {
        "logger": logger,
        "role_enum": enum.Role,
        "properties": properties,
    }
