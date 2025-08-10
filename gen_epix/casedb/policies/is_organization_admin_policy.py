from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy import BaseIsOrganizationAdminPolicy
from gen_epix.fastapp import Command, CrudCommand, CrudOperation, CrudOperationSet


class IsOrganizationAdminPolicy(BaseIsOrganizationAdminPolicy):
    def is_allowed(self, cmd: Command) -> bool:
        if cmd.user is None:
            return False

        if cmd.user.roles.intersection(enum.RoleSet.GE_APP_ADMIN.value):
            return True

        if isinstance(cmd, CrudCommand):
            if cmd.operation not in CrudOperationSet.WRITE.value:
                # Policy only applies to write operations
                return True
            objs = cmd.objs
            if objs is None:
                objs = []
            elif not isinstance(objs, list):
                objs = [objs]
            # Determine the set of organizations affected
            if isinstance(
                cmd, command.OrganizationAccessCasePolicyCrudCommand
            ) or isinstance(cmd, command.OrganizationShareCasePolicyCrudCommand):
                organization_ids = set(x.organization_id for x in objs)  # type: ignore
            elif isinstance(cmd, command.UserAccessCasePolicyCrudCommand) or isinstance(
                cmd, command.UserShareCasePolicyCrudCommand
            ):
                with self.abac_service.repository.uow() as uow:
                    users: list[model.User] = self.abac_service.app.handle(
                        command.UserCrudCommand(
                            user=cmd.user,
                            objs=None,
                            obj_ids=list(set(x.user_id for x in objs)),
                            operation=CrudOperation.READ_SOME,
                        )
                    )
                    organization_ids = set(x.organization_id for x in users)
            elif isinstance(cmd, command.SiteCrudCommand):
                organization_ids = {x.organization_id for x in objs}
            elif isinstance(cmd, command.ContactCrudCommand):
                contacts = self.abac_service.app.handle(
                    command.ContactCrudCommand(
                        user=cmd.user,
                        objs=None,
                        obj_ids=list(set(x.contact_id for x in objs)),
                        operation=CrudOperation.READ_SOME,
                    )
                )
                sites = self.abac_service.app.handle(
                    command.ContactCrudCommand(
                        user=cmd.user,
                        objs=None,
                        obj_ids=list(set(x.site_id for x in contacts)),
                        operation=CrudOperation.READ_SOME,
                    )
                )
                organization_ids = {x.organization_id for x in sites}
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError
        # Check if user is an admin for all of the affected organizations
        user_admin_organization_ids = self.abac_service.get_organizations_under_admin(
            cmd.user
        )
        has_permission = organization_ids.issubset(user_admin_organization_ids)
        return has_permission
