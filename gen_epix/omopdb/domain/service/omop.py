from abc import abstractmethod

from gen_epix.fastapp import BaseService
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class BaseOmopService(BaseService):
    SERVICE_TYPE = ServiceType.OMOP

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseOmopRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()
        f = self.app.register_handler
        f(command.UploadPersonsCommand, self.upload_persons)

    @abstractmethod
    def upload_persons(
        self, cmd: command.UploadPersonsCommand
    ) -> model.PersonBatchUploadResult:
        raise NotImplementedError("Must be implemented in subclass")
