from typing import Type

from gen_epix import fastapp
from gen_epix.commondb import policies as common_policies
from gen_epix.commondb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy as IsOrganizationAdminPolicy,
)
from gen_epix.commondb.policies.read_user_policy import ReadUserPolicy as ReadUserPolicy
from gen_epix.commondb.policies.update_user_policy import (
    UpdateUserPolicy as UpdateUserPolicy,
)
from gen_epix.omopdb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy as ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.omopdb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy as ReadSelfResultsOnlyPolicy,
)

COMMON_POLICY_MAP: dict[Type[fastapp.Policy], Type[fastapp.Policy]] = {
    common_policies.ReadOrganizationResultsOnlyPolicy: ReadOrganizationResultsOnlyPolicy,
    common_policies.ReadSelfResultsOnlyPolicy: ReadSelfResultsOnlyPolicy,
}
