"""Test commondb RBAC endpoint registration."""

from test.util.mock_compat import Mock, patch
from types import SimpleNamespace

import pytest
from fastapi import APIRouter

from gen_epix.commondb.api.rbac import create_rbac_endpoints
from gen_epix.commondb.domain import enum
from gen_epix.fastapp.api import CrudEndpointGenerator


@pytest.mark.parametrize(
    ("service_type_kwargs", "expected_service_type"),
    [
        pytest.param({}, enum.ServiceType.RBAC, id="default-service-type"),
        pytest.param(
            {"service_type": enum.ServiceType.ABAC},
            enum.ServiceType.ABAC,
            id="explicit-service-type",
        ),
    ],
)
def test_create_rbac_endpoints_generates_crud_routes(
    service_type_kwargs: dict[str, enum.ServiceType],
    expected_service_type: enum.ServiceType,
) -> None:
    """Generate CRUD routes with the selected service and registered-user dependency."""
    router = APIRouter()
    app = Mock()
    registered_user_dependency = object()
    app.impl = SimpleNamespace(
        registered_user_dependency=registered_user_dependency,
    )
    crud_endpoint_sets = [object()]
    handle_exception = Mock()

    with (
        patch.object(
            CrudEndpointGenerator,
            "create_crud_endpoint_set_for_domain",
            return_value=crud_endpoint_sets,
        ) as create_endpoint_sets,
        patch.object(CrudEndpointGenerator, "generate_endpoints") as generate_endpoints,
    ):
        create_rbac_endpoints(
            router,
            app,
            handle_exception=handle_exception,
            **service_type_kwargs,
        )

    create_endpoint_sets.assert_called_once_with(
        app,
        service_type=expected_service_type,
        user_dependency=registered_user_dependency,
    )
    generate_endpoints.assert_called_once_with(
        router,
        crud_endpoint_sets,
        handle_exception,
    )
