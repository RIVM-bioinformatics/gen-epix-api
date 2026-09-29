"""Expose shared organization policies and OmopDB role generation.

The facade re-exports commondb policies for organization administration,
scoped result reads, and user updates, together with OmopDB `RoleGenerator`.
"""

# pylint: disable=useless-import-alias
from gen_epix.commondb.domain.policy import (
    BaseIsOrganizationAdminPolicy as BaseIsOrganizationAdminPolicy,
)
from gen_epix.commondb.domain.policy import (
    BaseReadOrganizationResultsOnlyPolicy as BaseReadOrganizationResultsOnlyPolicy,
)
from gen_epix.commondb.domain.policy import (
    BaseReadSelfResultsOnlyPolicy as BaseReadSelfResultsOnlyPolicy,
)
from gen_epix.commondb.domain.policy import BaseUpdateUserPolicy as BaseUpdateUserPolicy
from gen_epix.omopdb.domain.policy.permission import RoleGenerator as RoleGenerator
