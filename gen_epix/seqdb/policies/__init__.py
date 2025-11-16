from gen_epix import fastapp
from gen_epix.commondb import policies as common_policies
from gen_epix.commondb.policies import (
    IsOrganizationAdminPolicy as IsOrganizationAdminPolicy,
)
from gen_epix.commondb.policies import ReadUserPolicy as ReadUserPolicy
from gen_epix.commondb.policies import UpdateUserPolicy as UpdateUserPolicy
from gen_epix.seqdb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy as ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.seqdb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy as ReadSelfResultsOnlyPolicy,
)

COMMON_POLICY_MAP: dict[type[fastapp.Policy], type[fastapp.Policy]] = {
    common_policies.ReadOrganizationResultsOnlyPolicy: ReadOrganizationResultsOnlyPolicy,
    common_policies.ReadSelfResultsOnlyPolicy: ReadSelfResultsOnlyPolicy,
}
