from sqlalchemy import Engine, select

from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.seqdb.domain import exc, model
from gen_epix.seqdb.domain.repository.organization import BaseOrganizationRepository
from gen_epix.seqdb.repositories import sa_model
from gen_epix.seqdb.repositories.sa_model.base import (
    DB_METADATA_FIELDS,
    GENERATE_SERVICE_METADATA,
    SERVICE_METADATA_FIELDS,
)


class OrganizationSARepository(SARepository, BaseOrganizationRepository):
    def __init__(self, engine: Engine, **kwargs: dict):
        entities = kwargs.pop("entities", BaseOrganizationRepository.ENTITIES)
        super().__init__(
            engine,
            entities=entities,
            service_metadata_fields=SERVICE_METADATA_FIELDS,
            db_metadata_fields=DB_METADATA_FIELDS,
            generate_service_metadata=GENERATE_SERVICE_METADATA,
            **kwargs,
        )

    def is_existing_user_by_key(
        self, uow: BaseUnitOfWork, user_key: str | None
    ) -> bool:
        if user_key is None:
            return False
        assert isinstance(uow, SAUnitOfWork)
        user_row = uow.session.execute(
            select(sa_model.User.id).where(sa_model.User.email == user_key)
        ).all()
        return True if user_row else False

    def retrieve_user_by_key(self, uow: BaseUnitOfWork, user_key: str) -> model.User:
        users = self.crud(
            uow,
            None,
            model.User,
            None,
            None,
            CrudOperation.READ_ALL,
        )
        for user in users:
            if user.email == user_key.lower():
                return user
        raise exc.NoResultsError()
