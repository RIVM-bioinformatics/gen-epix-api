"""
Unit tests for OrganizationService.anonymize_user().

The tests verify that anonymizing a user anonymizes personal information while
preserving a deterministic, organization-scoped user key.
"""

from datetime import datetime, timedelta, timezone
from test.util.mock_compat import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain import command, exc, model
from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.commondb.services.organization import OrganizationService
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork

_ORGANIZATION_ID = UUID("550e8400-e29b-41d4-a716-446655440003")
_USER_ID = UUID("550e8400-e29b-41d4-a716-446655440000")


def _make_user(
    user_id: UUID | None = _USER_ID,
    organization_id: UUID = _ORGANIZATION_ID,
    key: str | None = "user@example.org",
) -> model.User:
    return model.User(
        id=user_id,
        key=key,
        roles={"COMMONDB_USER"},
        organization_id=organization_id,
        is_active=True,
    )


def _make_invitation(
    *,
    key: str | None = None,
    token: str = "invite-token",
    expires_at: datetime | None = None,
    invitation_id: UUID | None = None,
    organization_id: UUID = _ORGANIZATION_ID,
) -> model.UserInvitation:
    return model.UserInvitation(
        id=invitation_id or uuid4(),
        key=key,
        description="Invitation description",
        token=token,
        expires_at=expires_at or datetime.now(timezone.utc) + timedelta(days=1),
        roles={"COMMONDB_USER"},
        invited_by_user_id=_USER_ID,
        organization_id=organization_id,
    )


def _make_service() -> OrganizationService:
    repository = Mock()
    uow = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=False)
    repository.uow.return_value = uow

    service = OrganizationService.__new__(OrganizationService)
    service._repository = repository
    service._app = Mock()
    service._app.user_manager = Mock()
    service._app.user_manager.is_root_user.return_value = False
    service._app.user_manager.is_existing_user_by_key.return_value = False
    service.user_class = model.User
    service.user_invitation_class = model.UserInvitation
    service.user_invitation_constraints_class = model.UserInvitationConstraints
    service._props = {}
    service._logger = None
    service._id_factory = Mock(
        return_value=UUID("550e8400-e29b-41d4-a716-446655440010")
    )
    return service


@pytest.mark.scenario_ids("TC-COMMONDB-ORGANIZATION-FORGET-USER")
class TestAnonymizeUser:
    """Verify anonymization of the target user."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.admin_user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        self.tgt_user_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.organization_id = UUID("550e8400-e29b-41d4-a716-446655440003")

        # Admin user performing the anonymization
        self.admin_user = model.User(
            id=self.admin_user_id,
            key="admin@example.com",
            email="admin@example.com",
            name="Admin User",
            description="Admin description",
            roles={"COMMONDB_ADMIN"},
            organization_id=self.organization_id,
            is_active=True,
        )

        # Target user to be anonymized
        self.tgt_user = model.User(
            id=self.tgt_user_id,
            key="person@example.com",
            email="person@example.com",
            name="Person Example",
            description="Personal description",
            roles={"COMMONDB_USER"},
            organization_id=self.organization_id,
            is_active=True,
        )
        self.organization = model.Organization(
            id=self.organization_id,
            code="ORG",
            name="Example Organization",
        )

        self.repository = Mock()
        self.uow = Mock(spec=BaseUnitOfWork)
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.repository.uow.return_value = self.uow

        self.service = OrganizationService.__new__(OrganizationService)
        self.service._repository = self.repository
        self.service.user_class = model.User

    def test_anonymize_user_information(self) -> None:
        """Anonymize personal fields and deactivate the anonymized user."""
        # Setup mock side_effect for 2 crud calls: READ user, UPDATE user
        self.repository.crud.side_effect = [
            self.tgt_user,
            self.tgt_user,
        ]
        cmd = command.AnonymizeUserCommand(
            user=self.admin_user, tgt_user_id=self.tgt_user_id
        )

        anonymized_user = self.service.anonymize_user(cmd)

        assert anonymized_user is self.tgt_user
        assert anonymized_user.key == str(anonymized_user.id)
        assert anonymized_user.email is None
        assert anonymized_user.name is None
        assert anonymized_user.description is None
        assert anonymized_user.is_active is False
        assert self.repository.crud.call_count == 2
        assert self.repository.crud.call_args_list[0].args[3] == CrudOperation.READ_ONE
        assert (
            self.repository.crud.call_args_list[1].args[3] == CrudOperation.UPDATE_ONE
        )

    def test_anonymize_normalizes_organization_name_in_user_key(self) -> None:
        """Anonymize personal fields and deactivate the anonymized user."""
        # Setup mock side_effect for 2 crud calls: READ user, UPDATE user
        self.repository.crud.side_effect = [
            self.tgt_user,
            self.tgt_user,
        ]

        anonymized_user = self.service.anonymize_user(
            command.AnonymizeUserCommand(
                user=self.admin_user,
                tgt_user_id=self.tgt_user_id,
            )
        )

        assert anonymized_user.key == str(anonymized_user.id)
        assert anonymized_user.email is None
        assert anonymized_user.is_active is False

    def test_anonymize_keeps_keys_unique_for_users_in_same_organization(self) -> None:
        """Include each user ID so forgotten users in one organization remain unique."""
        second_user_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        second_user = self.tgt_user.model_copy(
            update={
                "id": second_user_id,
                "key": "second.person@example.com",
                "email": "second.person@example.com",
            }
        )
        # Setup mock side_effect for 4 crud calls:
        # First anonymization: READ user, UPDATE user
        # Second anonymization: READ user, UPDATE user
        self.repository.crud.side_effect = [
            self.tgt_user,
            self.tgt_user,
            second_user,
            second_user,
        ]

        first_anonymized_user = self.service.anonymize_user(
            command.AnonymizeUserCommand(
                user=self.admin_user, tgt_user_id=self.tgt_user_id
            )
        )
        second_anonymized_user = self.service.anonymize_user(
            command.AnonymizeUserCommand(
                user=self.admin_user, tgt_user_id=second_user_id
            )
        )

        # Both should have the same key (the admin user's ID)
        assert first_anonymized_user.key == str(first_anonymized_user.id)
        assert second_anonymized_user.key == str(second_anonymized_user.id)


class TestRetrieveOwnUser:
    """Verify retrieval of the user a command is executed as."""

    def test_retrieve_own_user_returns_the_command_user(self) -> None:
        """Return the authenticated user of the command unchanged."""
        user = model.User(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            key="functional-user-sub",
            roles={"COMMONDB_ADMIN"},
            organization_id=UUID("550e8400-e29b-41d4-a716-446655440003"),
            is_active=True,
        )
        service = OrganizationService.__new__(OrganizationService)

        result = service.retrieve_own_user(command.RetrieveOwnUserCommand(user=user))

        assert result is user

    def test_retrieve_own_user_without_a_user_is_unauthorized(self) -> None:
        """Refuse a command that carries no authenticated user."""
        service = OrganizationService.__new__(OrganizationService)

        with pytest.raises(exc.UnauthorizedAuthError):
            service.retrieve_own_user(command.RetrieveOwnUserCommand(user=None))

    def test_base_service_leaves_retrieve_own_user_to_concrete_services(self) -> None:
        """The abstract method has no behaviour of its own."""
        with pytest.raises(NotImplementedError):
            BaseOrganizationService.retrieve_own_user(
                Mock(), command.RetrieveOwnUserCommand(user=None)
            )


def test_service_initialization_registers_cache_invalidation() -> None:
    app = Mock()
    app.impl.get_mapped_class.side_effect = lambda model_class: model_class
    app.generate_id.return_value = "service-id"
    app.generate_timestamp.return_value = datetime.now(timezone.utc)

    service = OrganizationService(app, register_handlers=False)

    assert service.user_class is model.User
    assert service.user_invitation_class is model.UserInvitation
    assert service.user_invitation_constraints_class is model.UserInvitationConstraints
    assert app.register_cache_invalidator.call_count == 2
    assert app.set_auto_invalidate_cache.call_count == 2
    assert all(
        call.args[1] is True for call in app.set_auto_invalidate_cache.call_args_list
    )


def test_crud_delegates_for_non_root_delete(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _make_service()
    user = _make_user()
    cmd = command.UserCrudCommand(
        operation=CrudOperation.DELETE_ONE, obj_ids=uuid4(), user=user
    )
    monkeypatch.setattr(BaseOrganizationService, "crud", lambda _self, _cmd: "base")

    assert service.crud(cmd) == "base"


@pytest.mark.parametrize(
    ("command_class", "target_id"),
    [
        (command.UserCrudCommand, _USER_ID),
        (command.OrganizationCrudCommand, _ORGANIZATION_ID),
    ],
    ids=["self", "home-organization"],
)
def test_root_user_cannot_delete_self_or_home_organization(
    command_class: type[command.CrudCommand], target_id: UUID
) -> None:
    service = _make_service()
    service.app.user_manager.is_root_user.return_value = True
    cmd = command_class(
        operation=CrudOperation.DELETE_ONE,
        obj_ids=target_id,
        user=_make_user(),
    )

    with pytest.raises(exc.UnauthorizedAuthError):
        service.crud(cmd)


def test_root_user_cannot_delete_self_from_a_subset() -> None:
    service = _make_service()
    service.app.user_manager.is_root_user.return_value = True
    cmd = command.UserCrudCommand(
        operation=CrudOperation.DELETE_SOME,
        obj_ids=[uuid4(), _USER_ID],
        user=_make_user(),
    )

    with pytest.raises(exc.UnauthorizedAuthError):
        service.crud(cmd)


def test_root_user_can_delete_other_users(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _make_service()
    service.app.user_manager.is_root_user.return_value = True
    target_id = uuid4()
    cmd = command.UserCrudCommand(
        operation=CrudOperation.DELETE_ONE, obj_ids=target_id, user=_make_user()
    )
    monkeypatch.setattr(BaseOrganizationService, "crud", lambda _self, _cmd: "deleted")

    assert service.crud(cmd) == "deleted"


def test_root_user_cannot_delete_all_users() -> None:
    service = _make_service()
    service.app.user_manager.is_root_user.return_value = True
    cmd = command.UserCrudCommand(operation=CrudOperation.DELETE_ALL, user=_make_user())

    with pytest.raises(exc.UnauthorizedAuthError):
        service.crud(cmd)


def test_root_user_rejects_unsupported_delete_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _make_service()
    service.app.user_manager.is_root_user.return_value = True
    cmd = command.UserCrudCommand.model_construct(
        operation=CrudOperation.UNDELETE_ONE,
        obj_ids=uuid4(),
        user=_make_user(),
    )
    monkeypatch.setattr(command.UserCrudCommand, "is_delete", lambda _self: True)

    with pytest.raises(NotImplementedError, match="Unsupported delete operation"):
        service.crud(cmd)


def test_retrieve_user_by_key_caches_and_invalidates_results() -> None:
    service = _make_service()
    user = _make_user()
    service.repository.retrieve_user_by_key.return_value = user
    OrganizationService.retrieve_user_by_key.cache_clear()

    assert service.retrieve_user_by_key("cached@example.org") is user
    assert service.retrieve_user_by_key("cached@example.org") is user
    service.repository.retrieve_user_by_key.assert_called_once()

    service._invalidate_cache(command.UserCrudCommand(operation=CrudOperation.READ_ALL))
    assert service.retrieve_user_by_key("cached@example.org") is user
    assert service.repository.retrieve_user_by_key.call_count == 2


def test_invite_user_requires_an_authenticated_user() -> None:
    service = _make_service()
    cmd = command.InviteUserCommand(
        roles={"COMMONDB_USER"}, organization_id=_ORGANIZATION_ID
    )

    with pytest.raises(exc.UnauthorizedAuthError, match="no user"):
        service.invite_user(cmd)


def test_invite_user_requires_user_id() -> None:
    service = _make_service()
    cmd = command.InviteUserCommand(
        user=_make_user(user_id=None),
        roles={"COMMONDB_USER"},
        organization_id=_ORGANIZATION_ID,
    )

    with pytest.raises(exc.UnauthorizedAuthError, match="no ID"):
        service.invite_user(cmd)


def test_invite_user_rejects_an_existing_user_key() -> None:
    service = _make_service()
    service.app.user_manager.is_existing_user_by_key.return_value = True
    cmd = command.InviteUserCommand(
        user=_make_user(),
        key="existing@example.org",
        roles={"COMMONDB_USER"},
        organization_id=_ORGANIZATION_ID,
    )

    with pytest.raises(exc.UserAlreadyExistsAuthError):
        service.invite_user(cmd)


def test_invite_user_logs_existing_user_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _make_service()
    service.app.user_manager.is_existing_user_by_key.return_value = True
    service._logger = Mock()
    monkeypatch.setattr(
        OrganizationService, "create_log_message", lambda *_args, **_kwargs: "log"
    )
    cmd = command.InviteUserCommand(
        user=_make_user(),
        key="existing@example.org",
        roles={"COMMONDB_USER"},
        organization_id=_ORGANIZATION_ID,
    )

    with pytest.raises(exc.UserAlreadyExistsAuthError):
        service.invite_user(cmd)

    service._logger.info.assert_called_once_with("log")


def test_invite_user_rejects_a_missing_organization() -> None:
    service = _make_service()
    service.repository.crud.return_value = False
    cmd = command.InviteUserCommand(
        user=_make_user(),
        key="new@example.org",
        roles={"COMMONDB_USER"},
        organization_id=_ORGANIZATION_ID,
    )

    with pytest.raises(exc.InvalidIdsError):
        service.invite_user(cmd)


def test_invite_user_logs_missing_organization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _make_service()
    service.repository.crud.return_value = False
    service._logger = Mock()
    monkeypatch.setattr(
        OrganizationService, "create_log_message", lambda *_args, **_kwargs: "log"
    )
    cmd = command.InviteUserCommand(
        user=_make_user(),
        roles={"COMMONDB_USER"},
        organization_id=_ORGANIZATION_ID,
    )

    with pytest.raises(exc.InvalidIdsError):
        service.invite_user(cmd)

    service._logger.info.assert_called_once_with("log")


def test_invite_user_replaces_old_invites_and_persists_metadata() -> None:
    service = _make_service()
    user = _make_user()
    previous_invitation = _make_invitation(key="new@example.org")

    def crud(
        _uow: BaseUnitOfWork,
        _user_id: UUID | None,
        _model_class: type,
        operation: CrudOperation,
        objs: model.Model | list[model.Model] | None = None,
        **_kwargs: object,
    ) -> object:
        if operation == CrudOperation.EXISTS_ONE:
            return True
        if operation == CrudOperation.READ_ALL:
            return [previous_invitation]
        if operation == CrudOperation.CREATE_ONE:
            return objs
        return None

    service.repository.crud.side_effect = crud
    service._props = {"user_invitation_time_to_live": 120}
    started_at = datetime.now(timezone.utc)
    cmd = command.InviteUserCommand(
        user=user,
        key="new@example.org",
        email="new@example.org",
        name="New User",
        description="New invitation",
        roles={"COMMONDB_USER"},
        organization_id=_ORGANIZATION_ID,
    )

    invitation = service.invite_user(cmd)

    assert invitation.key == "new@example.org"
    assert invitation.email == "new@example.org"
    assert invitation.name == "New User"
    assert invitation.description == "New invitation"
    assert invitation.roles == {"COMMONDB_USER"}
    assert invitation.invited_by_user_id == user.id
    assert started_at + timedelta(seconds=120) <= invitation.expires_at
    assert invitation.expires_at <= datetime.now(timezone.utc) + timedelta(seconds=120)
    delete_call = next(
        call
        for call in service.repository.crud.call_args_list
        if call.args[3] == CrudOperation.DELETE_SOME
    )
    assert delete_call.kwargs["obj_ids"] == [previous_invitation.id]


def test_invite_user_does_not_read_existing_invites_for_keyless_invite() -> None:
    service = _make_service()
    service.repository.crud.side_effect = [True, _make_invitation(key=None)]
    cmd = command.InviteUserCommand(
        user=_make_user(),
        key=None,
        roles={"COMMONDB_USER"},
        organization_id=_ORGANIZATION_ID,
    )

    service.invite_user(cmd)

    assert service.repository.crud.call_count == 2
    assert all(
        call.args[3] != CrudOperation.READ_ALL
        for call in service.repository.crud.call_args_list
    )


def test_retrieve_invite_user_constraints_passes_policy_context() -> None:
    service = _make_service()
    user = _make_user()
    policy_context = {"policy": "context"}
    cmd = command.RetrieveInviteUserConstraintsCommand(user=user)
    cmd._policies = policy_context
    organization_ids = {_ORGANIZATION_ID}
    roles = {"COMMONDB_USER"}
    service.app.handle.side_effect = [organization_ids, roles]

    result = service.retrieve_invite_user_constraints(cmd)

    assert result.organization_ids == organization_ids
    assert result.roles == roles
    assert service.app.handle.call_args_list[0].args[0]._policies == policy_context


@pytest.mark.parametrize(
    ("key", "token", "expired", "expected"),
    [
        (None, "match", False, (True, False)),
        ("user@example.org", "match", False, (True, False)),
        ("other@example.org", "match", False, (False, True)),
        ("user@example.org", "other", False, (False, True)),
        (None, "other", False, (False, False)),
        (None, "match", True, (False, True)),
    ],
    ids=[
        "open-match",
        "key-match",
        "key-mismatch",
        "token-mismatch",
        "unrelated",
        "expired",
    ],
)
def test_classify_invitation_for_registration(
    key: str | None,
    token: str,
    expired: bool,
    expected: tuple[bool, bool],
) -> None:
    expires_at = (
        datetime.now(timezone.utc) - timedelta(seconds=1)
        if expired
        else datetime.now(timezone.utc) + timedelta(days=1)
    )
    invitation = _make_invitation(key=key, token="match", expires_at=expires_at)

    assert (
        OrganizationService._classify_invitation_for_registration(
            invitation, "user@example.org", token, datetime.now(timezone.utc)
        )
        == expected
    )


def test_classify_invitation_normalizes_naive_expiry_to_utc() -> None:
    expires_at = (datetime.now(timezone.utc) + timedelta(days=1)).replace(tzinfo=None)
    invitation = _make_invitation(key=None, expires_at=expires_at)

    assert OrganizationService._classify_invitation_for_registration(
        invitation, "user@example.org", "invite-token", datetime.now(timezone.utc)
    ) == (True, False)


def test_register_invited_user_requires_a_user() -> None:
    service = _make_service()
    cmd = command.RegisterInvitedUserCommand(user=None, token="invite-token")

    with pytest.raises(AssertionError, match="no user"):
        service.register_invited_user(cmd)


def test_register_invited_user_requires_user_manager() -> None:
    service = _make_service()
    service.app.user_manager = None
    cmd = command.RegisterInvitedUserCommand(user=_make_user(), token="invite-token")

    with pytest.raises(exc.InvalidArgumentsError, match="User manager not set"):
        service.register_invited_user(cmd)


def test_register_invited_user_rejects_expired_invite_without_deleting_it() -> None:
    service = _make_service()
    expired_invitation = _make_invitation(
        key="user@example.org",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    service.repository.crud.return_value = [expired_invitation]
    cmd = command.RegisterInvitedUserCommand(user=_make_user(), token="invite-token")

    with pytest.raises(exc.UnauthorizedAuthError):
        service.register_invited_user(cmd)

    assert service.repository.crud.call_count == 1
    assert service.repository.crud.call_args.args[3] == CrudOperation.READ_ALL


def test_register_invited_user_rejects_multiple_matching_invites() -> None:
    service = _make_service()
    service.repository.crud.return_value = [
        _make_invitation(key=None),
        _make_invitation(key="user@example.org"),
    ]
    cmd = command.RegisterInvitedUserCommand(user=_make_user(), token="invite-token")

    with pytest.raises(exc.ServiceException, match="Multiple open invitations"):
        service.register_invited_user(cmd)


def test_register_invited_user_applies_invite_and_deletes_matching_invites() -> None:
    service = _make_service()
    invitation = _make_invitation(key="user@example.org")
    expired_invitation = _make_invitation(
        key="other@example.org",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    service.repository.crud.return_value = [invitation, expired_invitation]
    registered_user = _make_user(key="user@example.org")
    service.app.user_manager.create_new_user_from_token.return_value = registered_user
    new_user = _make_user(key="user@example.org")
    cmd = command.RegisterInvitedUserCommand(user=new_user, token="invite-token")

    result = service.register_invited_user(cmd)

    assert result is registered_user
    assert new_user.description == invitation.description
    assert new_user.roles == invitation.roles
    assert new_user.organization_id == invitation.organization_id
    service.app.user_manager.create_new_user_from_token.assert_called_once_with(
        new_user,
        invitation.token,
        description=invitation.description,
        created_by_user_id=invitation.invited_by_user_id,
        roles=invitation.roles,
    )
    delete_call = service.repository.crud.call_args_list[-1]
    assert delete_call.args[3] == CrudOperation.DELETE_SOME
    assert set(delete_call.kwargs["obj_ids"]) == {
        invitation.id,
        expired_invitation.id,
    }


def test_update_user_rejects_empty_roles() -> None:
    service = _make_service()
    cmd = command.UpdateUserCommand.model_construct(
        user=_make_user(), tgt_user_id=uuid4(), roles=set()
    )

    with pytest.raises(exc.InvalidArgumentsError, match="Roles cannot be empty"):
        service.update_user(cmd)


def test_update_user_returns_unchanged_target_without_writing() -> None:
    service = _make_service()
    target_user = _make_user()
    service.repository.crud.return_value = target_user
    cmd = command.UpdateUserCommand(user=_make_user(), tgt_user_id=target_user.id)

    assert service.update_user(cmd) is target_user
    service.repository.crud.assert_called_once()


def test_update_user_changes_fields_and_checks_new_organization() -> None:
    service = _make_service()
    target_user = _make_user()
    modified_at = datetime(2025, 1, 2, tzinfo=timezone.utc)
    target_user.created_at = None
    target_user.modified_at = modified_at
    new_organization_id = uuid4()
    updated_user = _make_user(organization_id=new_organization_id)
    service.repository.crud.side_effect = [target_user, None, updated_user]
    cmd = command.UpdateUserCommand(
        user=_make_user(),
        tgt_user_id=target_user.id,
        is_active=False,
        roles={"COMMONDB_ADMIN"},
        organization_id=new_organization_id,
    )

    result = service.update_user(cmd)

    assert result is updated_user
    assert target_user.is_active is False
    assert target_user.roles == {"COMMONDB_ADMIN"}
    assert target_user.organization_id == new_organization_id
    assert target_user.created_at == modified_at
    assert service.repository.crud.call_args_list[1].args[2] is model.Organization
    assert service.repository.crud.call_args_list[1].args[3] == CrudOperation.READ_ONE
    assert service.repository.crud.call_args_list[2].args[3] == CrudOperation.UPDATE_ONE


def test_retrieve_organization_contacts_filters_sites_and_contacts() -> None:
    service = _make_service()
    organization_id = _ORGANIZATION_ID
    other_organization_id = uuid4()
    organization = model.Organization(
        id=organization_id, code="ORG", name="Organization"
    )
    site = model.Site(organization_id=organization_id, name="Main")
    other_site = model.Site(organization_id=other_organization_id, name="Other")
    site.id = uuid4()
    other_site.id = uuid4()
    matching_contact = model.Contact(site_id=site.id, name="Contact")
    other_contact = model.Contact(site_id=other_site.id, name="Other contact")
    service.repository.crud.side_effect = [
        organization,
        [site, other_site],
        [matching_contact, other_contact],
    ]
    cmd = command.RetrieveOrganizationContactsCommand(
        user=_make_user(), organization_id=organization_id
    )

    result = service.retrieve_organization_contacts(cmd)

    assert result.organization is organization
    assert result.sites == [site]
    assert result.contacts == [matching_contact]


def test_anonymize_user_rejects_self_anonymization() -> None:
    service = _make_service()
    cmd = command.AnonymizeUserCommand(user=_make_user(), tgt_user_id=_USER_ID)

    with pytest.raises(exc.UnauthorizedAuthError, match="may not anonymize"):
        service.anonymize_user(cmd)
