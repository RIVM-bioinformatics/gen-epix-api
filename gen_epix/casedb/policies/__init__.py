# pylint: disable=useless-import-alias
from gen_epix import fastapp
from gen_epix.casedb.policies.case_abac_policy import CaseAbacPolicy as CaseAbacPolicy
from gen_epix.casedb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy as IsOrganizationAdminPolicy,
)
from gen_epix.casedb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy as ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.casedb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy as ReadSelfResultsOnlyPolicy,
)
from gen_epix.commondb import policies as common_policies
from gen_epix.commondb.policies.has_system_outage_policy import (
    HasSystemOutagePolicy as HasSystemOutagePolicy,
)
from gen_epix.commondb.policies.read_user_policy import ReadUserPolicy as ReadUserPolicy
from gen_epix.commondb.policies.update_user_policy import (
    UpdateUserPolicy as UpdateUserPolicy,
)

COMMON_POLICY_MAP: dict[type[fastapp.Policy], type[fastapp.Policy]] = {
    common_policies.ReadOrganizationResultsOnlyPolicy: ReadOrganizationResultsOnlyPolicy,
    common_policies.ReadSelfResultsOnlyPolicy: ReadSelfResultsOnlyPolicy,
    common_policies.IsOrganizationAdminPolicy: IsOrganizationAdminPolicy,
}
