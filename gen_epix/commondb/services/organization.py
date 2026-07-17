from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar
from uuid import UUID

from cachetools import TTLCache, cached

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.fastapp import Command, CrudOperation, exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import CrudCommand


class OrganizationService(BaseOrganizationService):
    DEFAULT_CFG = {
        "user_invitation_time_to_live": 86400,  # 1 day
    }

    CACHE_INVALIDATION_COMMANDS: tuple[type[Command], ...] = (
        command.UserCrudCommand,
        command.UpdateUserCommand,
    )
    _RETRIEVE_USER_BY_KEY_CACHE: ClassVar[TTLCache] = TTLCache(maxsize=1000, ttl=60)

    def __init__(
        self,
        app: App,
        **kwargs: Any,
    ) -> None:
        super().__init__(app, **kwargs)

        for command_class in self.CACHE_INVALIDATION_COMMANDS:
            app.register_cache_invalidator(command_class, self._invalidate_cache)
            app.set_auto_invalidate_cache(command_class, True)

        app_impl: AppImplDetails = app.impl
        self.user_class: type[model.User] = app_impl.get_mapped_class(model.User)
        self.user_invitation_class: type[model.UserInvitation] = (
            app_impl.get_mapped_class(model.UserInvitation)
        )
        self.user_invitation_constraints_class: type[
            model.UserInvitationConstraints
        ] = app_impl.get_mapped_class(model.UserInvitationConstraints)

    def crud(
        self,
        cmd: CrudCommand,
    ) -> Any:
        # ABAC: ROOT may not delete self or own organization
        if (
            issubclass(
                type(cmd), (command.UserCrudCommand, command.OrganizationCrudCommand)
            )
            and cmd.is_delete()
            and cmd.user
            and self.app.user_manager.is_root_user(cmd.user)
        ):
            user: model.User = cmd.user  # type: ignore[assignment]
            is_delete_user = issubclass(type(cmd), command.UserCrudCommand)
            id_ = user.id if is_delete_user else user.organization_id
            raise_error = False
            if cmd.is_delete_all():
                raise_error = True
            elif cmd.operation == CrudOperation.DELETE_ONE:
                raise_error = id_ == cmd.obj_ids
            elif cmd.operation == CrudOperation.DELETE_SOME:
                raise_error = id_ in cmd.obj_ids  # type: ignore[operator]
            else:
                raise NotImplementedError(
                    f"Unsupported delete operation: {cmd.operation}"
                )
            if raise_error:
                raise exc.UnauthorizedAuthError(
                    "4fc118ef",
                    f"Root user may not delete {'self' if is_delete_user else 'own organization'}",
                )

        return super().crud(cmd)

    def _invalidate_cache(self, _cmd: Command) -> None:
        self.retrieve_user_by_key.cache_clear()

    @cached(cache=_RETRIEVE_USER_BY_KEY_CACHE)
    def retrieve_user_by_key(self, user_key: str) -> model.User:
        with self.repository.uow() as uow:
            return self.repository.retrieve_user_by_key(uow, user_key)

    def invite_user(
        self,
        cmd: command.InviteUserCommand,
    ) -> model.UserInvitation:
        user = cmd.user
        if user is None:
            raise exc.UnauthorizedAuthError("97e65b72", "Command has no user")
        if user.id is None:
            raise exc.UnauthorizedAuthError("bc8feeed", "User has no ID")
        key = cmd.key
        description = cmd.description
        initial_roles = cmd.roles
        organization_id = cmd.organization_id

        with self.repository.uow() as uow:

            # Verify if user already exists (only applicable when key is provided)
            if key is not None:
                is_existing_user = self.app.user_manager.is_existing_user_by_key(
                    key, uow
                )
                if is_existing_user:
                    if self._logger:
                        self._logger.info(
                            self.create_log_message(
                                "acba1a0e",
                                f"User {key} already exists",
                            )
                        )
                    raise exc.UserAlreadyExistsAuthError(
                        "7ca0dc91", "User already exists"
                    )

            is_existing_organization: bool = self.repository.crud(
                uow,
                user.id,
                model.Organization,
                CrudOperation.EXISTS_ONE,
                obj_ids=organization_id,
            )
            if not is_existing_organization:
                if self._logger:
                    self._logger.info(
                        self.create_log_message(
                            "cdf1b633",
                            f"Organization id {organization_id} does not exist",
                        )
                    )
                raise exc.InvalidIdsError("639bd55b", "Organization does not exist")

            # Verify if invitation(s) already exist for this key, and delete those.
            # Only applicable when key is provided; keyless invitations are not deduplicated.
            # TODO: Must be done within the same session to be safe,
            # so requires specific repository method
            if key is not None:
                user_invitations: list[model.UserInvitation] = self.repository.crud(
                    uow,
                    user.id,
                    self.user_invitation_class,
                    CrudOperation.READ_ALL,
                )
                user_invitations = [x for x in user_invitations if x.key == key]
                if user_invitations:
                    self.repository.crud(
                        uow,
                        user.id,
                        self.user_invitation_class,
                        CrudOperation.DELETE_SOME,
                        obj_ids=[x.id for x in user_invitations],
                    )
            # Create user invitation
            user_invitation = self.user_invitation_class(
                id=self.generate_id(),  # type: ignore[arg-type]
                key=key,
                description=description,
                roles=initial_roles,
                organization_id=organization_id,
                invited_by_user_id=user.id,
                token=self.generate_user_invitation_token(),
                expires_at=datetime.now(timezone.utc)
                + timedelta(
                    seconds=self.props.get(
                        "user_invitation_time_to_live",
                        OrganizationService.DEFAULT_CFG["user_invitation_time_to_live"],
                    )
                ),
            )
            user_invitation_in_db: model.UserInvitation = self.repository.crud(
                uow,
                user.id,
                self.user_invitation_class,
                CrudOperation.CREATE_ONE,
                objs=user_invitation,
            )
        return user_invitation_in_db

    def retrieve_invite_user_constraints(
        self, cmd: command.RetrieveInviteUserConstraintsCommand
    ) -> model.UserInvitationConstraints:
        sub_cmd = command.RetrieveOrganizationsUnderAdminCommand(user=cmd.user)
        sub_cmd._policies = cmd._policies
        organization_ids = self.app.handle(sub_cmd)
        roles = self.app.handle(command.RetrieveSubRolesCommand(user=cmd.user))
        return self.user_invitation_constraints_class(
            organization_ids=organization_ids,
            roles=roles,
        )

    def register_invited_user(
        self, cmd: command.RegisterInvitedUserCommand
    ) -> model.User:
        new_user = cmd.user
        if new_user is None:
            # Should not happen
            raise AssertionError("Command has no user")
        if not self.app.user_manager:
            raise exc.InvalidArgumentsError("20c89b79", "User manager not set")

        with self.repository.uow() as uow:
            # Get possible user invitations
            user_invitations: list[model.UserInvitation] = self.repository.crud(
                uow,
                None,
                self.user_invitation_class,
                CrudOperation.READ_ALL,
            )
            now = datetime.now(timezone.utc)

            # Keep invitations that are not expired and either have no key
            # (open invites) or have a key matching the registering user.
            to_delete_user_invitation_ids: list[UUID] = []
            selected_user_invitation: model.UserInvitation | None = None
            for user_invitation in user_invitations:
                assert user_invitation.id is not None
                # convert x.expires_at to aware datetime if it is naive
                expires_at = user_invitation.expires_at
                if user_invitation.expires_at.tzinfo is None:
                    expires_at = user_invitation.expires_at.replace(tzinfo=timezone.utc)

                if expires_at > now:
                    # Invitation is not expired
                    if user_invitation.token == cmd.token:
                        if selected_user_invitation:
                            # Should not happen: multiple open invites with same token
                            raise exc.ServiceException(
                                "c6348285",
                                f"Multiple open invitations found for token {cmd.token}",
                            )
                        # Token matches, so this is a candidate invitation
                        if user_invitation.key is None:
                            # No key means open invite, so accept
                            selected_user_invitation = user_invitation
                        elif user_invitation.key == new_user.key:
                            # Key provided and matches user key, so accept
                            selected_user_invitation = user_invitation
                        else:
                            # Key provided but does not match user key, so reject and delete
                            to_delete_user_invitation_ids.append(user_invitation.id)
                    elif (
                        user_invitation.key is not None
                        and user_invitation.key == new_user.key
                    ):
                        # Additional invitation for same user with matching key but non-matching token, delete it
                        to_delete_user_invitation_ids.append(user_invitation.id)
                else:
                    # Expired invitation, delete it (functions as cleanup of expired invites rather than relying on separate cleanup process)
                    to_delete_user_invitation_ids.append(user_invitation.id)

            # Handle case where no valid invitation is found
            if not selected_user_invitation:
                raise exc.UnauthorizedAuthError(
                    "349c4bc0",
                    f"No valid invitations found for user {new_user.key} and token {cmd.token}",
                )

            # Add selected invitation to list of invitations to delete, to prevent reuse of the same invitation
            assert selected_user_invitation.id is not None
            to_delete_user_invitation_ids.append(selected_user_invitation.id)

            # Set new user properties
            new_user.description = selected_user_invitation.description
            new_user.roles = selected_user_invitation.roles
            new_user.organization_id = selected_user_invitation.organization_id

            # Create user
            # TODO: user_manager.create_new_user_from_token duplicates some of the logic above and should be refactored to avoid this duplication and potential inconsistencies
            user_in_db: model.User = self.app.user_manager.create_new_user_from_token(  # type: ignore[assignment]
                new_user,
                selected_user_invitation.token,
                description=selected_user_invitation.description,
                created_by_user_id=selected_user_invitation.invited_by_user_id,
                roles=selected_user_invitation.roles,
            )

            # Delete invitations
            self.repository.crud(
                uow,
                None,
                self.user_invitation_class,
                CrudOperation.DELETE_SOME,
                obj_ids=to_delete_user_invitation_ids,
            )

        return user_in_db

    def update_user(
        self,
        cmd: command.UpdateUserCommand,
    ) -> model.User:
        assert cmd.user
        if cmd.roles is not None and len(cmd.roles) == 0:
            raise exc.InvalidArgumentsError("8ac5ab63", "Roles cannot be empty")
        with self.repository.uow() as uow:
            tgt_user: model.User = self.repository.crud(
                uow,
                cmd.user.id,
                self.user_class,
                CrudOperation.READ_ONE,
                obj_ids=cmd.tgt_user_id,
            )
            is_active = tgt_user.is_active if cmd.is_active is None else cmd.is_active
            roles = tgt_user.roles if cmd.roles is None else cmd.roles
            organization_id = (
                tgt_user.organization_id
                if cmd.organization_id is None
                else cmd.organization_id
            )
            # Special case: no updates
            if (
                tgt_user.is_active == is_active
                and tgt_user.roles == roles
                and tgt_user.organization_id == organization_id
            ):
                return tgt_user
            # Check if organization_id exists
            if tgt_user.organization_id != organization_id:
                self.repository.crud(
                    uow,
                    cmd.user.id,
                    model.Organization,
                    CrudOperation.READ_ONE,
                    obj_ids=organization_id,
                )
            # Update user
            tgt_user.is_active = is_active
            tgt_user.roles = roles
            tgt_user.organization_id = organization_id

            if tgt_user.created_at is None:
                tgt_user.created_at = tgt_user.modified_at
            updated_tgt_user: model.User = self.repository.crud(
                uow,
                cmd.user.id,
                self.user_class,
                CrudOperation.UPDATE_ONE,
                objs=tgt_user,
            )

        return updated_tgt_user

    def retrieve_organization_contacts(
        self,
        cmd: command.RetrieveOrganizationContactsCommand,
    ) -> model.OrganizationContacts:
        user, repository = self._get_user_and_repository(cmd)

        sites: list[model.Site]
        contacts: list[model.Contact]
        with repository.uow() as uow:
            organization: model.Organization = repository.crud(
                uow,
                user.id,
                model.Organization,
                CrudOperation.READ_ONE,
                obj_ids=cmd.organization_id,
            )

            sites = repository.crud(
                uow,
                user.id,
                model.Site,
                CrudOperation.READ_ALL,
            )
            contacts = repository.crud(
                uow,
                user.id,
                model.Contact,
                CrudOperation.READ_ALL,
            )
            organization_id = cmd.organization_id
            sites = [x for x in sites if x.organization_id == organization_id]
            site_ids = {x.id for x in sites}
            contacts = [x for x in contacts if x.site_id in site_ids]

        return model.OrganizationContacts(
            organization=organization,
            sites=sites,
            contacts=contacts,
        )
