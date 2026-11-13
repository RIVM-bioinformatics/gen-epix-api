from test.util.mock_compat import MagicMock, Mock
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain import command, enum, exc, model
from gen_epix.commondb.domain.policy import BaseReadOrganizationResultsOnlyPolicy
from gen_epix.commondb.services.abac import AbacService
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.enum import EventTiming


def make_service() -> AbacService:
    """Build an ABAC service with isolated mocked dependencies."""
    service = AbacService.__new__(AbacService)
    service._app = Mock()
    service.repository = MagicMock()
    service.organization_admin_policy_model_class = model.OrganizationAdminPolicy
    service.user_crud_command_class = command.UserCrudCommand
    service.role_set_map = {
        enum.RoleSet.GE_APP_ADMIN: frozenset(
            {enum.Role.ROOT.value, enum.Role.APP_ADMIN.value}
        )
    }
    service.app.get_feature_flag.return_value = True
    return service


def make_user(
    organization_id: UUID,
    roles: set[str] | None = None,
) -> model.User:
    """Build a persisted user for ABAC service tests."""
    user_id = uuid4()
    return model.User(
        id=user_id,
        key=str(user_id),
        email="user@example.org",
        name="Example User",
        roles=roles or {enum.Role.ORG_USER.value},
        organization_id=organization_id,
        is_active=True,
    )


def test_init_registers_cache_invalidator_and_maps_implementations() -> None:
    app = Mock()
    app.impl.get_mapped_class.side_effect = lambda cls: cls

    service = AbacService(app, repository=Mock(), register_handlers=False)

    assert (
        service.organization_admin_policy_model_class is model.OrganizationAdminPolicy
    )
    assert service.user_crud_command_class is command.UserCrudCommand
    app.register_cache_invalidator.assert_called_once_with(
        command.UpdateUserOwnOrganizationCommand, service._invalidate_cache
    )
    app.set_auto_invalidate_cache.assert_called_once_with(
        command.UpdateUserOwnOrganizationCommand, True
    )


def test_register_policies_uses_each_required_lifecycle_phase() -> None:
    service = make_service()
    service.is_organization_admin_policy_class = Mock(return_value="admin")
    service.read_user_policy_class = Mock(return_value="read-user")
    service.update_user_policy_class = Mock(return_value="update-user")
    service.read_organization_results_only_policy_class = Mock(
        return_value="read-organization"
    )
    service.read_self_results_only_policy_class = Mock(return_value="read-self")
    organization_admin_command = command.ContactCrudCommand
    read_user_command = command.UserCrudCommand
    update_user_command = command.UpdateUserCommand
    organization_results_command = command.RetrieveInviteUserConstraintsCommand
    read_self_command = command.RetrieveOrganizationAdminNameEmailsCommand

    service.register_policies(
        organization_admin_write_commands={organization_admin_command},
        read_user_commands={read_user_command},
        update_user_commands={update_user_command},
        read_organization_results_only_commands={organization_results_command},
        read_self_results_only_commands={read_self_command},
    )

    assert [call.args for call in service.app.register_policy.call_args_list] == [
        (organization_admin_command, "admin", EventTiming.BEFORE),
        (read_user_command, "read-user", EventTiming.AFTER),
        (update_user_command, "update-user", EventTiming.BEFORE),
        (organization_results_command, "read-organization", EventTiming.DURING),
        (organization_results_command, "read-organization", EventTiming.AFTER),
        (read_self_command, "read-self", EventTiming.AFTER),
    ]


def test_retrieve_organizations_under_admin_returns_active_policy_orgs() -> None:
    service = make_service()
    organization_id = uuid4()
    user = make_user(organization_id)
    service.repository.crud.return_value = [
        model.OrganizationAdminPolicy(
            user_id=user.id, organization_id=organization_id, is_active=True
        )
    ]
    cmd = SimpleNamespace(user=user, _policies=[])

    result = service.retrieve_organizations_under_admin(cmd)

    assert result == {organization_id}
    assert service.repository.crud.call_args.args[3] is CrudOperation.READ_ALL


def test_application_admin_retrieves_all_organizations() -> None:
    service = make_service()
    organization_id = uuid4()
    user = make_user(organization_id, {enum.Role.APP_ADMIN.value})
    organization = model.Organization(
        id=uuid4(), code="ORG", name="Example Organization"
    )
    service.app.handle.return_value = [organization]
    cmd = SimpleNamespace(
        user=user,
        _policies=[Mock(spec=BaseReadOrganizationResultsOnlyPolicy)],
    )

    result = service.retrieve_organizations_under_admin(cmd)

    assert result == {organization.id}
    service.app.handle.assert_called_once()
    assert service.app.handle.call_args.args[0].operation is CrudOperation.READ_ALL
    service.repository.crud.assert_not_called()


def test_retrieve_organization_admin_name_emails_filters_inactive_and_other_orgs() -> (
    None
):
    service = make_service()
    organization_id = uuid4()
    user = make_user(organization_id)
    admin = make_user(organization_id)
    other_org_admin = make_user(uuid4())
    service.repository.crud.return_value = [
        model.OrganizationAdminPolicy(
            user_id=admin.id, organization_id=organization_id, is_active=True
        ),
        model.OrganizationAdminPolicy(
            user_id=uuid4(), organization_id=organization_id, is_active=False
        ),
        model.OrganizationAdminPolicy(
            user_id=other_org_admin.id,
            organization_id=other_org_admin.organization_id,
            is_active=True,
        ),
    ]
    service.app.handle.return_value = [admin]

    result = service.retrieve_organization_admin_name_emails(
        command.RetrieveOrganizationAdminNameEmailsCommand(user=user)
    )

    assert result == [
        model.UserNameEmail(id=admin.id, name=admin.name, email=admin.email)
    ]
    user_command = service.app.handle.call_args.args[0]
    assert user_command.obj_ids == [admin.id]
    assert user_command.operation is CrudOperation.READ_SOME


def test_retrieve_organization_admin_name_emails_rejects_missing_user() -> None:
    service = make_service()

    with pytest.raises(exc.ServiceException):
        service.retrieve_organization_admin_name_emails(
            command.RetrieveOrganizationAdminNameEmailsCommand(user=None)
        )


def test_update_user_own_organization_deletes_previous_admin_policy() -> None:
    service = make_service()
    previous_organization_id = uuid4()
    target_organization_id = uuid4()
    user = make_user(previous_organization_id)
    updated_user = user.model_copy(update={"organization_id": target_organization_id})
    service.app.handle.return_value = updated_user

    result = service.update_user_own_organization(
        command.UpdateUserOwnOrganizationCommand(
            user=user, organization_id=target_organization_id
        )
    )

    assert result is updated_user
    service.repository.crud.assert_called_once()
    assert service.repository.crud.call_args.args[3] is CrudOperation.DELETE_ALL
    user_command = service.app.handle.call_args.args[0]
    assert user_command.operation is CrudOperation.UPDATE_ONE
    assert user_command.objs.organization_id == target_organization_id


def test_update_user_own_organization_skips_unchanged_user() -> None:
    service = make_service()
    organization_id = uuid4()
    user = make_user(organization_id)

    result = service.update_user_own_organization(
        command.UpdateUserOwnOrganizationCommand(
            user=user, organization_id=organization_id
        )
    )

    assert result is user
    service.repository.crud.assert_not_called()
    service.app.handle.assert_not_called()


def test_update_user_own_organization_skips_policy_delete_for_new_user() -> None:
    service = make_service()
    user = make_user(uuid4())
    service.app.handle.return_value = user

    service.update_user_own_organization(
        command.UpdateUserOwnOrganizationCommand(
            user=user, organization_id=uuid4(), is_new_user=True
        )
    )

    service.repository.crud.assert_not_called()
    service.app.handle.assert_called_once()


def test_update_user_own_organization_respects_feature_flag() -> None:
    service = make_service()
    service.app.get_feature_flag.return_value = False

    with pytest.raises(exc.FeatureDisabledServiceError):
        service.update_user_own_organization(
            command.UpdateUserOwnOrganizationCommand(
                user=make_user(uuid4()), organization_id=uuid4()
            )
        )

    service.repository.crud.assert_not_called()
    service.app.handle.assert_not_called()


def test_cached_user_lookup_reuses_and_invalidates_result() -> None:
    service = make_service()
    user = make_user(uuid4())
    service.app.handle.return_value = user
    user_id = UUID(str(user.id))
    AbacService._GET_USER_BY_ID_CACHE.clear()

    first_result = service._get_user_by_id_cached(user_id)
    second_result = service._get_user_by_id_cached(user_id)
    service._invalidate_cache(Mock())
    third_result = service._get_user_by_id_cached(user_id)

    assert first_result is user
    assert second_result is user
    assert third_result is user
    assert service.app.handle.call_count == 2
    AbacService._GET_USER_BY_ID_CACHE.clear()
