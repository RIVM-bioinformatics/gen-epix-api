from typing import ClassVar

import gen_epix.casedb.domain.model as model
from gen_epix.commondb.domain.command import CrudCommand

# Non-CRUD


# CRUD


class OrganizationAccessCasePolicyCrudCommand(CrudCommand):
    """Manage organization-level access policies to cases and case sets in a data collection, scoped by case-type and read/write column sets."""

    MODEL_CLASS: ClassVar = model.OrganizationAccessCasePolicy


class UserAccessCasePolicyCrudCommand(CrudCommand):
    """Manage per-user maximum access policies to cases and case sets in a data collection; effective rights intersect with the organization policy."""

    MODEL_CLASS: ClassVar = model.UserAccessCasePolicy


class OrganizationShareCasePolicyCrudCommand(CrudCommand):
    """Manage which cases or case sets an organization may share from one data collection into another for specific case-type sets."""

    MODEL_CLASS: ClassVar = model.OrganizationShareCasePolicy


class UserShareCasePolicyCrudCommand(CrudCommand):
    """Manage per-user share permissions for moving cases or case sets between data collections, bounded by the organization's share policy."""

    MODEL_CLASS: ClassVar = model.UserShareCasePolicy
