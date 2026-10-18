from gen_epix.commondb.services import RbacService as CommonRbacService
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.services.rbac import RbacService


def test_constructor_passes_seqdb_role_enum_and_configuration(monkeypatch) -> None:
    """Configure the shared RBAC service with seqdb roles and caller options."""
    captured = {}

    def capture_init(self, app, logger=None, **kwargs) -> None:
        captured.update(app=app, logger=logger, kwargs=kwargs)

    monkeypatch.setattr(CommonRbacService, "__init__", capture_init)
    app = object()
    logger = object()

    RbacService(app, logger=logger, option="value")

    assert captured == {
        "app": app,
        "logger": logger,
        "kwargs": {"role_enum": enum.Role, "option": "value"},
    }
