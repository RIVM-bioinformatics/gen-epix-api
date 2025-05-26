from gen_epix.fastapp import BaseService
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class BaseOmopService(BaseService):
    SERVICE_TYPE = ServiceType.OMOP

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseOmopRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        for command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            f(command_class, self.crud)
