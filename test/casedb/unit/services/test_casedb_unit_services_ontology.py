from test.util.mock_compat import Mock

from gen_epix.casedb.domain import command, enum
from gen_epix.casedb.services.ontology import OntologyService


def test_init_registers_ontology_association_handler() -> None:
    app = Mock()
    app.domain.get_crud_commands_for_service_type.return_value = []
    app.domain.get_commands_for_service_type.return_value = [
        command.UpdateAssociationCommand
    ]

    service = OntologyService(app=app, service_type=enum.ServiceType.ONTOLOGY)

    app.domain.register_service_type.assert_called_once_with(enum.ServiceType.ONTOLOGY)
    app.register_handler.assert_called_once_with(
        command.UpdateAssociationCommand, service.update_association
    )
