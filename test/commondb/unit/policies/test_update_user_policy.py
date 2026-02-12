from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb import enum
from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.model.organization import User
from gen_epix.commondb.policies.update_user_policy import UpdateUserPolicy


def _make_role_set_map() -> dict[enum.RoleSet, set[str]]:
    return {
        enum.RoleSet.ROOT: {enum.Role.ROOT.value},
        enum.RoleSet.GE_APP_ADMIN: {enum.Role.ROOT.value, enum.Role.APP_ADMIN.value},
        enum.RoleSet.GE_ORG_ADMIN: {
            enum.Role.ROOT.value,
            enum.Role.APP_ADMIN.value,
            enum.Role.ORG_ADMIN.value,
        },
        enum.RoleSet.LT_ORG_ADMIN: {enum.Role.ORG_USER.value, enum.Role.GUEST.value},
    }


def _make_abac_service(role_set_map: dict[enum.RoleSet, set[str]]) -> Mock:
    abac_service: Mock = Mock()
    abac_service.app = Mock()
    abac_service.app.impl = Mock()
    abac_service.app.impl.get_mapped_class.return_value = User
    abac_service.app.impl.role_map = {r: r.value for r in enum.Role}
    abac_service.app.impl.role_set_map = role_set_map
    abac_service.app.user_manager = Mock()
    abac_service.retrieve_organizations_under_admin = Mock()
    return abac_service


def _make_policy(abac_service: Mock) -> UpdateUserPolicy:
    return UpdateUserPolicy(abac_service=abac_service)


def _make_user(
    roles: set[str],
    organization_id: UUID | None = None,
    key: str = "user@example.com",
) -> User:
    return User(
        id=uuid4(),
        key=key,
        email=key,
        roles=roles,
        organization_id=organization_id or uuid4(),
        is_active=True,
    )


def _make_invite_cmd(
    inviter: User,
    invite_key: str,
    invite_roles: set[str],
    organization_id: UUID,
    email: str | None = None,
) -> Mock:
    invite_cmd: Mock = Mock(spec=command.InviteUserCommand)
    invite_cmd.user = inviter
    invite_cmd.key = invite_key
    invite_cmd.model_dump.return_value = {
        "id": None,
        "key": invite_key,
        "email": email or invite_key,
        "roles": invite_roles,
        "organization_id": organization_id,
        "is_active": True,
    }
    return invite_cmd


def _make_update_cmd(
    actor: User,
    tgt_user_id: UUID,
    roles: set[str] | None,
    organization_id: UUID | None,
) -> Mock:
    update_cmd: Mock = Mock(spec=command.UpdateUserCommand)
    update_cmd.user = actor
    update_cmd.tgt_user_id = tgt_user_id
    update_cmd.roles = roles
    update_cmd.organization_id = organization_id
    return update_cmd


def _set_permission_side_effect(
    abac_service: Mock,
    actor: User,
    target: User,
    actor_permissions: set[str],
    target_permissions: set[str],
) -> None:
    def _retrieve_user_permissions(u: User) -> set[str]:
        if u.id == actor.id:
            return actor_permissions
        if u.id == target.id:
            return target_permissions
        return set()

    abac_service.app.user_manager.retrieve_user_permissions.side_effect = (
        _retrieve_user_permissions
    )


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestInitialChecks:
    def test_user_none_returns_false(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        cmd: Mock = Mock(spec=command.InviteUserCommand)
        cmd.user = None

        allowed: bool = policy.is_allowed(cmd)

        assert allowed is False

    def test_unrecognized_command_raises_not_implemented(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        user: User = _make_user({enum.Role.ORG_USER.value})
        bad_cmd: Mock = Mock(spec=command.Command)
        bad_cmd.user = user

        with pytest.raises(NotImplementedError):
            policy.is_allowed(bad_cmd)


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestInviteCommand:
    def test_root_can_invite_anyone(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        root_user: User = _make_user({enum.Role.ROOT.value}, organization_id=uuid4())
        target_roles: set[str] = {enum.Role.APP_ADMIN.value, enum.Role.ORG_USER.value}
        invite_cmd: Mock = _make_invite_cmd(
            inviter=root_user,
            invite_key="invited@example.com",
            invite_roles=target_roles,
            organization_id=root_user.organization_id,
        )

        allowed: bool = policy.is_allowed(invite_cmd)

        assert allowed is True
        abac_service.app.user_manager.retrieve_user_by_id.assert_not_called()

    def test_invite_self_disallowed_even_for_root(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        root_user: User = _make_user({enum.Role.ROOT.value}, key="root@example.com")
        invite_cmd: Mock = _make_invite_cmd(
            inviter=root_user,
            invite_key="root@example.com",
            invite_roles={enum.Role.ORG_USER.value},
            organization_id=root_user.organization_id,
        )

        allowed: bool = policy.is_allowed(invite_cmd)

        assert allowed is False

    def test_app_admin_invite_target_with_less_permissions_allowed(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        app_admin: User = _make_user({enum.Role.APP_ADMIN.value})
        invite_cmd: Mock = _make_invite_cmd(
            inviter=app_admin,
            invite_key="newuser@example.com",
            invite_roles={enum.Role.ORG_USER.value},
            organization_id=app_admin.organization_id,
        )
        target_user: User = User(
            id=None,
            key="newuser@example.com",
            email="newuser@example.com",
            roles={enum.Role.ORG_USER.value},
            organization_id=app_admin.organization_id,
            is_active=True,
        )
        actor_permissions: set[str] = {"perm_a", "perm_b"}
        target_permissions: set[str] = {"perm_a"}
        _set_permission_side_effect(
            abac_service, app_admin, target_user, actor_permissions, target_permissions
        )

        allowed: bool = policy.is_allowed(invite_cmd)

        assert allowed is True

    def test_app_admin_invite_target_with_equal_permissions_disallowed(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        app_admin: User = _make_user({enum.Role.APP_ADMIN.value})
        invite_cmd: Mock = _make_invite_cmd(
            inviter=app_admin,
            invite_key="newuser@example.com",
            invite_roles={enum.Role.ORG_USER.value},
            organization_id=app_admin.organization_id,
        )
        target_user: User = User(
            id=None,
            key="newuser@example.com",
            email="newuser@example.com",
            roles={enum.Role.ORG_USER.value},
            organization_id=app_admin.organization_id,
            is_active=True,
        )
        actor_permissions: set[str] = {"perm_a", "perm_b"}
        target_permissions: set[str] = {"perm_a", "perm_b"}
        _set_permission_side_effect(
            abac_service, app_admin, target_user, actor_permissions, target_permissions
        )

        allowed: bool = policy.is_allowed(invite_cmd)

        assert allowed is False

    def test_user_below_org_admin_cannot_invite(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        org_user: User = _make_user({enum.Role.ORG_USER.value})
        invite_cmd: Mock = _make_invite_cmd(
            inviter=org_user,
            invite_key="newuser@example.com",
            invite_roles={enum.Role.ORG_USER.value},
            organization_id=org_user.organization_id,
        )

        allowed: bool = policy.is_allowed(invite_cmd)

        assert allowed is False


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestUpdateCommand:
    def test_root_can_update_anyone(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        root_user: User = _make_user({enum.Role.ROOT.value})
        target_user: User = _make_user({enum.Role.APP_ADMIN.value})
        update_cmd: Mock = _make_update_cmd(
            actor=root_user,
            tgt_user_id=uuid4(),
            roles={enum.Role.ORG_USER.value},
            organization_id=None,
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = target_user

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is True
        abac_service.app.user_manager.retrieve_user_by_id.assert_called_once_with(
            update_cmd.tgt_user_id
        )

    def test_app_admin_update_target_with_less_permissions_allowed(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        app_admin: User = _make_user({enum.Role.APP_ADMIN.value})
        existing_target: User = _make_user({enum.Role.ORG_USER.value})
        update_cmd: Mock = _make_update_cmd(
            actor=app_admin,
            tgt_user_id=uuid4(),
            roles=None,  # ensure branch where cmd.roles is None
            organization_id=None,
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = existing_target
        actor_permissions: set[str] = {"perm_a", "perm_b", "perm_c"}
        target_permissions: set[str] = {"perm_a", "perm_b"}
        _set_permission_side_effect(
            abac_service,
            app_admin,
            existing_target,
            actor_permissions,
            target_permissions,
        )

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is True
        assert abac_service.app.user_manager.retrieve_user_permissions.call_count == 2

    def test_app_admin_update_target_with_equal_permissions_disallowed(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        app_admin: User = _make_user({enum.Role.APP_ADMIN.value})
        existing_target: User = _make_user({enum.Role.ORG_USER.value})
        update_cmd: Mock = _make_update_cmd(
            actor=app_admin,
            tgt_user_id=uuid4(),
            roles={enum.Role.ORG_USER.value},  # union remains same size
            organization_id=None,
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = existing_target
        actor_permissions: set[str] = {"perm_a", "perm_b"}
        target_permissions: set[str] = {"perm_a", "perm_b"}
        _set_permission_side_effect(
            abac_service,
            app_admin,
            existing_target,
            actor_permissions,
            target_permissions,
        )

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is False

    def test_user_below_org_admin_cannot_update(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        org_user: User = _make_user({enum.Role.ORG_USER.value})
        existing_target: User = _make_user({enum.Role.GUEST.value})
        update_cmd: Mock = _make_update_cmd(
            actor=org_user,
            tgt_user_id=uuid4(),
            roles={enum.Role.GUEST.value},
            organization_id=None,
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = existing_target

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is False

    def test_org_admin_update_target_with_non_org_roles_disallowed(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        org_admin: User = _make_user({enum.Role.ORG_ADMIN.value})
        existing_target: User = _make_user({enum.Role.ORG_USER.value})
        update_cmd: Mock = _make_update_cmd(
            actor=org_admin,
            tgt_user_id=uuid4(),
            roles={
                enum.Role.ORG_ADMIN.value
            },  # target union includes ORG_ADMIN -> not subset of LT_ORG_ADMIN
            organization_id=None,
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = existing_target

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is False

    def test_org_admin_cannot_change_organization(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        org_admin: User = _make_user(
            {enum.Role.ORG_ADMIN.value}, organization_id=uuid4()
        )
        target_user_org: UUID = uuid4()
        existing_target: User = _make_user(
            {enum.Role.ORG_USER.value}, organization_id=target_user_org
        )
        update_cmd: Mock = _make_update_cmd(
            actor=org_admin,
            tgt_user_id=uuid4(),
            roles={enum.Role.ORG_USER.value},
            organization_id=uuid4(),  # different org than target
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = existing_target

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is False

    def test_org_admin_update_only_allowed_within_admin_orgs_and_less_permissions(
        self,
    ) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        org_id: UUID = uuid4()
        org_admin: User = _make_user(
            {enum.Role.ORG_ADMIN.value}, organization_id=org_id
        )
        existing_target: User = _make_user(
            {enum.Role.ORG_USER.value}, organization_id=org_id
        )
        update_cmd: Mock = _make_update_cmd(
            actor=org_admin,
            tgt_user_id=uuid4(),
            roles={enum.Role.GUEST.value},  # remains subset of LT_ORG_ADMIN
            organization_id=None,
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = existing_target
        abac_service.retrieve_organizations_under_admin.return_value = [org_id]
        actor_permissions: set[str] = {"perm_a", "perm_b", "perm_c"}
        target_permissions: set[str] = {"perm_a"}
        _set_permission_side_effect(
            abac_service,
            org_admin,
            existing_target,
            actor_permissions,
            target_permissions,
        )

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is True
        abac_service.retrieve_organizations_under_admin.assert_called_once()
        # Verify PDP command is constructed with correct type and actor
        pdp_cmd = abac_service.retrieve_organizations_under_admin.call_args[0][0]
        assert isinstance(pdp_cmd, command.RetrieveOrganizationsUnderAdminCommand)
        assert pdp_cmd.user == org_admin

    def test_org_admin_update_disallowed_when_not_admin_of_target_org(self) -> None:
        role_set_map: dict[enum.RoleSet, set[str]] = _make_role_set_map()
        abac_service: Mock = _make_abac_service(role_set_map)
        policy: UpdateUserPolicy = _make_policy(abac_service)
        org_admin: User = _make_user(
            {enum.Role.ORG_ADMIN.value}, organization_id=uuid4()
        )
        target_org: UUID = uuid4()
        existing_target: User = _make_user(
            {enum.Role.ORG_USER.value}, organization_id=target_org
        )
        update_cmd: Mock = _make_update_cmd(
            actor=org_admin,
            tgt_user_id=uuid4(),
            roles={enum.Role.GUEST.value},
            organization_id=None,
        )
        abac_service.app.user_manager.retrieve_user_by_id.return_value = existing_target
        abac_service.retrieve_organizations_under_admin.return_value = [
            uuid4()
        ]  # different org

        allowed: bool = policy.is_allowed(update_cmd)

        assert allowed is False
