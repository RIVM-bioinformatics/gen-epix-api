"""Expose OmopDB API request schemas used by shared router composition.

The facade exports person and cohort retrieval request bodies and the OmopDB
organization permission schema, including the inherited update-user request.
"""

# pylint: disable=useless-import-alias
from gen_epix.commondb.api import (
    UpdateUserOwnOrganizationRequestBody as UpdateUserOwnOrganizationRequestBody,
)
from gen_epix.omopdb.api.omop import (
    RetrievePersonsByIdsRequestBody as RetrievePersonsByIdsRequestBody,
)
from gen_epix.omopdb.api.omop import (
    RetrieveSpecimenIdsByCohortIdsRequestBody as RetrieveSpecimenIdsByCohortIdsRequestBody,
)
from gen_epix.omopdb.api.organization import ApiPermission as ApiPermission
