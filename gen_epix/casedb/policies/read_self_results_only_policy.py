from typing import Any

from gen_epix.casedb.domain import command, enum, exc
from gen_epix.casedb.domain.policy import BaseReadSelfResultsOnlyPolicy
from gen_epix.fastapp import Command, CrudOperation, CrudOperationSet


class ReadSelfResultsOnlyPolicy(BaseReadSelfResultsOnlyPolicy):
    def filter(self, cmd: Command, retval: Any) -> Any:
        if not cmd.user or not cmd.user.id:
            raise exc.ServiceException("Command has no user")
        # TODO: replace filter for AFTER with injecting a filter DURING for efficiency
        if not isinstance(cmd, command.CrudCommand):
            raise NotImplementedError
        if cmd.operation not in CrudOperationSet.READ_OR_EXISTS.value:
            # Policy only applies to read or exists operations
            return retval

        # No restrictions for ORG_ADMIN, APP_ADMIN users and above
        is_not_restricted = (
            len(cmd.user.roles.intersection(enum.RoleSet.GE_ORG_ADMIN.value)) > 0
        )
        if is_not_restricted:
            return retval

        # Filter results based on organizations
        is_read_all = cmd.operation == CrudOperation.READ_ALL
        is_read_one = cmd.operation == CrudOperation.READ_ONE
        msg = "No data for user"
        user_id = cmd.user.id
        if isinstance(cmd, command.UserCrudCommand):
            if is_read_all:
                retval = [x for x in retval if x.id == user_id]
            if is_read_one and retval.id != user_id:
                raise exc.UnauthorizedAuthError(msg)
            if not is_read_one and any(x.id != user_id for x in retval):
                raise exc.UnauthorizedAuthError(msg)
        elif isinstance(cmd, command.UserAccessCasePolicyCrudCommand) or isinstance(
            cmd, command.UserShareCasePolicyCrudCommand
        ):
            if is_read_all:
                retval = [x for x in retval if x.user_id == user_id]
            if is_read_one and retval.user_id != user_id:
                raise exc.UnauthorizedAuthError(msg)
            if not is_read_one and any(x.user_id != user_id for x in retval):
                raise exc.UnauthorizedAuthError(msg)
        else:
            raise NotImplementedError
        return retval
