# pylint: disable=useless-import-alias
from typing import Type

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.service.abac import BaseAbacService as BaseAbacService
from gen_epix.casedb.domain.service.case import BaseCaseService as BaseCaseService
from gen_epix.casedb.domain.service.geo import BaseGeoService as BaseGeoService
from gen_epix.casedb.domain.service.ontology import (
    BaseOntologyService as BaseOntologyService,
)
from gen_epix.casedb.domain.service.seqdb import BaseSeqdbService as BaseSeqdbService
from gen_epix.casedb.domain.service.subject import (
    BaseSubjectService as BaseSubjectService,
)
from gen_epix.common.domain.service.organization import (
    BaseOrganizationService as BaseOrganizationService,
)
from gen_epix.common.domain.service.rbac import BaseRbacService as BaseRbacService
from gen_epix.common.domain.service.system import BaseSystemService as BaseSystemService
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.services.auth import BaseAuthService as BaseAuthService

ORDERED_SERVICE_TYPES: list[enum.ServiceType] = [
    enum.ServiceType.GEO,
    enum.ServiceType.ONTOLOGY,
    enum.ServiceType.ORGANIZATION,
    enum.ServiceType.AUTH,
    enum.ServiceType.SEQDB,
    enum.ServiceType.SUBJECT,
    enum.ServiceType.CASE,
    enum.ServiceType.ABAC,
    enum.ServiceType.SYSTEM,
    enum.ServiceType.RBAC,
]

BASE_SERVICE_CLASS_MAP: dict[enum.ServiceType, Type[BaseService]] = {
    enum.ServiceType.GEO: BaseGeoService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.ONTOLOGY: BaseOntologyService,
    enum.ServiceType.ORGANIZATION: BaseOrganizationService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.AUTH: BaseAuthService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.SEQDB: BaseSeqdbService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.SUBJECT: BaseSubjectService,
    enum.ServiceType.CASE: BaseCaseService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.ABAC: BaseAbacService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.SYSTEM: BaseSystemService,  # type: ignore[type-abstract] # Abstract class is ok here
}
