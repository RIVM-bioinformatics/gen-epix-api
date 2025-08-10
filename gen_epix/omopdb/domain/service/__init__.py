# pylint: disable=useless-import-alias
from typing import Type

from gen_epix.common.domain.service.organization import (
    BaseOrganizationService as BaseOrganizationService,
)
from gen_epix.common.domain.service.rbac import BaseRbacService as BaseRbacService
from gen_epix.common.domain.service.system import BaseSystemService as BaseSystemService
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.services.auth import BaseAuthService as BaseAuthService
from gen_epix.omopdb.domain import enum
from gen_epix.omopdb.domain.service.omop import BaseOmopService as BaseOmopService

ORDERED_SERVICE_TYPES: list[enum.ServiceType] = [
    enum.ServiceType.ORGANIZATION,
    enum.ServiceType.AUTH,
    enum.ServiceType.SYSTEM,
    enum.ServiceType.OMOP,
    enum.ServiceType.RBAC,
]

BASE_SERVICE_CLASS_MAP: dict[enum.ServiceType, Type[BaseService]] = {
    enum.ServiceType.ORGANIZATION: BaseOrganizationService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.AUTH: BaseAuthService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.SYSTEM: BaseSystemService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.OMOP: BaseOmopService,  # type: ignore[type-abstract] # Abstract class is ok here
    enum.ServiceType.RBAC: BaseRbacService,  # type: ignore[type-abstract] # Abstract class is ok here
}
