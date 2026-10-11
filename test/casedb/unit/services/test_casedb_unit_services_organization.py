from typing import Any

import pytest

from gen_epix.casedb.domain import model
from gen_epix.casedb.services.organization import OrganizationService
from gen_epix.commondb.services import OrganizationService as CommonOrganizationService


def test_init_forwards_arguments_and_casedb_model_classes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def capture_init(self: Any, *args: Any, **kwargs: Any) -> None:
        captured["args"] = args
        captured["kwargs"] = kwargs

    monkeypatch.setattr(CommonOrganizationService, "__init__", capture_init)

    OrganizationService("app", option="value")

    assert captured == {
        "args": ("app",),
        "kwargs": {
            "option": "value",
            "user_class": model.User,
            "user_invitation_class": model.UserInvitation,
            "user_invitation_constraints_class": model.UserInvitationConstraints,
        },
    }