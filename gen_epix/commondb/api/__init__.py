"""Re-export commondb API endpoint factories and request/response schemas.

The package exposes endpoint builders for authentication, RBAC, organization, and
system commands plus request/response models used by remote commondb clients.
"""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports
from gen_epix.commondb.api.organization_schema import ApiPermission as ApiPermission
from gen_epix.commondb.api.organization_schema import (
    DataCollectionSetDataCollectionUpdateAssociationRequestBody as DataCollectionSetDataCollectionUpdateAssociationRequestBody,
)
from gen_epix.commondb.api.organization_schema import (
    InviteUserRequestBody as InviteUserRequestBody,
)
from gen_epix.commondb.api.organization_schema import (
    OrganizationIdentifierIssuerUpdateAssociationRequestBody as OrganizationIdentifierIssuerUpdateAssociationRequestBody,
)
from gen_epix.commondb.api.organization_schema import (
    OrganizationSetOrganizationUpdateAssociationRequestBody as OrganizationSetOrganizationUpdateAssociationRequestBody,
)
from gen_epix.commondb.api.organization_schema import (
    RetrieveOrganizationContactsRequestBody as RetrieveOrganizationContactsRequestBody,
)
from gen_epix.commondb.api.organization_schema import (
    UpdateUserOwnOrganizationRequestBody as UpdateUserOwnOrganizationRequestBody,
)
from gen_epix.commondb.api.organization_schema import (
    UpdateUserRequestBody as UpdateUserRequestBody,
)
from gen_epix.commondb.api.system_schema import ExternalLogItem as ExternalLogItem
from gen_epix.commondb.api.system_schema import HealthResponseBody as HealthResponseBody
from gen_epix.commondb.api.system_schema import HealthStatus as HealthStatus
from gen_epix.commondb.api.system_schema import (
    LicensesResponseBody as LicensesResponseBody,
)
from gen_epix.commondb.api.system_schema import LogRequestBody as LogRequestBody

if TYPE_CHECKING:
    from gen_epix.commondb.api.auth import (
        create_auth_endpoints as create_auth_endpoints,
    )
    from gen_epix.commondb.api.organization import (
        create_organization_endpoints as create_organization_endpoints,
    )
    from gen_epix.commondb.api.rbac import (
        create_rbac_endpoints as create_rbac_endpoints,
    )
    from gen_epix.commondb.api.system import (
        create_system_endpoints as create_system_endpoints,
    )

# The endpoint factories depend on FastAPI and are resolved on first access, so
# that a remote client can import the request and response models without it
_LAZY_EXPORTS: dict[str, LazyExport] = {
    **exports_from("gen_epix.commondb.api.auth", "create_auth_endpoints"),
    **exports_from(
        "gen_epix.commondb.api.organization", "create_organization_endpoints"
    ),
    **exports_from("gen_epix.commondb.api.rbac", "create_rbac_endpoints"),
    **exports_from("gen_epix.commondb.api.system", "create_system_endpoints"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)
