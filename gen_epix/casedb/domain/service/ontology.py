from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseOntologyRepository
from gen_epix.fastapp import BaseService


class BaseOntologyService(BaseService):
    SERVICE_TYPE = ServiceType.ONTOLOGY

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseOntologyRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        for command_class in self.app.domain.get_commands_for_service_type(
            ServiceType.ONTOLOGY, base_class=command.UpdateAssociationCommand
        ):
            f(command_class, self.update_association)
