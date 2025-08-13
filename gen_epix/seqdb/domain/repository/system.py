from gen_epix.common.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import model as model  # forces models to be registered now
from gen_epix.seqdb.domain.enum import ServiceType


class BaseSystemRepository(CommonBaseSystemRepository):
    ENTITIES = DOMAIN.get_dag_sorted_entities(
        service_type=ServiceType.SYSTEM, persistable=True
    )
