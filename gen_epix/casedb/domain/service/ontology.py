"""Define ontology command registration for Casedb services."""

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseOntologyRepository
from gen_epix.fastapp import BaseService


class BaseOntologyService(BaseService[BaseOntologyRepository]):
    """Encapsulates ontology CRUD and association-update dispatch."""

    SERVICE_TYPE = ServiceType.ONTOLOGY

    def register_handlers(self) -> None:
        """Register ontology CRUD and association-update command handlers.

        This discovers ontology association commands from domain metadata and
        mutates the application dispatch table during service initialization.
        """
        f = self.app.register_handler
        self.register_default_crud_handlers()
        for command_class in self.app.domain.get_commands_for_service_type(
            ServiceType.ONTOLOGY, base_class=command.UpdateAssociationCommand
        ):
            f(command_class, self.update_association)
