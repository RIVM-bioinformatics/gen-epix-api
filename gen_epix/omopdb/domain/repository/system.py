from gen_epix.fastapp import BaseRepository
from gen_epix.omopdb.domain import DOMAIN
from gen_epix.omopdb.domain import model as model  # forces models to be registered now
from gen_epix.omopdb.domain.enum import ServiceType


class BaseSystemRepository(BaseRepository):
    ENTITIES = DOMAIN.get_dag_sorted_entities(
        service_type=ServiceType.SYSTEM, persistable=True
    )
