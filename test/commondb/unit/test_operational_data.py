"""Test the shared reset command, feature flag, endpoint, and RBAC lifecycle."""

from importlib import import_module
from test.util.mock_compat import Mock
from types import SimpleNamespace
from typing import Annotated
from uuid import uuid4

import pytest
from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient

from gen_epix.commondb.api.operational_data import create_operational_data_endpoints
from gen_epix.commondb.domain.command import DeleteOperationalDataCommand
from gen_epix.commondb.domain.enum import FeatureFlag, Role
from gen_epix.commondb.domain.model import User
from gen_epix.fastapp import App, exc


@pytest.mark.parametrize("app_name", ["commondb", "casedb", "seqdb", "omopdb"])
@pytest.mark.parametrize(
    "role_name",
    ["ROOT", "APP_ADMIN", "ORG_ADMIN", "REFDATA_ADMIN", "ORG_USER", "GUEST"],
)
def test_reset_rbac(app_name: str, role_name: str) -> None:
    """Only root and app administrators reach the handler through App.handle."""
    domain = import_module(f"gen_epix.{app_name}.domain").DOMAIN
    enum = import_module(f"gen_epix.{app_name}.domain.enum")
    generator = import_module(
        f"gen_epix.{app_name}.domain.policy.permission"
    ).RoleGenerator
    rbac_class = import_module(f"gen_epix.{app_name}.services.rbac").RbacService
    app = App(
        domain=domain,
        impl=SimpleNamespace(
            role_map=generator.get_role_map(), role_set_map=generator.get_role_set_map()
        ),
    )
    rbac = rbac_class(app, service_type=enum.ServiceType.RBAC)
    rbac.register_roles(generator.get_role_permissions_map(), enum.Role.ROOT.value)
    rbac.register_policies()
    handler = Mock(return_value=None)
    app.register_handler(DeleteOperationalDataCommand, handler)
    user = User(
        id=uuid4(),
        key="reset@example.org",
        email="reset@example.org",
        organization_id=uuid4(),
        is_active=True,
        roles={enum.Role[role_name].value},
    )
    cmd = DeleteOperationalDataCommand(user=user)
    if role_name in {"ROOT", "APP_ADMIN"}:
        assert app.handle(cmd) is None
        handler.assert_called_once_with(cmd)
    else:
        with pytest.raises(exc.UnauthorizedAuthError):
            app.handle(cmd)
        handler.assert_not_called()


@pytest.mark.parametrize("enabled", [None, False, True])
def test_reset_endpoint_visibility_and_dispatch(enabled: bool | None) -> None:
    """Only enabled routers expose a bodyless DELETE returning HTTP 204."""
    user = User(
        id=uuid4(),
        key="reset@example.org",
        email="reset@example.org",
        organization_id=uuid4(),
        is_active=True,
        roles={Role.ROOT.value},
    )

    def get_user() -> User:
        """Supply the authenticated user without an external identity provider."""
        return user

    app = App(
        impl=SimpleNamespace(
            registered_user_dependency=Annotated[User, Depends(get_user)]
        )
    )
    if enabled is not None:
        app.set_feature_flag(FeatureFlag.ALLOW_DELETE_OPERATIONAL_DATA.value, enabled)
    handler = Mock(return_value=None)
    app.register_handler(DeleteOperationalDataCommand, handler)
    api = FastAPI()
    router = APIRouter()
    create_operational_data_endpoints(router, app)
    api.include_router(router, prefix="/v1")
    with TestClient(api) as client:
        response = client.delete("/v1/operational_data")
    assert response.status_code == (204 if enabled else 404)
    assert ("/v1/operational_data" in api.openapi()["paths"]) == bool(enabled)
    if enabled:
        assert response.content == b""
        assert handler.call_args.args[0].user is user
    else:
        handler.assert_not_called()
