# pylint: disable=useless-import-alias
from typing import Type

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.service.abac import BaseAbacService as BaseAbacService
from gen_epix.casedb.domain.service.case import BaseCaseService as BaseCaseService
from gen_epix.casedb.domain.service.geo import BaseGeoService as BaseGeoService
from gen_epix.casedb.domain.service.ontology import (
    BaseOntologyService as BaseOntologyService,
)
from gen_epix.casedb.domain.service.organization import (
    BaseOrganizationService as BaseOrganizationService,
)
from gen_epix.casedb.domain.service.rbac import BaseRbacService as BaseRbacService
from gen_epix.casedb.domain.service.seqdb import BaseSeqdbService as BaseSeqdbService
from gen_epix.casedb.domain.service.subject import (
    BaseSubjectService as BaseSubjectService,
)
from gen_epix.casedb.domain.service.system import BaseSystemService as BaseSystemService
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
    enum.ServiceType.GEO: BaseGeoService,
    enum.ServiceType.ONTOLOGY: BaseOntologyService,
    enum.ServiceType.ORGANIZATION: BaseOrganizationService,
    enum.ServiceType.AUTH: BaseAuthService,
    enum.ServiceType.SEQDB: BaseSeqdbService,
    enum.ServiceType.SUBJECT: BaseSubjectService,
    enum.ServiceType.CASE: BaseCaseService,
    enum.ServiceType.ABAC: BaseAbacService,
    enum.ServiceType.SYSTEM: BaseSystemService,
    enum.ServiceType.RBAC: BaseRbacService,
}
