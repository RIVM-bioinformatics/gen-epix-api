from datetime import timedelta
from typing import Any, Type

from cachetools import TTLCache, cached

from gen_epix.common.domain import command, model
from gen_epix.common.domain.service.organization import BaseOrganizationService
from gen_epix.fastapp import Command, CrudOperation, exc
from gen_epix.fastapp.model import CrudCommand


class OrganizationService(BaseOrganizationService):
    DEFAULT_CFG = {
        "user_invitation_time_to_live": 86400,  # 1 day
    }

    CACHE_INVALIDATION_COMMANDS: tuple[Type[Command], ...] = (
        command.UserCrudCommand,
        command.UpdateUserCommand,
    )

    def crud(
        self,
        cmd: CrudCommand,
    ) -> Any:
        retval = super().crud(cmd)
        # Invalidate cache
        if issubclass(type(cmd), OrganizationService.CACHE_INVALIDATION_COMMANDS):
            self.retrieve_user_by_key.cache_clear()  # type:ignore[attr-defined]
        return retval

    @cached(cache=TTLCache(maxsize=1000, ttl=60))
    def retrieve_user_by_key(self, user_key: str) -> model.User:
        with self.repository.uow() as uow:
            return self.repository.retrieve_user_by_key(uow, user_key)

    def invite_user(
        self,
        cmd: command.InviteUserCommand,
    ) -> model.UserInvitation:
        user = cmd.user
        if user is None:
            raise exc.UnauthorizedAuthError("Command has no user")
        if user.id is None:
            raise exc.UnauthorizedAuthError("User has no ID")
        email = cmd.email
        initial_roles = cmd.roles
        organization_id = cmd.organization_id

        with self.repository.uow() as uow:
            # Verify if user already exists
            is_existing_user = self.app.user_manager.is_existing_user_by_key(
                cmd.email, uow
            )

            if is_existing_user:
                if self._logger:
                    self._logger.info(
                        self.create_log_message(
                            "acba1a0e",
                            f"User {email} already exists",
                        )
                    )
                raise exc.UserAlreadyExistsAuthError("User already exists")

            is_existing_organization = self.repository.crud(
                uow,
                user.id,
                model.Organization,
                None,
                organization_id,
                CrudOperation.EXISTS_ONE,
            )
            if not is_existing_organization:
                if self._logger:
                    self._logger.info(
                        self.create_log_message(
                            "cdf1b633",
                            f"Organization id {organization_id} does not exist",
                        )
                    )
                raise exc.InvalidIdsError("Organization does not exist")

            # Verify if invitation(s) already exists for this email, and delete those
            # TODO: Must be done within the same session to be safe,
            # so requires specific repository method
            user_invitations: list[model.UserInvitation] = self.repository.crud(
                uow,
                user.id,
                self.user_invitation_class,
                None,
                None,
                CrudOperation.READ_ALL,
            )  # type: ignore
            user_invitations = [x for x in user_invitations if x.email == email]
            if user_invitations:
                self.repository.crud(
                    uow,
                    user.id,
                    self.user_invitation_class,
                    None,
                    [x.id for x in user_invitations],  # type: ignore
                    CrudOperation.DELETE_SOME,
                )  # type: ignore
            # Create user invitation
            user_invitation = self.user_invitation_class(
                id=self.generate_id(),
                email=email,
                roles=initial_roles,
                organization_id=organization_id,
                invited_by_user_id=user.id,
                token=self.generate_user_invitation_token(),
                expires_at=self.generate_timestamp()
                + timedelta(
                    seconds=self.props.get(
                        "user_invitation_time_to_live",
                        OrganizationService.DEFAULT_CFG["user_invitation_time_to_live"],
                    )
                ),
            )
            user_invitation_in_db: self.user_invitation_class = self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                self.user_invitation_class,
                user_invitation,
                None,
                CrudOperation.CREATE_ONE,
            )
        return user_invitation_in_db

    def register_invited_user(
        self, cmd: command.RegisterInvitedUserCommand
    ) -> model.User:
        new_user = cmd.user
        if new_user is None:
            # Should not happen
            raise AssertionError("Command has no user")
        if not self.app.user_manager:
            raise exc.InvalidArgumentsError("User manager not set")

        with self.repository.uow() as uow:
            # Get possible user invitations
            user_invitations: list[self.user_invitation_class] = self.repository.crud(  # type: ignore
                uow,
                None,
                self.user_invitation_class,
                None,
                None,
                CrudOperation.READ_ALL,
            )
            now = self.generate_timestamp()
            user_invitations = [
                x
                for x in user_invitations
                if x.email == new_user.email and x.expires_at > now
            ]
            if not user_invitations:
                raise exc.UnauthorizedAuthError(
                    f"No valid invitations found for user {new_user.email}",
                )
            user_invitations_with_token = [
                x for x in user_invitations if x.token == cmd.token
            ]
            if not user_invitations_with_token:
                raise exc.UnauthorizedAuthError(
                    f"No invitation found for token {cmd.token}"
                )
            # Choose the invitation with the latest expiry date
            user_invitation: self.user_invitation_class = sorted(
                user_invitations_with_token, key=lambda x: x.expires_at
            )[-1]
            # Set roles of the user
            new_user.roles = user_invitation.roles
            # Set ID and organization ID of the user
            new_user.organization_id = user_invitation.organization_id
            # Create user
            user_in_db = self.app.user_manager.create_new_user_from_token(
                new_user,
                user_invitation.token,
                created_by_user_id=user_invitation.invited_by_user_id,  # type: ignore[arg-type]
                roles=user_invitation.roles,  # type: ignore[arg-type]
            )
        return user_in_db  # type: ignore

    def update_user(
        self,
        cmd: command.UpdateUserCommand,
    ) -> model.User:
        if cmd.roles is not None and len(cmd.roles) == 0:
            raise exc.InvalidArgumentsError("Roles cannot be empty")
        with self.repository.uow() as uow:
            tgt_user = self.repository.crud(
                uow,
                cmd.user,
                self.user_class,
                None,
                cmd.tgt_user_id,
                CrudOperation.READ_ONE,
            )
            assert isinstance(tgt_user, self.user_class)
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
                    cmd.user,
                    model.Organization,
                    None,
                    organization_id,
                    CrudOperation.READ_ONE,
                )
            # Update user
            tgt_user.is_active = is_active
            tgt_user.roles = roles
            tgt_user.organization_id = organization_id
            tgt_user = self.repository.crud(
                uow,
                cmd.user,
                self.user_class,
                tgt_user,
                None,
                CrudOperation.UPDATE_ONE,
            )
            assert isinstance(tgt_user, self.user_class)

        # Invalidate cache for the user
        self.retrieve_user_by_key.cache_clear()
        return tgt_user

    def retrieve_organization_contact(
        self,
        cmd: command.RetrieveOrganizationContactCommand,
    ) -> list[model.Contact]:
        if (
            sum(
                [
                    cmd.organization_ids is not None,
                    cmd.site_ids is not None,
                    cmd.contact_ids is not None,
                ]
            )
            != 1
        ):
            raise exc.InvalidArgumentsError(
                "Exactly one of organization_ids, site_ids or contact_ids must be provided"
            )
        user, repository = self._get_user_and_repository(cmd)

        organizations: list[model.Organization]
        sites: list[model.Site]
        contacts: list[model.Contact]
        with repository.uow() as uow:
            if cmd.organization_ids:
                organizations = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Organization,
                    None,
                    cmd.organization_ids,
                    CrudOperation.READ_SOME,
                    cascade_read=True,  # type: ignore[arg-type]
                )
                sites = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Site,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    cascade_read=True,  # type: ignore[arg-type]
                )
                contacts = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Contact,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    cascade_read=False,  # type: ignore[arg-type]
                )
                organization_ids = set(cmd.organization_ids)
                sites = [x for x in sites if x.organization_id in organization_ids]
                site_ids = {x.id for x in sites}
                contacts = [x for x in contacts if x.site_id in site_ids]
            elif cmd.site_ids:
                sites = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Site,
                    None,
                    cmd.site_ids,
                    CrudOperation.READ_SOME,
                    cascade_read=True,  # type: ignore[arg-type]
                )
                organizations = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Organization,
                    None,
                    list({x.organization_id for x in sites}),
                    CrudOperation.READ_SOME,
                    cascade_read=True,  # type: ignore[arg-type]
                )
                contacts = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Contact,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    cascade_read=False,  # type: ignore[arg-type]
                )
                site_ids = {x.id for x in sites}
                contacts = [x for x in contacts if x.site_id in site_ids]
            elif cmd.contact_ids:
                contacts = (
                    repository.crud(  # type: ignore[assignment]
                        uow,
                        user.id,
                        model.Contact,
                        None,
                        cmd.contact_ids,
                        CrudOperation.READ_ALL,
                        cascade_read=True,  # type: ignore[arg-type]
                        links=self.app.domain.get_model_links(
                            model.Contact,
                            service_type=self.app.domain.get_service_type_for_model(
                                model.Contact
                            ),
                        ),
                    ),
                )
                sites = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Site,
                    None,
                    list({x.site_id for x in contacts}),
                    CrudOperation.READ_SOME,
                    cascade_read=True,  # type: ignore[arg-type]
                )
                organizations = repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    model.Organization,
                    None,
                    list({x.organization_id for x in sites}),
                    CrudOperation.READ_SOME,
                    cascade_read=True,  # type: ignore[arg-type]
                )
            else:
                raise AssertionError

        # Replace organization and site with cascaded version
        site_map = {x.id: x for x in sites}
        organization_map = {x.id: x for x in organizations}
        for site in site_map.values():
            site.organization = organization_map[site.organization_id]
        for contact in contacts:
            contact.site = site_map[contact.site_id]
        return contacts
