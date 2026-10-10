"""Unit tests for the shared commondb test client."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.test import test_client as test_client_module
from gen_epix.commondb.test.test_client import TestClient as CommondbTestClient
from gen_epix.fastapp.enum import CrudOperation


@pytest.fixture
def client() -> CommondbTestClient:
    """Create a test client without constructing an application."""
    instance = object.__new__(CommondbTestClient)
    instance.db = {}
    instance.use_endpoints = False
    instance.user_class = model.User
    instance.organization_admin_policy_class = model.OrganizationAdminPolicy
    instance.role_map = {enum.Role.ROOT: "root", enum.Role.GUEST: "guest"}
    instance.rev_role_map = {"root": enum.Role.ROOT, "guest": enum.Role.GUEST}
    instance.role_set_map = {enum.RoleSet.ROOT: {"root"}}
    instance.role_permissions_map = {
        "root": {"read", "write"},
        "guest": {"read"},
    }
    return instance


def _organization(name: str = "Org", code: str | None = None) -> model.Organization:
    return model.Organization(id=uuid4(), name=name, code=code or name)


def _user(organization_id: UUID | None = None, **kwargs: Any) -> model.User:
    return model.User(
        id=kwargs.pop("id", uuid4()),
        key=kwargs.pop("key", "user@example.org"),
        email=kwargs.pop("email", "user@example.org"),
        name=kwargs.pop("name", "User"),
        organization_id=organization_id or uuid4(),
        roles=kwargs.pop("roles", {"guest"}),
        **kwargs,
    )


def _construct_client(**kwargs: Any) -> CommondbTestClient:
    role_map = {enum.Role.ROOT: "root", enum.Role.GUEST: "guest"}
    implementation = SimpleNamespace(
        get_mapped_class=lambda mapped: mapped,
        role_map=role_map,
        rev_role_map={value: key for key, value in role_map.items()},
        role_set_map={},
        role_permissions_map={},
        services={},
        repositories={},
    )
    app = SimpleNamespace(impl=implementation, cfg={})
    composer = SimpleNamespace(app=app)
    config = SimpleNamespace(app_name="commondb")
    return CommondbTestClient("test", Path("."), config, composer, **kwargs)


def test_constructor_validates_endpoint_dependencies_and_preserves_props(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(test_client_module, "set_log_level", lambda *args: None)
    with pytest.raises(ValueError, match="Endpoint test client not provided"):
        _construct_client(use_endpoints=True)
    with pytest.raises(ValueError, match="App last handled exception not provided"):
        _construct_client(use_endpoints=True, endpoint_test_client=object())

    endpoint_client = object()
    exception_state = {"id": 0, "exception": None}
    client = _construct_client(
        use_endpoints=True,
        endpoint_test_client=endpoint_client,
        app_last_handled_exception=exception_state,
        custom_prop="kept",
        default_route_prefix="/custom",
    )
    assert client.endpoint_test_client is endpoint_client
    assert client.app_last_handled_exception is exception_state
    assert client.props == {"custom_prop": "kept"}
    assert client.default_route_prefix == "/custom"


def test_get_obj_list_propagates_copy_and_missing_options(
    client: CommondbTestClient,
) -> None:
    stored = _organization()
    client.set_obj(stored)
    result = client.get_obj(
        model.Organization,
        ["Org", "Missing"],
        copy=True,
        on_missing="return_none",
    )
    assert result[0] == stored
    assert result[0] is not stored
    assert result[1] is None


def test_object_store_supports_duplicates_updates_and_deletes(
    client: CommondbTestClient,
) -> None:
    original, replacement = _organization(), _organization()
    client.set_obj(original)
    with pytest.raises(ValueError, match="already exists"):
        client.set_obj(replacement)
    assert client.set_obj(replacement, update=True) is replacement
    assert client.get_obj(model.Organization, "Org") is replacement
    assert client.delete_obj(model.Organization, replacement.id) is replacement
    with pytest.raises(ValueError, match="not found"):
        client.delete_obj(model.Organization, replacement.id)


def test_get_obj_handles_missing_and_invalid_references(
    client: CommondbTestClient,
) -> None:
    with pytest.raises(ValueError, match="not found"):
        client.get_obj(model.Organization, "missing")
    with pytest.raises(NotImplementedError):
        client.get_obj(model.Organization, "missing", on_missing="ignore")
    assert client.get_obj(model.Organization, uuid4(), on_missing="return_none") is None
    with pytest.raises(ValueError, match="Invalid object"):
        client._get_obj_key({}, model.Organization, object(), "raise")


def test_get_obj_key_supports_keys_ids_models_and_composite_keys(
    client: CommondbTestClient,
) -> None:
    organization = _organization()
    first_id, second_id = uuid4(), uuid4()
    link = model.OrganizationIdentifierIssuerLink(
        organization_id=first_id, identifier_issuer_id=second_id
    )
    assert client._get_obj_key({}, model.Organization, "Org", "raise") == "Org"
    assert (
        client._get_obj_key(
            {"Org": organization}, model.Organization, organization.id, "raise"
        )
        == "Org"
    )
    assert client._get_obj_key({}, model.Organization, organization, "raise") == "Org"
    assert client._get_obj_key(
        {}, model.OrganizationIdentifierIssuerLink, (first_id, second_id), "raise"
    ) == (first_id, second_id)
    assert client._get_key_for_obj(link) == (first_id, second_id)


def test_handle_dispatches_directly_and_through_endpoint() -> None:
    cmd = object()
    client = object.__new__(CommondbTestClient)
    client.app = SimpleNamespace(handle=lambda value: ("direct", value))
    client.use_endpoints = False
    assert client.handle(cmd) == ("direct", cmd)

    response = object()

    class Endpoint:
        def handle(self, value, **kwargs):
            assert value is cmd
            return "endpoint", response

    client.use_endpoints = True
    client.default_route_prefix = "/v1"
    client.endpoint_test_client = Endpoint()
    client.app_last_handled_exception = {"id": 1, "exception": None}
    assert client.handle(cmd, return_response=True) == ("endpoint", response)
    assert client.handle(cmd) == "endpoint"


def test_handle_reraises_endpoint_exception() -> None:
    exception = RuntimeError("endpoint failed")
    state = {"id": 1, "exception": None}

    class Endpoint:
        def handle(self, cmd, **kwargs):
            state.update(id=2, exception=exception)
            return None, None

    client = object.__new__(CommondbTestClient)
    client.use_endpoints = True
    client.endpoint_test_client = Endpoint()
    client.app_last_handled_exception = state
    client.default_route_prefix = "/v1"
    with pytest.raises(RuntimeError, match="endpoint failed"):
        client.handle(object())


def test_command_helpers_create_and_store_objects(client: CommondbTestClient) -> None:
    user = _user(name="root")
    organization = _organization()
    client.set_obj(user)
    client.set_obj(organization)

    def handle(cmd: Any) -> Any:
        obj = getattr(cmd, "objs", None)
        if obj is not None and obj.id is None:
            obj.id = uuid4()
        return obj

    client.app = SimpleNamespace(handle=handle)
    client.organization_admin_policy_crud_command_class = (
        command.OrganizationAdminPolicyCrudCommand
    )
    created_org = client.create_organization(user, "New Org")
    collection = client.create_data_collection(user, "Data")
    issuer = client.create_identifier_issuer(user, "code")
    policy = client.create_org_admin_policy(user, user, organization)
    link = client.create_organization_identifier_issuer_link(user, organization, issuer)

    assert created_org.name == "New Org"
    assert client.get_obj(model.DataCollection, "Data") is collection
    assert client.get_obj(model.IdentifierIssuer, "code") is issuer
    assert policy.organization_id == organization.id
    assert link.identifier_issuer_id == issuer.id


def test_user_lookup_and_read_wrappers(client: CommondbTestClient) -> None:
    user = _user(name="Reader")
    client.set_obj(user)
    client.app = SimpleNamespace(
        handle=lambda cmd: [cmd],
        user_manager=SimpleNamespace(retrieve_user_by_key=lambda key: user),
    )
    client.user_invitation_crud_command_class = command.UserInvitationCrudCommand
    client.retrieve_organization_admin_name_emails_command_class = (
        command.RetrieveOrganizationAdminNameEmailsCommand
    )
    client.get_root_user = lambda *args, **kwargs: user
    client.handle = lambda cmd, **kwargs: [cmd]

    assert client.retrieve_user_by_key("reader") is user
    assert client.read_all_user_invitations(user)[0].user is user
    assert client.read_organization_admin_name_emails(user)[0].user is user


def test_read_all_users_role_filter_and_role_check(
    client: CommondbTestClient,
) -> None:
    root = _user(name="Root", roles={"root"})
    guest = _user(name="Guest", roles={"guest"})
    client.set_obj(guest)
    client.user_crud_command_class = command.UserCrudCommand
    client.get_root_user = lambda *args, **kwargs: root
    client.app = SimpleNamespace(handle=lambda cmd: [root, guest])
    assert client.read_all_users() == [root, guest]
    assert client.read_users_by_role("guest") == [guest]
    assert client.verify_user_has_role(guest, "guest")
    assert not client.verify_user_has_role(guest, "root", exclusive=False)


def test_root_user_uses_configured_key(client: CommondbTestClient) -> None:
    user = _user(name="Root")
    client.cfg = {
        "service": {"auth": {"props": {"root": {"user": {"key": "root-key"}}}}}
    }
    client.app = SimpleNamespace(
        user_manager=SimpleNamespace(retrieve_user_by_key=lambda key: user)
    )
    assert client.get_root_user() is user


def test_admin_user_filters_cover_missing_inactive_and_peer_cases(
    client: CommondbTestClient,
) -> None:
    org_id = uuid4()
    admin = _user(org_id, name="Admin")
    inactive = _user(org_id, name="Inactive", is_active=False)
    peer = _user(uuid4(), name="Peer")
    client.set_obj(admin)
    client.set_obj(inactive)
    client.set_obj(peer)
    client.db[model.OrganizationAdminPolicy] = {}
    with pytest.raises(ValueError, match="not an organization admin"):
        client.get_org_ids_for_org_admin(admin)
    assert client.get_org_ids_for_org_admin(admin, on_no_admin="return") == []
    with pytest.raises(ValueError, match="not an organization admin"):
        client.get_users_for_org_admin(admin)
    assert client.get_users_for_org_admin(admin, on_no_admin="return") == []

    client.db[model.OrganizationAdminPolicy] = {
        1: model.OrganizationAdminPolicy(
            organization_id=org_id, user_id=admin.id, is_active=True
        ),
        2: model.OrganizationAdminPolicy(
            organization_id=org_id, user_id=peer.id, is_active=True
        ),
    }
    assert set(client.get_org_ids_for_org_admin(admin, include_self=True)) == {
        org_id,
        admin.organization_id,
    }
    assert client.get_own_org_admin_users(admin) == [admin, peer]
    assert client.get_own_org_admin_users(admin, include_self=True) == [admin, peer]
    assert client.get_users_for_org_admin(
        admin, include_self=True, include_other_org_admins=True
    ) == [admin, inactive, peer]
    assert client.get_users_for_org(admin) == [admin, inactive]


def test_role_hierarchy_and_property_lookup(client: CommondbTestClient, monkeypatch):
    assert client.is_sub_role("guest", "root")
    assert not client.is_sub_role("root", "root")
    assert client.is_sub_role("root", "root", allow_equal=True)
    matches = []
    monkeypatch.setattr(
        client, "read_some_by_property", lambda *args, **kwargs: matches
    )
    with pytest.raises(ValueError, match="not found"):
        client.read_one_by_property(_user(), model.Organization, "name", "Org")
    matches.extend([_organization("One"), _organization("Two")])
    with pytest.raises(ValueError, match="Multiple"):
        client.read_one_by_property(_user(), model.Organization, "name", "Org")


def test_cascade_reads_preserve_fk_and_attach_relationship(
    client: CommondbTestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    organization = _organization()
    user = _user(organization.id)
    monkeypatch.setattr(client, "read_some", lambda *args, **kwargs: [organization])
    client._add_linked_objs(user, model.User, [user])
    assert user.organization_id == organization.id
    assert user.organization is organization

    calls: list[tuple[Any, ...]] = []
    monkeypatch.setattr(client, "read_some", lambda *args, **kwargs: calls.append(args))
    user.organization_id = None
    client._add_linked_objs(user, model.User, [])
    client._add_linked_objs(user, model.User, [user])
    assert calls == []


def test_read_operations_and_property_filters(client: CommondbTestClient) -> None:
    user = _user()
    organization = _organization()
    client.set_obj(user)
    client.app = SimpleNamespace(
        domain=SimpleNamespace(
            get_crud_command_for_model=lambda cls: lambda **kwargs: kwargs
        )
    )
    client.handle = lambda cmd, **kwargs: [organization]
    assert client.read_all(user, model.Organization) == [organization]
    assert client.read_some(user, model.Organization, {organization.id}) == [
        organization
    ]
    assert client.read_some_by_property(user, model.Organization, "name", "Org") == [
        organization
    ]
    assert (
        client.read_one_by_property(user, model.Organization, "name", "Org")
        is organization
    )


def test_update_object_properties_resolve_links_and_dummy_defaults(
    client: CommondbTestClient,
) -> None:
    organization = _organization()
    client.set_obj(organization)
    user = _user()
    dummy_id = uuid4()
    client.app = SimpleNamespace(generate_id=lambda: dummy_id)
    client._update_object_properties(
        user, {"name": "Updated", "organization": organization}
    )
    assert user.name == "Updated"
    assert user.organization_id == organization.id
    client._update_object_properties(user, {"organization": None}, set_dummy_link=True)
    assert user.organization_id == dummy_id
    assert client._get_dummy_link_defaults(True) == ({}, True)
    assert client._get_dummy_link_defaults({"organization_id": True}) == (
        {"organization_id": True},
        False,
    )
    with pytest.raises(ValueError, match="set dummy link True"):
        client._update_object_properties(
            user, {"organization": organization}, set_dummy_link=True
        )


def test_update_and_delete_object_paths(client: CommondbTestClient) -> None:
    user = _user(roles={"root"})
    organization = _organization()
    client.set_obj(user)
    client.set_obj(organization)
    client.role_set_map = {enum.RoleSet.ROOT: {"root"}}
    client.app = SimpleNamespace(
        domain=SimpleNamespace(
            get_crud_command_for_model=lambda cls: lambda **kwargs: SimpleNamespace(
                **kwargs
            )
        ),
        handle=lambda cmd: cmd.objs if hasattr(cmd, "objs") else cmd.obj_ids,
    )
    updated = client.update_object(
        user, model.Organization, organization, {"name": "Changed"}
    )
    assert updated.name == "Changed"
    assert client.get_obj(model.Organization, "Changed") is updated
    client.app.handle = lambda cmd: (
        False if cmd.operation == CrudOperation.EXISTS_ONE else cmd.obj_ids
    )
    deleted_id = client.delete_object(user, model.Organization, updated, verify=True)
    assert deleted_id == updated.id


def test_delete_object_reports_failed_verification(client: CommondbTestClient) -> None:
    user = _user()
    organization = _organization()
    client.set_obj(user)
    client.set_obj(organization)
    client.app = SimpleNamespace(
        domain=SimpleNamespace(
            get_crud_command_for_model=lambda cls: lambda **kwargs: SimpleNamespace(
                **kwargs
            )
        ),
        handle=lambda cmd: True,
    )
    with pytest.raises(ValueError, match="not deleted"):
        client.delete_object(user, model.Organization, organization, verify=True)


def test_update_user_rejects_conflicting_options_and_updates_fields(
    client: CommondbTestClient,
) -> None:
    user = _user(name="Admin", roles={"root"})
    target = _user(name="Target")
    organization = _organization("Other")
    client.set_obj(user)
    client.set_obj(target)
    client.set_obj(organization)
    client.update_user_command_class = command.UpdateUserCommand
    client.handle = lambda cmd, **kwargs: target.model_copy(
        update={
            "is_active": cmd.is_active,
            "roles": cmd.roles,
            "organization_id": cmd.organization_id,
        }
    )
    with pytest.raises(ValueError, match="Organization given"):
        client.update_user(
            user, target, organization_or_str="Other", set_dummy_organization=True
        )
    updated = client.update_user(
        user,
        target,
        is_active=False,
        roles={"reader"},
        organization_or_str="Other",
    )
    assert not updated.is_active
    assert updated.roles == {"reader"}
    assert updated.organization_id == organization.id


def test_anonymize_user_rekeys_local_entry(client: CommondbTestClient) -> None:
    user = _user(name="Admin", roles={"root"})
    target = _user(name="Target", key="target@example.org")
    anonymized = target.model_copy(update={"email": None, "name": None})
    client.set_obj(user)
    client.set_obj(target)
    client.handle = lambda cmd, **kwargs: anonymized
    result = client.anonymize_user(user, target)
    assert result.name == target.key
    assert client.get_obj(model.User, target.key) is result


def test_verify_read_all_accepts_ids_or_models_and_reports_difference(
    client: CommondbTestClient,
) -> None:
    user = _user(name="Reader")
    organization = _organization()
    client.set_obj(user)
    client.set_obj(organization)
    client.app = SimpleNamespace(
        domain=SimpleNamespace(
            get_crud_command_for_model=lambda cls: lambda **kwargs: kwargs
        )
    )
    client.handle = lambda cmd, **kwargs: [organization]
    client.verify_read_all(user, model.Organization, {organization.id})
    client.verify_read_all(user, model.Organization, [organization])
    with pytest.raises(ValueError, match="Difference in read all"):
        client.verify_read_all(user, model.Organization, set())


def test_invitation_helper_rejects_invalid_name_and_missing_organization(
    client: CommondbTestClient,
) -> None:
    user = _user(name="Admin", roles={"root"})
    client.set_obj(user)
    client.get_root_user = lambda *args, **kwargs: user
    client.db[model.Organization] = {}
    with pytest.raises(ValueError, match="Invalid user name"):
        client.invite_and_register_user(user, "not-a-role-name")
    with pytest.raises(ValueError, match="Organization org1 not found"):
        client.invite_and_register_user(user, "guest1_1")


def test_print_methods_handle_empty_and_populated_results(
    client: CommondbTestClient,
    capsys: pytest.CaptureFixture[str],
) -> None:
    organization = _organization()
    user = _user(organization.id, name="Alice")
    collection = model.DataCollection(id=uuid4(), name="Data")
    issuer = model.IdentifierIssuer(id=uuid4(), code="issuer", name="Issuer")
    client.role_map = {enum.Role.ROOT: "root", enum.Role.GUEST: "guest"}
    client.rev_role_map = {"guest": enum.Role.GUEST}
    client.get_root_user = lambda *args, **kwargs: user
    client.set_obj(user)
    values = {
        model.Organization: [organization],
        model.DataCollection: [collection],
        model.User: [user],
        model.OrganizationAdminPolicy: [],
        model.IdentifierIssuer: [issuer],
        model.OrganizationIdentifierIssuerLink: [],
    }
    client.read_all = lambda user_arg, cls, **kwargs: values.get(cls, [])
    client.read_some = lambda user_arg, cls, ids: values.get(cls, [])
    client.app = SimpleNamespace(
        user_manager=SimpleNamespace(retrieve_user_permissions=lambda user_arg: [])
    )
    client.print_organizations()
    client.print_data_collections()
    client.print_users()
    client.print_user_permissions(user)
    client.print_org_admin_policies()
    client.print_identifier_issuers()
    client.print_organization_identifier_issuer_links()
    output = capsys.readouterr().out
    assert "Org (" in output
    assert "Data (" in output
    assert "Alice" in output
    assert "OrganizationIdentifierIssuerLinks:" in output


def test_set_log_level_uses_lowercase_app_name(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []
    monkeypatch.setattr(
        test_client_module, "set_log_level", lambda *args: calls.append(args)
    )
    CommondbTestClient._set_log_level(SimpleNamespace(app_name="CommonDB"), 20)
    assert calls == [("commondb", 20)]


def test_verify_updated_obj_ignores_metadata_and_reports_mismatch() -> None:
    original = _organization()
    updated = original.model_copy()
    CommondbTestClient._verify_updated_obj(original, updated, uuid4())
    updated.name = "Different"
    with pytest.raises(ValueError, match="Object not updated"):
        CommondbTestClient._verify_updated_obj(original, updated, uuid4())
