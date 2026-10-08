"""Tests for the organization API's anonymization endpoint contract."""

from test.util.mock_compat import Mock
from uuid import uuid4

import pytest
from fastapi import APIRouter

from gen_epix.commondb.api.organization import create_organization_endpoints
from gen_epix.commondb.domain.model.organization import User


def _create_anonymize_endpoint(
    result: object,
) -> tuple[object, Mock, Mock, User]:
    router = APIRouter()
    app = Mock()
    app.impl.get_mapped_class.side_effect = lambda model_class: model_class
    app.impl.registered_user_dependency = User
    app.impl.new_user_dependency = User
    app.domain.get_dag_sorted_entities.return_value = []
    app.handle.return_value = result
    error_handler = Mock()
    create_organization_endpoints(router, app, handle_exception=error_handler)
    endpoint = next(
        route.endpoint
        for route in router.routes
        if getattr(route, "operation_id", None) == "anonymize_user"
    )
    user = User(
        id=uuid4(),
        key="user@example.com",
        email="user@example.com",
        roles={"COMMONDB_USER"},
        organization_id=uuid4(),
        is_active=True,
    )
    return endpoint, app, error_handler, user


@pytest.mark.asyncio
async def test_anonymize_endpoint_accepts_none_result() -> None:
    """Accept the endpoint's required no-content command result."""
    endpoint, app, error_handler, user = _create_anonymize_endpoint(None)

    result = await endpoint(user, uuid4())

    assert result is None
    error_handler.assert_not_called()
    assert app.handle.call_args.args[0].user == user


@pytest.mark.asyncio
async def test_anonymize_endpoint_reports_non_none_result() -> None:
    """Send an invalid command result to the configured API error handler."""
    endpoint, _, error_handler, user = _create_anonymize_endpoint(object())

    await endpoint(user, uuid4())

    error_handler.assert_called_once()
    error = error_handler.call_args.args[2]
    assert isinstance(error, RuntimeError)
    assert str(error) == "AnonymizeUserCommand must not return a value"
