"""Define casedb commands for case access and sharing policies."""

from typing import ClassVar

import gen_epix.casedb.domain.model as model
from gen_epix.commondb.domain.command import CrudCommand

# Non-CRUD


# CRUD


class OrganizationAccessCasePolicyCrudCommand(CrudCommand):
    """Represent CRUD operations for organization-level case access policies.

    Policies apply within a data collection and are scoped by case-type and
    read/write column sets.
    """

    MODEL_CLASS: ClassVar = model.OrganizationAccessCasePolicy


class UserAccessCasePolicyCrudCommand(CrudCommand):
    """Represent CRUD operations for per-user case access policies.

    Effective rights within a data collection intersect with the applicable
    organization policy.
    """

    MODEL_CLASS: ClassVar = model.UserAccessCasePolicy


class OrganizationShareCasePolicyCrudCommand(CrudCommand):
    """Represent CRUD operations for organization case-sharing policies.

    Policies control which cases or case sets an organization may share between
    data collections for specific case-type sets.
    """

    MODEL_CLASS: ClassVar = model.OrganizationShareCasePolicy


class UserShareCasePolicyCrudCommand(CrudCommand):
    """Represent CRUD operations for per-user case-sharing policies.

    User permissions for sharing cases or case sets between data collections
    are bounded by the applicable organization policy.
    """

    MODEL_CLASS: ClassVar = model.UserShareCasePolicy
