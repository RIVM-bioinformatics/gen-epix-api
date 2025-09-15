from uuid import UUID

from gen_epix.casedb.domain import exc
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.policy import BaseReadUserPolicy
from gen_epix.fastapp import Command
from gen_epix.fastapp.enum import CrudOperation, CrudOperationSet
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_boolean import EqualsBooleanFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter


class ReadUserPolicy(BaseReadUserPolicy):
    # TODO: replace by get_content implementation for more efficient application DURING execution
    def filter(
        self, cmd: Command, results: model.User | list[model.User]
    ) -> model.User | list[model.User]:
        if not isinstance(cmd, command.UserCrudCommand):
            raise NotImplementedError(
                "Unsupported command type: {cmd.__class__.__name__}"
            )
        if cmd.operation not in CrudOperationSet.READ.value:
            # Not applicable
            return results
        user: model.User | None = cmd.user
        if user is None or user.id is None:
            raise AssertionError("User must be authenticated")
        is_no_abac_user = (
            len(
                user.roles.intersection(
                    self.role_set_map[model.enum.RoleSet.GE_APP_ADMIN]
                )
            )
            > 0
        )
        if is_no_abac_user:
            return results

        organization_ids: set[UUID]
        org_admin_policies: list[model.OrganizationAdminPolicy]
        is_org_admin = (
            len(
                user.roles.intersection(
                    self.role_set_map[model.enum.RoleSet.GE_ORG_ADMIN]
                )
            )
            > 0
        )
        if is_org_admin:
            # User is organization admin: can read all users (active or not) of all
            # organizations they are admin of, plus all organization admins of those
            org_admin_policies = self.abac_service.app.handle(
                self.organization_admin_policy_crud_command_class(
                    user=user,
                    operation=CrudOperation.READ_ALL,
                    query_filter=EqualsBooleanFilter(key="is_active", value=True),
                )
            )
            organization_ids = {
                x.organization_id for x in org_admin_policies if x.user_id == user.id
            }
            org_admin_user_ids = {
                x.user_id
                for x in org_admin_policies
                if x.organization_id in organization_ids
            }
        else:
            # Regular user: can read only self and active organization admins of own organization
            org_admin_policies = self.abac_service.app.handle(
                self.organization_admin_policy_crud_command_class(
                    user=user,
                    operation=CrudOperation.READ_ALL,
                    query_filter=CompositeFilter(
                        filters=[
                            EqualsUuidFilter(
                                key="organization_id", value=user.organization_id
                            ),
                            EqualsBooleanFilter(key="is_active", value=True),
                        ],
                        operator=LogicalOperator.AND,
                    ),
                )
            )
            organization_ids = set()
            org_admin_user_ids = {x.user_id for x in org_admin_policies}
        user_ids = {user.id} | org_admin_user_ids

        # Filter or check results
        result_list: list[model.User]
        if cmd.operation == CrudOperation.READ_ALL:
            # Open-ended results: filter
            result_list = results  # type:ignore[assignment]
            return [
                x
                for x in result_list
                if (x.id in user_ids or x.organization_id in organization_ids)
                and (x.is_active or is_org_admin)
            ]
        elif cmd.operation == CrudOperation.READ_SOME:
            # Specific users requested: check results
            result_list = results  # type:ignore[assignment]
            if not all(
                (x.organization_id in organization_ids or x.id in user_ids)
                and (x.is_active or is_org_admin)
                for x in result_list
            ):
                # User cannot read users outside their admin organizations
                raise exc.UnauthorizedAuthError(
                    "Cannot read users outside your admin organizations"
                )
            return results
        elif cmd.operation == CrudOperation.READ_ONE:
            # Specific user requested: check results
            result: model.User = results  # type:ignore[assignment]
            if (
                result.organization_id not in organization_ids
                and result.id not in user_ids
            ) or not (result.is_active or is_org_admin):
                # User cannot read users outside their admin organizations
                raise exc.UnauthorizedAuthError(
                    "Cannot read users outside your admin organizations"
                )
            return results
        raise NotImplementedError("Unsupported operation: {cmd.operation.value}")
