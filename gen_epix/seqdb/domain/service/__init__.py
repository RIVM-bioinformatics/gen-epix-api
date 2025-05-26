# pylint: disable=useless-import-alias
from typing import Type

from gen_epix.fastapp import BaseService
from gen_epix.fastapp.services.auth import BaseAuthService as BaseAuthService
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.service.abac import BaseAbacService as BaseAbacService
from gen_epix.seqdb.domain.service.organization import (
    BaseOrganizationService as BaseOrganizationService,
)
from gen_epix.seqdb.domain.service.rbac import BaseRbacService as BaseRbacService
from gen_epix.seqdb.domain.service.seq import BaseSeqService as BaseSeqService
from gen_epix.seqdb.domain.service.system import BaseSystemService as BaseSystemService

ORDERED_SERVICE_TYPES: list[enum.ServiceType] = [
    enum.ServiceType.ORGANIZATION,
    enum.ServiceType.AUTH,
    enum.ServiceType.ABAC,
    enum.ServiceType.SYSTEM,
    enum.ServiceType.SEQ,
    enum.ServiceType.RBAC,
]

BASE_SERVICE_CLASS_MAP: dict[enum.ServiceType, Type[BaseService]] = {
    enum.ServiceType.ORGANIZATION: BaseOrganizationService,
    enum.ServiceType.AUTH: BaseAuthService,
    enum.ServiceType.ABAC: BaseAbacService,
    enum.ServiceType.SYSTEM: BaseSystemService,
    enum.ServiceType.SEQ: BaseSeqService,
    enum.ServiceType.RBAC: BaseRbacService,
}
