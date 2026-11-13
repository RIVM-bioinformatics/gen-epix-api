"""Unit tests for gen_epix.casedb.domain.service.ontology."""

from test.util.mock_compat import MagicMock

import pytest

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.service import ontology as module
from gen_epix.casedb.domain.service.ontology import BaseOntologyService


class _Service(BaseOntologyService):
    """Concrete service; the update_association handler is stubbed out."""

    def crud(self, *args, **kwargs):  # pragma: no cover - never invoked
        raise NotImplementedError()


@pytest.fixture(name="app")
def app_fixture() -> MagicMock:
    app = MagicMock()
    app.domain.get_crud_commands_for_service_type.return_value = frozenset(
        {command.ConceptCrudCommand, command.DiseaseCrudCommand}
    )
    app.domain.get_commands_for_service_type.return_value = frozenset(
        {command.DiseaseEtiologicalAgentUpdateAssociationCommand}
    )
    return app


def _registered(app: MagicMock) -> dict:
    return {c.args[0]: c.args[1] for c in app.register_handler.call_args_list}


def test_service_type_constant() -> None:
    assert module.BaseOntologyService.SERVICE_TYPE == ServiceType.ONTOLOGY


def test_register_handlers_registers_crud_and_association_handlers(
    app: MagicMock,
) -> None:
    service = _Service(app, service_type=ServiceType.ONTOLOGY)

    registered = _registered(app)
    assert registered == {
        command.ConceptCrudCommand: service.crud,
        command.DiseaseCrudCommand: service.crud,
        command.DiseaseEtiologicalAgentUpdateAssociationCommand: (
            service.update_association
        ),
    }


def test_register_handlers_queries_ontology_association_commands(
    app: MagicMock,
) -> None:
    _Service(app, service_type=ServiceType.ONTOLOGY)

    app.domain.get_commands_for_service_type.assert_called_once_with(
        ServiceType.ONTOLOGY, base_class=command.UpdateAssociationCommand
    )
    app.domain.get_crud_commands_for_service_type.assert_called_once_with(
        ServiceType.ONTOLOGY
    )


def test_register_handlers_without_association_commands(app: MagicMock) -> None:
    app.domain.get_commands_for_service_type.return_value = frozenset()

    service = _Service(app, service_type=ServiceType.ONTOLOGY)

    assert set(_registered(app)) == {
        command.ConceptCrudCommand,
        command.DiseaseCrudCommand,
    }
    assert service.service_type == ServiceType.ONTOLOGY


def test_register_handlers_not_called_when_disabled(app: MagicMock) -> None:
    _Service(app, service_type=ServiceType.ONTOLOGY, register_handlers=False)

    app.register_handler.assert_not_called()
