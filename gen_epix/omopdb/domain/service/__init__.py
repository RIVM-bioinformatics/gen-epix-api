"""Expose OmopDB service contracts for shared and OMOP command handling.

`BaseOmopService` handles OMOP CRUD, upload, and retrieval commands, and
`BaseAbacService` configures their access-control command groups. Shared auth,
organization, RBAC, and system service contracts are re-exported for
application composition.
"""

# pylint: disable=useless-import-alias

from gen_epix.commondb.domain.service import (
    BaseOrganizationService as BaseOrganizationService,
)
from gen_epix.commondb.domain.service import BaseRbacService as BaseRbacService
from gen_epix.commondb.domain.service import BaseSystemService as BaseSystemService
from gen_epix.fastapp.services.auth import BaseAuthService as BaseAuthService
from gen_epix.omopdb.domain.service.abac import BaseAbacService as BaseAbacService
from gen_epix.omopdb.domain.service.omop import BaseOmopService as BaseOmopService
