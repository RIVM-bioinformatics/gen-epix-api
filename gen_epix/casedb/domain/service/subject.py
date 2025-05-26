from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository.subject import BaseSubjectRepository
from gen_epix.fastapp import BaseService


class BaseSubjectService(BaseService):
    SERVICE_TYPE = ServiceType.SUBJECT

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseSubjectRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        for command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            f(command_class, self.crud)
