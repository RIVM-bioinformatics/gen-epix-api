"""Tests for the shared commondb endpoint test client."""

import json
from test.util.mock_compat import Mock
from types import SimpleNamespace
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi import FastAPI
from httpx import Response

from gen_epix.commondb.api import InviteUserRequestBody, UpdateUserRequestBody
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.test.endpoint_test_client import EndpointTestClient
from gen_epix.fastapp import Command, CrudOperation
from gen_epix.filter.equals_string import EqualsStringFilter


@pytest.fixture
def endpoint_client() -> EndpointTestClient:
    """Build the endpoint client around a mocked HTTP transport."""
    client = object.__new__(EndpointTestClient)
    client.route_prefix = "/v1"
    client.test_client = Mock()
    client._handlers = {
        command.GetIdentityProvidersCommand: client.handle_get_identity_providers
    }
    client.test_client.get.return_value = Response(400)
    client.test_client.post.return_value = Response(400)
    client.test_client.put.return_value = Response(400)
    client.test_client.delete.return_value = Response(400)
    client.user_class = model.User
    client.user_invitation_class = model.UserInvitation
    client.user_invitation_constraints_class = model.UserInvitationConstraints
    client.user_invitation_request_body = InviteUserRequestBody
    client.update_user_request_body = UpdateUserRequestBody
    return client


@pytest.fixture
def organization() -> model.Organization:
    """Return a valid organization with a stable identifier for one test."""
    return model.Organization(id=uuid4(), code="org", name="Organization")


def test_constructor_registers_default_handlers_and_optional_crud() -> None:
    """Register standard handlers and conditionally register CRUD handlers."""
    app = SimpleNamespace(
        domain=SimpleNamespace(crud_commands={command.OrganizationCrudCommand})
    )
    fast_api = FastAPI()
    client = EndpointTestClient(app, fast_api, {})
    try:
        assert command.OrganizationCrudCommand in client._handlers
        assert command.GetIdentityProvidersCommand in client._handlers
        assert command.InviteUserCommand in client._handlers
        assert client.route_prefix == ""

        without_crud = EndpointTestClient(
            SimpleNamespace(), FastAPI(), {}, register_crud_commands=False
        )
        assert command.OrganizationCrudCommand not in without_crud._handlers
        assert without_crud.route_prefix == ""
        without_crud.test_client.close()
    finally:
        client.test_client.close()


def test_register_and_handle_dispatch_and_route_prefix_override(
    endpoint_client: EndpointTestClient,
) -> None:
    """Dispatch commands, preserve responses, and honor route-prefix overrides."""
    response = Response(200, json=[])
    endpoint_client.test_client.get.return_value = response
    cmd = command.GetIdentityProvidersCommand()

    assert endpoint_client.handle(cmd, return_response=True, route_prefix="") == (
        [],
        response,
    )
    endpoint_client.test_client.get.assert_called_once_with("/identity_providers")

    endpoint_client.test_client.get.reset_mock()
    endpoint_client.handle(cmd)
    endpoint_client.test_client.get.assert_called_once_with("/v1/identity_providers")

    custom_handler = Mock(return_value=("handled", response))
    generic_command = Command()
    endpoint_client.register_handler(Command, custom_handler)
    assert endpoint_client.handle(generic_command, return_response=True) == (
        "handled",
        response,
    )
    custom_handler.assert_called_once_with(generic_command, "/v1", None)

    with pytest.raises(NotImplementedError, match="Unsupported command"):
        endpoint_client.handle(command.RetrieveLicensesCommand())


def test_handle_forwards_generated_headers_for_a_user_command(
    endpoint_client: EndpointTestClient,
) -> None:
    """Attach a signed bearer token when the command has a user."""
    user = model.User(
        id=uuid4(),
        email="user@example.org",
        name="User",
        roles={"reader"},
        organization_id=uuid4(),
    )
    endpoint_client._handlers[command.OrganizationCrudCommand] = (
        endpoint_client.handle_crud_command
    )
    endpoint_client.handle(
        command.OrganizationCrudCommand(operation=CrudOperation.READ_ALL, user=user)
    )

    call = endpoint_client.test_client.get.call_args
    assert call.args == ("/v1/organizations",)
    authorization = call.kwargs["headers"]["Authorization"]
    claims = jwt.decode(
        authorization.removeprefix("Bearer "),
        options={"verify_signature": False, "verify_exp": False},
    )
    assert claims["__key__"] == user.email


def test_specialized_handlers_build_expected_requests(
    endpoint_client: EndpointTestClient,
) -> None:
    """Translate supported specialized commands into their REST requests."""
    organization_id = uuid4()
    invite = command.InviteUserCommand(
        key="invitee@example.org",
        email="invitee@example.org",
        name="Invitee",
        description="New account",
        roles={"reader"},
        organization_id=organization_id,
    )
    endpoint_client.handle_invite_user(invite, "/api", {"Authorization": "token"})
    endpoint_client.test_client.post.assert_called_once_with(
        "/api/invite_user",
        json={
            "key": "invitee@example.org",
            "description": "New account",
            "roles": ["reader"],
            "organization_id": str(organization_id),
        },
        headers={"Authorization": "token"},
    )

    endpoint_client.test_client.get.reset_mock()
    endpoint_client.handle_get_identity_providers(
        command.GetIdentityProvidersCommand(), "/api", None
    )
    endpoint_client.test_client.get.assert_called_once_with("/api/identity_providers")

    endpoint_client.test_client.get.reset_mock()
    endpoint_client.handle_retrieve_invite_user_constraints(
        command.RetrieveInviteUserConstraintsCommand(), "/api", None
    )
    endpoint_client.test_client.get.assert_called_once_with(
        "/api/invite_user/constraints", headers=None
    )

    endpoint_client.test_client.post.reset_mock()
    endpoint_client.handle_register_invited_user(
        command.RegisterInvitedUserCommand(token="invite-token"), "/api", None
    )
    endpoint_client.test_client.post.assert_called_once_with(
        "/api/user_registrations/invite-token", headers=None
    )

    endpoint_client.test_client.put.reset_mock()
    target_user_id = uuid4()
    endpoint_client.handle_update_user(
        command.UpdateUserCommand(
            tgt_user_id=target_user_id,
            is_active=False,
            roles={"reader"},
            organization_id=organization_id,
        ),
        "/api",
        {"Authorization": "token"},
    )
    endpoint_client.test_client.put.assert_called_once_with(
        f"/api/update_user/{target_user_id}",
        headers={"Authorization": "token"},
        json={
            "is_active": False,
            "roles": ["reader"],
            "organization_id": str(organization_id),
        },
    )


def test_get_headers_handles_absent_and_email_fallback_users(
    endpoint_client: EndpointTestClient,
) -> None:
    """Return no headers without a user and reject users without an identity."""
    assert endpoint_client.get_headers(Command(user=None)) is None

    class EmailOnlyUser(model.User):
        """Represent a valid user whose key is absent but email is present."""

        def get_key(self) -> str:
            """Provide the empty key that exercises email fallback."""
            return ""

    user = EmailOnlyUser(
        id=uuid4(),
        email="fallback@example.org",
        roles={"reader"},
        organization_id=uuid4(),
    )
    headers = endpoint_client.get_headers(Command(user=user))
    assert headers is not None
    assert headers["Authorization"].startswith("Bearer ")
    claims = jwt.decode(
        headers["Authorization"].removeprefix("Bearer "),
        options={"verify_signature": False, "verify_exp": False},
    )
    assert claims["__key__"] == "fallback@example.org"

    with pytest.raises(ValueError, match="neither key nor email"):
        endpoint_client.get_headers(
            Command(
                user=EmailOnlyUser(
                    id=uuid4(), email="", roles={"reader"}, organization_id=uuid4()
                )
            )
        )


def test_dummy_jwt_supports_custom_claims_and_explicit_zero_expiry(
    endpoint_client: EndpointTestClient,
) -> None:
    """Preserve supplied claims and encode a zero expiration explicitly."""
    token = endpoint_client.get_dummy_jwt(
        "user@example.org", iss="issuer", sub="subject", aud="audience", exp=0
    )
    claims = jwt.decode(
        token,
        options={"verify_signature": False, "verify_exp": False},
    )
    assert claims["__key__"] == "user@example.org"
    assert claims["email"] == "user@example.org"
    assert claims["iss"] == "issuer"
    assert claims["sub"] == "subject"
    assert claims["aud"] == "audience"
    assert claims["exp"] == 0

    header = endpoint_client.get_dummy_jwt_header(
        "user@example.org", expire_default_minutes=0
    )
    assert set(header) == {"Authorization"}
    assert header["Authorization"].startswith("Bearer ")


@pytest.mark.parametrize(
    ("operation", "args", "method", "path", "extra"),
    [
        pytest.param(
            CrudOperation.READ_ALL,
            {},
            "get",
            "/v2/organizations",
            {"headers": None},
            id="read-all",
        ),
        pytest.param(
            CrudOperation.READ_SOME,
            "ids",
            "get",
            "/v2/organizations/batch",
            "ids-param",
            id="read-some",
        ),
        pytest.param(
            CrudOperation.READ_ONE,
            "id",
            "get",
            "id-path",
            {"headers": None},
            id="read-one",
        ),
        pytest.param(
            CrudOperation.CREATE_ONE,
            "object",
            "post",
            "/v2/organizations",
            "object-json",
            id="create-one",
        ),
        pytest.param(
            CrudOperation.CREATE_SOME,
            "objects",
            "post",
            "/v2/organizations/batch",
            "objects-json",
            id="create-some",
        ),
        pytest.param(
            CrudOperation.UPDATE_ONE,
            "object",
            "put",
            "object-path",
            "object-json",
            id="update-one",
        ),
        pytest.param(
            CrudOperation.UPDATE_SOME,
            "objects",
            "put",
            "/v2/organizations",
            "objects-json",
            id="update-some",
        ),
        pytest.param(
            CrudOperation.DELETE_ONE,
            "id",
            "delete",
            "id-path",
            {"headers": None},
            id="delete-one",
        ),
        pytest.param(
            CrudOperation.DELETE_SOME,
            "ids",
            "delete",
            "/v2/organizations/batch",
            "ids-param",
            id="delete-some",
        ),
    ],
)
def test_handle_crud_command_maps_supported_operations(
    endpoint_client: EndpointTestClient,
    organization: model.Organization,
    operation: CrudOperation,
    args: str | dict,
    method: str,
    path: str,
    extra: str | dict,
) -> None:
    """Map each supported CRUD operation to its expected HTTP request."""
    identifier = organization.id
    assert identifier is not None
    if args == "ids":
        command_args = {"obj_ids": [identifier]}
    elif args == "id":
        command_args = {"obj_ids": identifier}
    elif args == "object":
        command_args = {"objs": organization}
    elif args == "objects":
        command_args = {"objs": [organization]}
    else:
        command_args = args
    cmd = command.OrganizationCrudCommand(operation=operation, **command_args)

    if path == "id-path":
        path = f"/v2/organizations/{identifier}"
    elif path == "object-path":
        path = f"/v2/organizations/{identifier}"

    result, response = endpoint_client.handle_crud_command(cmd, "/v2", None)

    assert result is None
    assert response.status_code == 400
    request = getattr(endpoint_client.test_client, method)
    if extra == "ids-param":
        request.assert_called_once_with(
            path,
            headers=None,
            params={"ids": json.dumps([str(identifier)])},
        )
    elif extra == "object-json":
        request.assert_called_once_with(
            path,
            json=json.loads(organization.model_dump_json()),
            headers=None,
        )
    elif extra == "objects-json":
        request.assert_called_once_with(
            path,
            json=[json.loads(organization.model_dump_json())],
            headers=None,
        )
    else:
        request.assert_called_once_with(path, **extra)


def test_handle_crud_command_reads_filtered_all_and_rejects_unsupported(
    endpoint_client: EndpointTestClient,
) -> None:
    """Post filtered reads and reject CRUD operations without an endpoint."""
    query_filter = EqualsStringFilter(key="name", value="Organization")
    cmd = command.OrganizationCrudCommand(
        operation=CrudOperation.READ_ALL, query_filter=query_filter
    )
    endpoint_client.handle_crud_command(cmd, "/v1", None)
    endpoint_client.test_client.post.assert_called_once_with(
        "/v1/organizations/query",
        json=json.loads(query_filter.model_dump_json()),
        headers=None,
    )

    unsupported = command.OrganizationCrudCommand(
        operation=CrudOperation.EXISTS_ONE, obj_ids=uuid4()
    )
    with pytest.raises(NotImplementedError, match="Unsupported operation"):
        endpoint_client.handle_crud_command(unsupported, "/v1", None)


@pytest.mark.parametrize(
    ("status_code", "retval_class", "payload", "is_list", "expected"),
    [
        pytest.param(
            200,
            model.Organization,
            {"code": "org", "name": "Org"},
            False,
            "model",
            id="model-one",
        ),
        pytest.param(
            201,
            model.Organization,
            [{"code": "org", "name": "Org"}],
            True,
            "models",
            id="model-list",
        ),
        pytest.param(200, UUID, str(UUID(int=1)), False, UUID(int=1), id="uuid-one"),
        pytest.param(
            201,
            UUID,
            [str(UUID(int=1)), str(UUID(int=2))],
            True,
            [UUID(int=1), UUID(int=2)],
            id="uuid-list",
        ),
        pytest.param(
            204, model.Organization, None, False, None, id="unsuccessful-status"
        ),
    ],
)
def test_content_to_obj_deserializes_supported_response_shapes(
    status_code: int,
    retval_class: type,
    payload: object,
    is_list: bool,
    expected: object,
) -> None:
    """Deserialize models and UUIDs from successful response body shapes."""
    response = Response(status_code, json=payload)
    result = EndpointTestClient._content_to_obj(response, retval_class, is_list)

    if expected == "model":
        assert result == model.Organization(code="org", name="Org")
    elif expected == "models":
        assert result == [model.Organization(code="org", name="Org")]
    else:
        assert result == expected


def test_content_to_obj_rejects_unsupported_return_class() -> None:
    """Reject response types that are neither Pydantic models nor UUIDs."""
    response = Response(200, json={"value": "unsupported"})
    with pytest.raises(NotImplementedError, match="Unsupported return type"):
        EndpointTestClient._content_to_obj(response, str)
