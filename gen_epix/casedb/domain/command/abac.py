from typing import ClassVar

import gen_epix.casedb.domain.model as model
from gen_epix.commondb.domain.command import CrudCommand
from gen_epix.commondb.domain.command import (
    OrganizationAdminPolicyCrudCommand as CommonOrgAdminPolicyCrudCommand,
)

# Non-CRUD


# CRUD


class OrganizationAdminPolicyCrudCommand(CommonOrgAdminPolicyCrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy


class OrganizationAccessCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAccessCasePolicy


class UserAccessCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserAccessCasePolicy


class OrganizationShareCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationShareCasePolicy


class UserShareCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserShareCasePolicy
