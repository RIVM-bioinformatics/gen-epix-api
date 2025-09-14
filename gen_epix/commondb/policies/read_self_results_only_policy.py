from enum import Enum
from typing import Any

from gen_epix.commondb.domain import command, enum, exc
from gen_epix.commondb.domain.policy import BaseReadSelfResultsOnlyPolicy
from gen_epix.commondb.domain.service.abac import BaseAbacService
from gen_epix.fastapp import Command, CrudOperation, CrudOperationSet


class ReadSelfResultsOnlyPolicy(BaseReadSelfResultsOnlyPolicy):

    def __init__(
        self,
        abac_service: BaseAbacService,
        role_map: dict[Enum, Enum] | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            role_map=role_map,
            **kwargs,
        )
        self.id_attr_by_command_class = {
            command.UserCrudCommand: "id",
            command.UserInvitationCrudCommand: "invited_by_user_id",
        }

    def filter(self, cmd: Command, retval: Any) -> Any:
        if not cmd.user or not cmd.user.id:
            raise exc.ServiceException("Command has no user")
        # TODO: replace filter for AFTER with injecting a filter DURING for efficiency
        if not isinstance(cmd, command.CrudCommand):
            raise NotImplementedError
        if cmd.operation not in CrudOperationSet.READ_OR_EXISTS.value:
            # Policy only applies to read or exists operations
            return retval

        # Roles exempt from this policy
        is_exempt = (
            len(
                cmd.user.roles.intersection(
                    self.role_set_map[enum.RoleSet.GE_ORG_ADMIN]
                )
            )
            > 0
        )
        if is_exempt:
            return retval

        # Filter results based on own user
        is_read_all = cmd.operation == CrudOperation.READ_ALL
        is_read_one = cmd.operation == CrudOperation.READ_ONE
        msg = "No data for user"
        user_id = cmd.user.id
        id_attr: str | None = self.id_attr_by_command_class.get(type(cmd))
        if not id_attr:
            raise NotImplementedError
        if is_read_all:
            retval = [x for x in retval if getattr(x, id_attr) == user_id]
        if is_read_one and getattr(retval, id_attr) != user_id:
            raise exc.UnauthorizedAuthError(msg)
        if not is_read_one and any(getattr(x, id_attr) != user_id for x in retval):
            raise exc.UnauthorizedAuthError(msg)
        return retval
