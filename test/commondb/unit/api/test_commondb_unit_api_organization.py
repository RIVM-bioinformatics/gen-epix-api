"""Tests for the organization API's anonymization and own-user endpoint contracts."""

from test.util.mock_compat import Mock
from uuid import uuid4

import pytest
from fastapi import APIRouter

from gen_epix.commondb.api.organization import create_organization_endpoints
from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.model.organization import User


def _create_anonymize_endpoint(
    result: object,
) -> tuple[object, Mock, Mock, User]:
    return _create_endpoint("anonymize_user", result)


def _create_endpoint(
    operation_id: str,
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
        if getattr(route, "operation_id", None) == operation_id
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


@pytest.mark.asyncio
async def test_user_me_endpoint_returns_the_result_of_the_own_user_command() -> None:
    """Answer with what RetrieveOwnUserCommand returns for the requesting user."""
    endpoint, app, error_handler, user = _create_endpoint("user_me__get_one", None)
    app.handle.return_value = user

    result = await endpoint(user)

    assert result is user
    error_handler.assert_not_called()
    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.RetrieveOwnUserCommand)
    assert sent_command.user == user


@pytest.mark.asyncio
async def test_user_me_endpoint_reports_a_failed_command() -> None:
    """Send a command failure to the configured API error handler."""
    endpoint, app, error_handler, user = _create_endpoint("user_me__get_one", None)
    failure = RuntimeError("no user")
    app.handle.side_effect = failure
    # The real handler raises the HTTP error; so does this one.
    error_handler.side_effect = failure

    with pytest.raises(RuntimeError, match="no user"):
        await endpoint(user)

    error_handler.assert_called_once_with("5d0e7a41", user, failure)
