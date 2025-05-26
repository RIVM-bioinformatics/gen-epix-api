import abc

from gen_epix.casedb.domain import model  # forces models to be registered now
from gen_epix.casedb.domain import DOMAIN
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.fastapp import BaseRepository, BaseUnitOfWork


class BaseOrganizationRepository(BaseRepository):
    ENTITIES = DOMAIN.get_dag_sorted_entities(
        service_type=ServiceType.ORGANIZATION, persistable=True
    )

    @abc.abstractmethod
    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        raise NotImplementedError()
