from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy import BaseUpdateUserPolicy
from gen_epix.fastapp import Command


class UpdateUserPolicy(BaseUpdateUserPolicy):
    def is_allowed(self, cmd: Command) -> bool:
        user: model.User | None = cmd.user  # type: ignore[assignment]
        if user is None or user.id is None:
            return False
        roles = user.roles
        is_root = enum.Role.ROOT in roles

        if isinstance(cmd, command.InviteUserCommand):
            if user.email == cmd.email:
                # User cannot invite themselves
                return False
            tgt_user = model.User(**cmd.model_dump())
            tgt_roles_union = set(tgt_user.roles)
            is_organization_update = False
        elif isinstance(cmd, command.UpdateUserCommand):
            tgt_user = self.abac_service.app.user_manager.retrieve_user_by_id(  # type: ignore[assignment]
                cmd.tgt_user_id
            )
            tgt_roles_union = set(tgt_user.roles)
            if cmd.roles is not None:
                tgt_roles_union.update(cmd.roles)
            is_organization_update = (
                cmd.organization_id is not None
                and cmd.organization_id != tgt_user.organization_id
            )
        else:
            raise NotImplementedError

        # Handle ROOT, >=APP_ADMIN, <ORG_ADMIN
        if is_root:
            # Root user can invite/update anyone with any permissions
            return True
        tgt_user.roles = tgt_roles_union
        if len(roles.intersection(enum.RoleSet.GE_APP_ADMIN.value)) > 0:
            # APP_ADMIN users and above can invite/update anyone with less permissions
            # (so not another APP_ADMIN), and only if the new set of permissions is also
            # less than their own permissions
            return self._has_more_permissions(user, tgt_user)
        if not roles.intersection(enum.RoleSet.GE_ORG_ADMIN.value):
            # Only ORG_ADMIN users and above can invite/update users
            return False

        # ORG_ADMIN users can invite/update users of the organization(s) they are admin
        # of, but only if they have less permissions (so not another ORG_ADMIN), and
        # only if the new set of permissions is also less than their own permissions.
        # They cannot update the organization.
        if is_organization_update:
            # User cannot update the organization
            return False
        user_admin_organization_ids = self.abac_service.get_organizations_under_admin(
            user
        )
        if tgt_user.organization_id not in user_admin_organization_ids:
            # User is not admin of the organization(s) the target user is part of
            return False
        return self._has_more_permissions(user, tgt_user)

    def _has_more_permissions(self, user: model.User, tgt_user: model.User) -> bool:
        permissions = self.abac_service.app.user_manager.retrieve_user_permissions(user)  # type: ignore[arg-type]
        tgt_permissions = self.abac_service.app.user_manager.retrieve_user_permissions(
            tgt_user  # type: ignore[arg-type]
        )
        return tgt_permissions.issubset(permissions) and len(permissions) > len(
            tgt_permissions
        )
