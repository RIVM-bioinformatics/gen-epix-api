from gen_epix.common.domain.repository import (
    BaseOrganizationRepository as CommonBaseOrganizationRepository,
)
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import model as model  # forces models to be registered now
from gen_epix.seqdb.domain.enum import ServiceType


class BaseOrganizationRepository(CommonBaseOrganizationRepository):
    ENTITIES = DOMAIN.get_dag_sorted_entities(
        service_type=ServiceType.ORGANIZATION, persistable=True
    )
