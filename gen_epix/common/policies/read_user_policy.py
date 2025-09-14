from gen_epix.casedb.domain import exc
from gen_epix.common.domain import command, model
from gen_epix.common.domain.policy import BaseUpdateUserPolicy
from gen_epix.fastapp import Command
from gen_epix.fastapp.enum import CrudOperation, CrudOperationSet


class ReadUserPolicy(BaseUpdateUserPolicy):
    # TODO: replace by get_content implementation for more efficient application DURING execution
    def filter(  # type: ignore[override]
        self, cmd: Command, results: model.User | list[model.User]
    ) -> model.User | list[model.User]:
        if not isinstance(cmd, command.UserCrudCommand):
            raise NotImplementedError(
                "Unsupported command type: {cmd.__class__.__name__}"
            )
        if cmd.operation not in CrudOperationSet.READ.value:
            # Not applicable
            return results
        user: model.User | None = cmd.user  # type: ignore[assignment]
        if user is None or user.id is None:
            raise AssertionError("User must be authenticated")
        is_no_abac_user = (self.root_role and self.root_role in user.roles) or len(
            user.roles.intersection(self.app_admin_roles)
        ) > 0
        if is_no_abac_user:
            return results

        # Get all allowed organization IDs: own organization plus any
        # organizations that the user is ORG_ADMIN for
        organization_ids = self.abac_service.retrieve_organizations_under_admin(
            command.RetrieveOrganizationsUnderAdminCommand(user=user)
        )
        organization_ids.add(user.organization_id)

        # Filter or check results
        if cmd.operation == CrudOperation.READ_ALL:
            # Open-ended results: filter
            return [x for x in results if x.organization_id in organization_ids]  # type: ignore[union-attr,misc,return-value]
        elif cmd.operation == CrudOperation.READ_SOME:
            # Specific users requested: check results
            if any(x.organization_id not in organization_ids for x in results):  # type: ignore[union-attr]
                # User cannot read users outside their admin organizations
                raise exc.UnauthorizedAuthError(
                    "Cannot read users outside your admin organizations"
                )
            return results
        elif cmd.operation == CrudOperation.READ_ONE:
            # Specific user requested: check results
            if results.organization_id not in organization_ids:  # type: ignore[union-attr]
                # User cannot read users outside their admin organizations
                raise exc.UnauthorizedAuthError(
                    "Cannot read users outside your admin organizations"
                )
            return results
        raise NotImplementedError("Unsupported operation: {cmd.operation.value}")
