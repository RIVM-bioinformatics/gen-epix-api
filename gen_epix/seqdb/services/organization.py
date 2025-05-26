from datetime import timedelta

from cachetools import TTLCache, cached

from gen_epix.fastapp import CrudOperation, EventTiming
from gen_epix.seqdb.domain import command, exc, model
from gen_epix.seqdb.domain.service.organization import BaseOrganizationService
from gen_epix.seqdb.policies.update_user_policy import UpdateUserPolicy


class OrganizationService(BaseOrganizationService):
    DEFAULT_CFG = {
        "user_invitation_time_to_live": 86400,  # 1 day
    }

    def register_policies(self) -> None:
        f = self.app.register_policy
        policy = UpdateUserPolicy(self)
        for command_class in BaseOrganizationService.UPDATE_USER_COMMANDS:
            f(command_class, policy, EventTiming.BEFORE)

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
        initial_data_collection_ids = cmd.data_collection_ids

        with self.repository.uow() as uow:
            # Verify if data_collection_ids are valid
            self.repository.crud(
                uow,
                user.id,
                model.DataCollection,
                None,
                initial_data_collection_ids,
                CrudOperation.READ_SOME,
            )
            # Verify if user already exists
            try:
                self.app.user_manager.retrieve_user_by_key(user)
                if self._logger:
                    self._logger.info(
                        self.create_log_message(
                            "acba1a0e",
                            f"User {email} already exists",
                        )
                    )
                raise exc.UserAlreadyExistsAuthError("User already exists")
            except exc.UserAlreadyExistsAuthError as e:
                raise e
            except Exception:
                # User does not exist yet
                pass
            # Verify if invitation(s) already exists for this email, and delete those
            # TODO: Must be done within the same session to be safe,
            # so requires specific repository method
            user_invitations: list[model.UserInvitation] = self.repository.crud(
                uow,
                user.id,
                model.UserInvitation,
                None,
                None,
                CrudOperation.READ_ALL,
            )  # type: ignore
            user_invitations = [x for x in user_invitations if x.email == email]
            if user_invitations:
                self.repository.crud(
                    uow,
                    user.id,
                    model.UserInvitation,
                    None,
                    [x.id for x in user_invitations],  # type: ignore
                    CrudOperation.DELETE_SOME,
                )  # type: ignore
            # Create user invitation
            user_invitation = model.UserInvitation(
                email=email,
                roles=initial_roles,
                data_collection_ids=initial_data_collection_ids,
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
            user_invitation_in_db: model.UserInvitation = self.app.handle(
                command.UserInvitationCrudCommand(
                    user=user,
                    objs=user_invitation,
                    operation=CrudOperation.CREATE_ONE,
                )
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
            user_invitations: list[model.UserInvitation] = self.repository.crud(  # type: ignore
                uow,
                None,
                model.UserInvitation,
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
            user_invitation: model.UserInvitation = sorted(
                user_invitations_with_token, key=lambda x: x.expires_at
            )[-1]
            # Create user
            user_in_db = self.app.user_manager.create_new_user_from_token(
                new_user,
                user_invitation.token,
                created_by_user_id=user_invitation.invited_by_user_id,
                roles=user_invitation.roles,
            )
        return user_in_db  # type: ignore

    def retrieve_complete_user(
        self, cmd: command.RetrieveCompleteUserCommand
    ) -> model.CompleteUser:
        user = cmd.user
        if user is None:
            raise exc.UnauthorizedAuthError("Command has no user")

        # Get data collections
        data_collections: list[model.DataCollection] = self.repository.crud(
            cmd.user,
            model.DataCollection,
            None,
            user.data_collection_ids,
            CrudOperation.READ_SOME,
        )

        return model.CompleteUser(
            **{x: y for x, y in user.model_dump().items() if x != "data_collections"},
            data_collections=data_collections,
        )

    def update_user(
        self,
        cmd: command.UpdateUserCommand,
    ) -> model.User:
        tgt_user = self.repository.crud(
            cmd.user,
            model.User,
            None,
            cmd.tgt_user_id,
            CrudOperation.READ_ONE,
        )
        is_active = tgt_user.is_active if cmd.is_active is None else cmd.is_active
        roles = tgt_user.roles if cmd.roles is None else cmd.roles
        data_collection_ids = (
            tgt_user.data_collection_ids
            if cmd.data_collection_ids is None
            else cmd.data_collection_ids
        )
        # Special case: no updates
        if (
            tgt_user.is_active == is_active
            and tgt_user.roles == roles
            and tgt_user.data_collection_ids == data_collection_ids
        ):
            return tgt_user
        # Check if data_collection_ids exists
        if tgt_user.data_collection_ids != data_collection_ids:
            self.repository.crud(
                cmd.user,
                model.DataCollection,
                None,
                data_collection_ids,
                CrudOperation.READ_SOME,
            )
        # Update user
        tgt_user.is_active = is_active
        tgt_user.roles = roles
        tgt_user.data_collection_ids = data_collection_ids
        return self.repository.crud(
            cmd.user,
            model.User,
            tgt_user,
            None,
            CrudOperation.UPDATE_ONE,
        )
