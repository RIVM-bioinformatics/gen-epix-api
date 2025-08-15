from typing import ClassVar

import gen_epix.casedb.domain.model.abac as model
from gen_epix.common.domain.command import Command, CrudCommand

# Non-CRUD


class RetrieveOrganizationAdminNameEmailsCommand(Command):
    pass


# CRUD


class OrganizationAdminPolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy


class OrganizationAccessCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAccessCasePolicy


class UserAccessCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserAccessCasePolicy


class OrganizationShareCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationShareCasePolicy


class UserShareCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserShareCasePolicy
