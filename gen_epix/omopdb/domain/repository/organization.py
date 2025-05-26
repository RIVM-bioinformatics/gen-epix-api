import abc

from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import model  # forces models to be registered now
from gen_epix.omopdb.domain import DOMAIN
from gen_epix.omopdb.domain.enum import ServiceType


class BaseOrganizationRepository(BaseRepository):
    ENTITIES = DOMAIN.get_dag_sorted_entities(
        service_type=ServiceType.ORGANIZATION, persistable=True
    )

    @abc.abstractmethod
    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        raise NotImplementedError()
