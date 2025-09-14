from enum import Enum
from typing import Any, Type

from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.policy import BaseReadOrganizationResultsOnlyPolicy
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp import CrudOperation, CrudOperationSet, exc


class ReadOrganizationResultsOnlyPolicy(BaseReadOrganizationResultsOnlyPolicy):

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
        self.user_crud_command_class: Type[command.UserCrudCommand] = (
            command.UserCrudCommand
        )
        self.has_organization_id_attr_command_classes: set[Type[command.Command]] = {
            command.UserCrudCommand,
            command.OrganizationAdminPolicyCrudCommand,
            command.UserInvitationCrudCommand,
        }
        self.has_user_id_attr_command_classes: set[Type[command.Command]] = set()

    def filter(self, cmd: command.Command, retval: Any) -> Any:  # type: ignore[override]
        if not cmd.user or not cmd.user.id:
            raise exc.ServiceException("Command has no user")
        # TODO: replace filter for AFTER with injecting a filter DURING for efficiency
        if isinstance(cmd, command.RetrieveInviteUserConstraintsCommand):
            # Already handled DURING
            return retval
        if not isinstance(cmd, command.CrudCommand):
            raise NotImplementedError
        if cmd.operation not in CrudOperationSet.READ_OR_EXISTS.value:
            # Policy only applies to read or exists operations
            return retval

        # Roles exempt from this policy
        is_exempt = (
            len(
                cmd.user.roles.intersection(
                    self.role_set_map[enum.RoleSet.GE_APP_ADMIN]
                )
            )
            > 0
        )
        if is_exempt:
            return retval

        # Get organizations to filter on: user's own organization plus any
        # organizations they are admin for
        organization_ids = self.abac_service.retrieve_organizations_under_admin(
            command.RetrieveOrganizationsUnderAdminCommand(user=cmd.user)
        )
        if organization_ids:
            organization_ids.add(cmd.user.organization_id)
        else:
            organization_ids = {cmd.user.organization_id}
        # Filter results based on organizations
        is_read_all = cmd.operation == CrudOperation.READ_ALL
        is_read_one = cmd.operation == CrudOperation.READ_ONE
        msg1 = "User is not an admin for the organization and/or does not belong to it"
        msg2 = "User is not an admin for some of the organizations and/or does not belong to them"
        for command_class in self.has_organization_id_attr_command_classes:
            if not isinstance(cmd, command_class):
                continue
            if is_read_all:
                return [x for x in retval if x.organization_id in organization_ids]
            if is_read_one and retval.organization_id not in organization_ids:
                raise exc.UnauthorizedAuthError(msg1)
            if not is_read_one and any(
                x.organization_id not in organization_ids for x in retval
            ):
                raise exc.UnauthorizedAuthError(msg2)
        for command_class in self.has_user_id_attr_command_classes:
            if not isinstance(cmd, command_class):
                continue
            objs: list = cmd.get_objs() if not is_read_all else []  # type: ignore[attr-defined]
            users: list[model.User] = self.abac_service.app.handle(
                self.user_crud_command_class(
                    user=cmd.user,
                    objs=None,
                    obj_ids=(None if is_read_all else list({x.user_id for x in objs})),
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
                return [x for x in retval if x.user_id in valid_user_ids]
            else:
                if is_read_one and retval.user_id not in valid_user_ids:
                    raise exc.UnauthorizedAuthError(msg1)
                if not is_read_one and not {x.user_id for x in retval}.issubset(
                    valid_user_ids
                ):
                    raise exc.UnauthorizedAuthError(msg2)
        raise NotImplementedError
