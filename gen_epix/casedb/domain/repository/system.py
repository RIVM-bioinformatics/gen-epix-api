from gen_epix.casedb.domain import DOMAIN
from gen_epix.casedb.domain import model as model  # forces models to be registered now
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.common.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)


class BaseSystemRepository(CommonBaseSystemRepository):
    ENTITIES = DOMAIN.get_dag_sorted_entities(
        service_type=ServiceType.SYSTEM, persistable=True
    )
