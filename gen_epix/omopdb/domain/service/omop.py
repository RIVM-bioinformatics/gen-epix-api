from abc import abstractmethod

from gen_epix.fastapp import BaseService
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class BaseOmopService(BaseService[BaseOmopRepository]):
    SERVICE_TYPE = ServiceType.OMOP

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()
        f = self.app.register_handler
        f(command.UploadPersonsCommand, self.upload_persons)
        f(command.RetrievePersonsByIdCommand, self.retrieve_persons_by_id)
        f(command.RetrievePersonsByQueryCommand, self.retrieve_persons_by_query)

    @abstractmethod
    def upload_persons(
        self, cmd: command.UploadPersonsCommand
    ) -> model.PersonBatchUploadResult:
        raise NotImplementedError("Must be implemented in subclass")

    @abstractmethod
    def retrieve_persons_by_id(
        self, cmd: command.RetrievePersonsByIdCommand
    ) -> list[model.FullPerson]:
        raise NotImplementedError("Must be implemented in subclass")

    @abstractmethod
    def retrieve_persons_by_query(
        self, cmd: command.RetrievePersonsByQueryCommand
    ) -> model.PersonQueryResult:
        raise NotImplementedError("Must be implemented in subclass")
