"""Tests for the organization API's anonymization and own-user endpoint contracts."""

from test.util.mock_compat import Mock
from uuid import uuid4

import pytest
from fastapi import APIRouter

from gen_epix.commondb.api.organization import (
    CommandName,
    DataCollectionSetDataCollectionUpdateAssociationRequestBody,
    InviteUserRequestBody,
    OrganizationIdentifierIssuerUpdateAssociationRequestBody,
    OrganizationSetOrganizationUpdateAssociationRequestBody,
    RetrieveOrganizationContactsRequestBody,
    UpdateUserOwnOrganizationRequestBody,
    UpdateUserRequestBody,
    create_organization_endpoints,
)
from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.model import Permission


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


@pytest.mark.asyncio
async def test_invite_user_endpoint_builds_invitation_command() -> None:
    endpoint, app, error_handler, user = _create_endpoint("invite_user", object())
    organization_id = uuid4()
    request_body = InviteUserRequestBody(
        key=None,
        description="Temporary access",
        roles={"COMMONDB_USER"},
        organization_id=organization_id,
    )

    result = await endpoint(user, request_body)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.InviteUserCommand)
    assert sent_command.user == user
    assert sent_command.key is None
    assert sent_command.description == "Temporary access"
    assert sent_command.roles == {"COMMONDB_USER"}
    assert sent_command.organization_id == organization_id
    assert result is app.handle.return_value
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_invite_user_endpoint_reports_command_failure() -> None:
    endpoint, app, error_handler, user = _create_endpoint("invite_user", None)
    failure = RuntimeError("invitation failed")
    app.handle.side_effect = failure
    error_handler.side_effect = failure
    request_body = InviteUserRequestBody(
        key="new@example.com",
        description="Temporary access",
        roles={"COMMONDB_USER"},
        organization_id=uuid4(),
    )

    with pytest.raises(RuntimeError, match="invitation failed"):
        await endpoint(user, request_body)

    error_handler.assert_called_once_with("e088de91", None, failure)


@pytest.mark.asyncio
async def test_invite_user_constraints_endpoint_dispatches_command() -> None:
    constraints = object()
    endpoint, app, error_handler, user = _create_endpoint(
        "invite_user__constraints", constraints
    )

    result = await endpoint(user)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.RetrieveInviteUserConstraintsCommand)
    assert sent_command.user == user
    assert result is constraints
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_register_invited_user_endpoint_dispatches_token() -> None:
    endpoint, app, error_handler, user = _create_endpoint(
        "user_registrations__post_one", user_result := object()
    )
    token = "invite-token"

    result = await endpoint(user, token)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.RegisterInvitedUserCommand)
    assert sent_command.user == user
    assert sent_command.token == token
    assert result is user_result
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_organization_set_members_endpoint_dispatches_associations() -> None:
    endpoint, app, error_handler, user = _create_endpoint(
        "organization_sets__put__organizations", []
    )
    organization_set_id = uuid4()
    request_body = OrganizationSetOrganizationUpdateAssociationRequestBody(
        organization_set_members=[]
    )

    result = await endpoint(user, organization_set_id, request_body)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(
        sent_command, command.OrganizationSetOrganizationUpdateAssociationCommand
    )
    assert sent_command.user == user
    assert sent_command.obj_id1 == organization_set_id
    assert sent_command.association_objs == []
    assert sent_command.props == {"return_id": False}
    assert result == []
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_data_collection_set_members_endpoint_dispatches_associations() -> None:
    endpoint, app, error_handler, user = _create_endpoint(
        "data_collection_sets__put__data_collections", []
    )
    data_collection_set_id = uuid4()
    request_body = DataCollectionSetDataCollectionUpdateAssociationRequestBody(
        data_collection_set_members=[]
    )

    result = await endpoint(user, data_collection_set_id, request_body)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(
        sent_command, command.DataCollectionSetDataCollectionUpdateAssociationCommand
    )
    assert sent_command.user == user
    assert sent_command.obj_id1 == data_collection_set_id
    assert sent_command.association_objs == []
    assert sent_command.props == {"return_id": False}
    assert result == []
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_association_endpoint_reports_command_failure() -> None:
    endpoint, app, error_handler, user = _create_endpoint(
        "organization_sets__put__organizations", None
    )
    failure = RuntimeError("association failed")
    app.handle.side_effect = failure
    error_handler.side_effect = failure
    request_body = OrganizationSetOrganizationUpdateAssociationRequestBody(
        organization_set_members=[]
    )

    with pytest.raises(RuntimeError, match="association failed"):
        await endpoint(user, uuid4(), request_body)

    error_handler.assert_called_once_with("c026628e", user, failure)


@pytest.mark.asyncio
async def test_user_permissions_endpoint_converts_permissions_to_api_models() -> None:
    permission = Permission(
        command_name=next(iter(CommandName)).value,
        permission_type=PermissionType.READ,
    )
    endpoint, app, error_handler, user = _create_endpoint(
        "user_me__retrieve_permissions", {permission}
    )

    result = await endpoint(user)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.RetrieveOwnPermissionsCommand)
    assert sent_command.user == user
    assert len(result) == 1
    converted_permission = next(iter(result))
    assert converted_permission.command_name == permission.command_name
    assert converted_permission.permission_type == permission.permission_type
    error_handler.assert_not_called()


@pytest.mark.parametrize(
    ("operation_id", "exception_code", "call_kind", "error_user"),
    [
        ("user_registrations__post_one", "fc1fc53c", "register", None),
        ("user_me__retrieve_permissions", "a7f3b8e2", "permissions", "user"),
        ("update_user", "a594ba2b", "update_user", None),
        (
            "update_user_own_organization",
            "c2382b65",
            "update_own_organization",
            None,
        ),
    ],
    ids=["register", "permissions", "update-user", "own-organization"],
)
@pytest.mark.asyncio
async def test_user_command_endpoints_report_failures(
    operation_id: str,
    exception_code: str,
    call_kind: str,
    error_user: str | None,
) -> None:
    endpoint, app, error_handler, user = _create_endpoint(operation_id, None)
    failure = RuntimeError("command failed")
    app.handle.side_effect = failure
    error_handler.side_effect = failure

    if call_kind == "register":
        endpoint_call = endpoint(user, "invite-token")
    elif call_kind == "permissions":
        endpoint_call = endpoint(user)
    elif call_kind == "update_user":
        endpoint_call = endpoint(
            user,
            uuid4(),
            UpdateUserRequestBody(is_active=None, roles=None, organization_id=None),
        )
    else:
        endpoint_call = endpoint(
            user, UpdateUserOwnOrganizationRequestBody(organization_id=uuid4())
        )

    with pytest.raises(RuntimeError, match="command failed"):
        await endpoint_call

    error_handler.assert_called_once_with(
        exception_code, user if error_user == "user" else None, failure
    )


@pytest.mark.asyncio
async def test_update_user_endpoint_builds_update_command() -> None:
    user_result = object()
    endpoint, app, error_handler, user = _create_endpoint("update_user", user_result)
    target_user_id = uuid4()
    organization_id = uuid4()
    request_body = UpdateUserRequestBody(
        is_active=False,
        roles={"COMMONDB_USER"},
        organization_id=organization_id,
    )

    result = await endpoint(user, target_user_id, request_body)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.UpdateUserCommand)
    assert sent_command.user == user
    assert sent_command.tgt_user_id == target_user_id
    assert sent_command.is_active is False
    assert sent_command.roles == {"COMMONDB_USER"}
    assert sent_command.organization_id == organization_id
    assert result is user_result
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_own_organization_endpoint_builds_command() -> None:
    user_result = object()
    endpoint, app, error_handler, user = _create_endpoint(
        "update_user_own_organization", user_result
    )
    organization_id = uuid4()
    request_body = UpdateUserOwnOrganizationRequestBody(organization_id=organization_id)

    result = await endpoint(user, request_body)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.UpdateUserOwnOrganizationCommand)
    assert sent_command.user == user
    assert sent_command.organization_id == organization_id
    assert result is user_result
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_organization_identifier_issuers_dispatch_associations() -> None:
    endpoint, app, error_handler, user = _create_endpoint(
        "organizations__put__identifier_issuers", []
    )
    organization_id = uuid4()
    request_body = OrganizationIdentifierIssuerUpdateAssociationRequestBody(
        organization_identifier_issuer_links=[]
    )

    result = await endpoint(user, organization_id, request_body)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(
        sent_command, command.OrganizationIdentifierIssuerUpdateAssociationCommand
    )
    assert sent_command.user == user
    assert sent_command.obj_id1 == organization_id
    assert sent_command.association_objs == []
    assert sent_command.props == {"return_id": False}
    assert result == []
    error_handler.assert_not_called()


@pytest.mark.asyncio
async def test_retrieve_organization_contacts_dispatches_id() -> None:
    contacts = object()
    endpoint, app, error_handler, user = _create_endpoint(
        "retrieve__organization_contacts", contacts
    )
    organization_id = uuid4()
    request_body = RetrieveOrganizationContactsRequestBody(
        organization_id=organization_id
    )

    result = await endpoint(user, request_body)

    sent_command = app.handle.call_args.args[0]
    assert isinstance(sent_command, command.RetrieveOrganizationContactsCommand)
    assert sent_command.user == user
    assert sent_command.organization_id == organization_id
    assert result is contacts
    error_handler.assert_not_called()
