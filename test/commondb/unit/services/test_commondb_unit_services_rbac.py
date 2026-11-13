from types import SimpleNamespace

import pytest

from gen_epix.commondb.services.rbac import RbacService


def make_service(root_role: str = "root") -> RbacService:
    service = object.__new__(RbacService)
    service.root_role = root_role
    return service


def test_register_policies_delegates_to_rbac_registration(monkeypatch):
    service = make_service()
    calls = []
    monkeypatch.setattr(service, "register_rbac_policies", lambda: calls.append(True))

    service.register_policies()

    assert calls == [True]


def test_retrieve_user_roles_returns_assigned_roles():
    service = make_service()
    roles = {"reader", "editor"}

    assert service.retrieve_user_roles(SimpleNamespace(roles=roles)) is roles


@pytest.mark.parametrize(
    ("roles", "expected"),
    [(set(), False), ({"reader"}, False), ({"root"}, True)],
    ids=["no-roles", "non-root", "root"],
)
def test_retrieve_user_is_root_checks_configured_root_role(roles, expected):
    service = make_service()

    assert service.retrieve_user_is_root(SimpleNamespace(roles=roles)) is expected


@pytest.mark.parametrize(
    ("user", "expected"),
    [
        (None, False),
        (SimpleNamespace(is_active=False, roles={"reader"}), False),
        (SimpleNamespace(is_active=True, roles={"reader"}), True),
        (SimpleNamespace(is_active=False, roles={"root"}), True),
    ],
    ids=["anonymous", "inactive", "active", "inactive-root"],
)
def test_retrieve_user_is_non_rbac_authorized(user, expected):
    service = make_service()

    assert (
        service.retrieve_user_is_non_rbac_authorized(SimpleNamespace(user=user))
        is expected
    )


@pytest.mark.parametrize(
    "user",
    [None, SimpleNamespace(id=None)],
    ids=["anonymous", "missing-id"],
)
def test_retrieve_own_permissions_returns_empty_for_missing_user(user):
    service = make_service()

    assert service.retrieve_own_permissions(SimpleNamespace(user=user)) == set()


def test_retrieve_own_permissions_delegates_for_identified_user(monkeypatch):
    service = make_service()
    user = SimpleNamespace(id="user-1", roles={"reader"})
    permissions = {object()}
    monkeypatch.setattr(service, "retrieve_user_permissions", lambda value: permissions)

    assert service.retrieve_own_permissions(SimpleNamespace(user=user)) is permissions


@pytest.mark.parametrize(
    "user",
    [
        None,
        SimpleNamespace(id=None, roles={"reader"}),
        SimpleNamespace(id="user-1", roles=set()),
    ],
    ids=["anonymous", "missing-id", "no-roles"],
)
def test_retrieve_sub_roles_returns_empty_without_identified_roles(user):
    service = make_service()

    assert service.retrieve_sub_roles(SimpleNamespace(user=user)) == set()


def test_retrieve_sub_roles_unions_inherited_roles_and_includes_root(monkeypatch):
    service = make_service()
    inherited = {"reader": {"viewer"}, "root": {"editor"}}
    monkeypatch.setattr(service, "get_sub_roles", lambda role: inherited[role])
    user = SimpleNamespace(id="user-1", roles={"reader", "root"})

    assert service.retrieve_sub_roles(SimpleNamespace(user=user)) == {
        "viewer",
        "editor",
        "root",
    }
