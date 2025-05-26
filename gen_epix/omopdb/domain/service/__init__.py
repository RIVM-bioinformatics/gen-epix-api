# pylint: disable=useless-import-alias
from typing import Type

from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.services.auth.base import BaseAuthService
from gen_epix.omopdb.domain import enum
from gen_epix.omopdb.domain.service.omop import BaseOmopService as BaseOmopService
from gen_epix.omopdb.domain.service.organization import (
    BaseOrganizationService as BaseOrganizationService,
)
from gen_epix.omopdb.domain.service.rbac import BaseRbacService as BaseRbacService
from gen_epix.omopdb.domain.service.system import BaseSystemService as BaseSystemService

ORDERED_SERVICE_TYPES: list[enum.ServiceType] = [
    enum.ServiceType.ORGANIZATION,
    enum.ServiceType.AUTH,
    enum.ServiceType.SYSTEM,
    enum.ServiceType.OMOP,
    enum.ServiceType.RBAC,
]

BASE_SERVICE_CLASS_MAP: dict[enum.ServiceType, Type[BaseService]] = {
    enum.ServiceType.ORGANIZATION: BaseOrganizationService,
    enum.ServiceType.AUTH: BaseAuthService,
    enum.ServiceType.SYSTEM: BaseSystemService,
    enum.ServiceType.OMOP: BaseOmopService,
    enum.ServiceType.RBAC: BaseRbacService,
}
