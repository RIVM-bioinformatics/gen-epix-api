from typing import Any

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseReadOrganizationResultsOnlyPolicy
from gen_epix.fastapp import Command, CrudOperation, CrudOperationSet


class ReadOrganizationResultsOnlyPolicy(BaseReadOrganizationResultsOnlyPolicy):
    def filter(self, cmd: Command, retval: Any) -> Any:
        if not cmd.user or not cmd.user.id:
            raise exc.ServiceException("Command has no user")
        # TODO: replace filter for AFTER with injecting a filter DURING for efficiency
        if not isinstance(cmd, command.CrudCommand):
            raise NotImplementedError
        if cmd.operation not in CrudOperationSet.READ_OR_EXISTS.value:
            # Policy only applies to read or exists operations
            return retval
        # No restrictions for APP_ADMIN users and above
        is_not_restricted = (
            len(cmd.user.roles.intersection(enum.RoleSet.GE_APP_ADMIN.value)) > 0
        )
        if is_not_restricted:
            return retval
        # Get organizations to filter on: user's own organization plus any
        # organizations they are admin for
        organization_ids = self.abac_service.get_organizations_under_admin(cmd.user)
        if organization_ids:
            organization_ids.add(cmd.user.organization_id)
        else:
            organization_ids = {cmd.user.organization_id}
        # Filter results based on organizations
        is_read_all = cmd.operation == CrudOperation.READ_ALL
        is_read_one = cmd.operation == CrudOperation.READ_ONE
        msg1 = "User is not an admin for the organization and/or does not belong to it"
        msg2 = "User is not an admin for some of the organizations and/or does not belong to them"
        if (
            isinstance(cmd, command.UserCrudCommand)
            or isinstance(cmd, command.OrganizationAdminPolicyCrudCommand)
            or isinstance(cmd, command.OrganizationAccessCasePolicyCrudCommand)
            or isinstance(cmd, command.OrganizationShareCasePolicyCrudCommand)
            or isinstance(cmd, command.UserInvitationCrudCommand)
        ):
            if is_read_all:
                retval = [x for x in retval if x.organization_id in organization_ids]
            if is_read_one and retval.organization_id not in organization_ids:
                raise exc.UnauthorizedAuthError(msg1)
            if not is_read_one and any(
                x.organization_id not in organization_ids for x in retval
            ):
                raise exc.UnauthorizedAuthError(msg2)
        elif isinstance(cmd, command.UserAccessCasePolicyCrudCommand) or isinstance(
            cmd, command.UserShareCasePolicyCrudCommand
        ):
            if is_read_one:
                user_ids = [cmd.objs]
            elif is_read_all:
                user_ids = None
            else:
                user_ids = list(set(cmd.objs))
            users: list[model.User] = self.abac_service.app.handle(
                command.UserCrudCommand(
                    user=cmd.user,
                    objs=None,
                    obj_ids=user_ids,
                    operation=(
                        CrudOperation.READ_ALL
                        if is_read_all
                        else CrudOperation.READ_SOME
                    ),
                )
            )
            valid_user_ids = {
                x.id for x in users if x.organization_id in organization_ids
            }
            if is_read_all:
                retval = [x for x in retval if x.user_id in valid_user_ids]
            else:
                if is_read_one and retval.user_id not in valid_user_ids:
                    raise exc.UnauthorizedAuthError(msg1)
                if not is_read_one and not {x.user_id for x in retval}.issubset(
                    valid_user_ids
                ):
                    raise exc.UnauthorizedAuthError(msg2)
        else:
            raise NotImplementedError
        return retval
