# pylint: disable=useless-import-alias
from gen_epix import fastapp
from gen_epix.commondb.policies.has_system_outage_policy import (
    HasSystemOutagePolicy as HasSystemOutagePolicy,
)
from gen_epix.commondb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy as IsOrganizationAdminPolicy,
)
from gen_epix.commondb.policies.model_metadata_policy import (
    ModelMetadataPolicy as ModelMetadataPolicy,
)
from gen_epix.commondb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy as ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.commondb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy as ReadSelfResultsOnlyPolicy,
)
from gen_epix.commondb.policies.read_user_policy import ReadUserPolicy as ReadUserPolicy
from gen_epix.commondb.policies.update_user_policy import (
    UpdateUserPolicy as UpdateUserPolicy,
)

COMMON_POLICY_MAP: dict[type[fastapp.Policy], type[fastapp.Policy]] = {}
