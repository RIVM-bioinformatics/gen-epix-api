from gen_epix.fastapp import Command, CrudOperation
from gen_epix.omopdb.domain import command, enum, model
from gen_epix.omopdb.domain.policy.organization import BaseUpdateUserPolicy


class UpdateUserPolicy(BaseUpdateUserPolicy):
    def is_allowed(self, cmd: Command) -> bool:
        if cmd.user is None:
            return False

        # Root user can do anything
        if enum.Role.ROOT in cmd.user.roles:
            return True

        # Check if user is allowed to update themselves
        if isinstance(cmd, command.UpdateUserCommand):
            if cmd.tgt_user_id == cmd.user.id:
                # Only root user can update themselves
                return enum.Role.ROOT in cmd.user.roles
        elif isinstance(cmd, command.InviteUserCommand):
            if cmd.user.email == cmd.email:
                # User cannot invite themselves
                return False
        else:
            raise NotImplementedError()

        # Check if invite is allowed according to roles
        if isinstance(cmd, command.InviteUserCommand):
            # Only admin can invite another, except root and admin
            if enum.Role.APP_ADMIN not in cmd.user.roles:
                return False
            if enum.Role.ROOT in cmd.roles or enum.Role.APP_ADMIN in cmd.roles:
                return False

        # Check if update is allowed according to roles
        if isinstance(cmd, command.UpdateUserCommand):
            # Only admin can update another, except root
            if enum.Role.APP_ADMIN not in cmd.user.roles:
                return False
            with self.organization_service.repository.uow() as uow:
                tgt_user: model.User = self.organization_service.repository.crud(
                    uow,
                    cmd.user.id,
                    model.User,
                    None,
                    cmd.tgt_user_id,
                    CrudOperation.READ_ONE,
                )
            if enum.Role.ROOT in tgt_user.roles:
                return False

        raise NotImplementedError()
