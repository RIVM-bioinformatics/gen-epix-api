# pylint: disable=useless-import-alias
from typing import Type

from gen_epix.common.domain.service.organization import (
    BaseOrganizationService as BaseOrganizationService,
)
from gen_epix.common.domain.service.rbac import BaseRbacService as BaseRbacService
from gen_epix.common.domain.service.system import BaseSystemService as BaseSystemService
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.services.auth import BaseAuthService as BaseAuthService
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.service.abac import BaseAbacService as BaseAbacService
from gen_epix.seqdb.domain.service.seq import BaseSeqService as BaseSeqService

ORDERED_SERVICE_TYPES: list[enum.ServiceType] = [
    enum.ServiceType.ORGANIZATION,
    enum.ServiceType.AUTH,
    enum.ServiceType.ABAC,
    enum.ServiceType.SYSTEM,
    enum.ServiceType.SEQ,
    enum.ServiceType.RBAC,
]

BASE_SERVICE_CLASS_MAP: dict[enum.ServiceType, Type[BaseService]] = {
    enum.ServiceType.ORGANIZATION: BaseOrganizationService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.AUTH: BaseAuthService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.ABAC: BaseAbacService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.SYSTEM: BaseSystemService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.SEQ: BaseSeqService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.RBAC: BaseRbacService,  # type: ignore[type-abstract] # Abstract class is ok here
}
