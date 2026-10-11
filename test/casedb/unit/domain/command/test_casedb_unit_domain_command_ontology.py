"""Test casedb ontology command definitions."""

from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.command import ontology
from gen_epix.commondb.domain.command import CrudCommand
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import CrudOperation

CRUD_COMMAND_MODELS = [
    pytest.param(ontology.ConceptCrudCommand, model.Concept, id="concept"),
    pytest.param(ontology.ConceptSetCrudCommand, model.ConceptSet, id="concept-set"),
    pytest.param(
        ontology.ConceptRelationCrudCommand,
        model.ConceptRelation,
        id="concept-relation",
    ),
    pytest.param(ontology.DiseaseCrudCommand, model.Disease, id="disease"),
    pytest.param(
        ontology.EtiologicalAgentCrudCommand,
        model.EtiologicalAgent,
        id="etiological-agent",
    ),
    pytest.param(ontology.EtiologyCrudCommand, model.Etiology, id="etiology"),
]


@pytest.fixture(name="disease_id")
def disease_id_fixture() -> UUID:
    """Provide a fresh disease ID."""
    return uuid4()


@pytest.fixture(name="make_etiology")
def make_etiology_fixture():
    """Create an etiology for the given disease and a fresh agent."""

    def _make(disease_id: UUID, agent_id: UUID | None = None) -> model.Etiology:
        return model.Etiology(
            disease_id=disease_id, etiological_agent_id=agent_id or uuid4()
        )

    return _make


@pytest.mark.parametrize("command_class, model_class", CRUD_COMMAND_MODELS)
def test_crud_command_binds_model_class(
    command_class: type[CrudCommand], model_class: type[model.Model]
) -> None:
    """Bind each CRUD command to its ontology model."""
    assert issubclass(command_class, CrudCommand)
    assert command_class.MODEL_CLASS is model_class


@pytest.mark.parametrize("command_class, _", CRUD_COMMAND_MODELS)
def test_crud_command_accepts_read_all(
    command_class: type[CrudCommand], _: type[model.Model]
) -> None:
    """Build a read-all command without objects."""
    command = command_class(operation=CrudOperation.READ_ALL)

    assert command.is_read_all()
    assert command.get_objs() is None


def test_association_command_class_variables() -> None:
    """Link diseases to etiological agents through the etiology model."""
    command_class = ontology.DiseaseEtiologicalAgentUpdateAssociationCommand

    assert command_class.ASSOCIATION_CLASS is model.Etiology
    assert command_class.LINK_FIELD_NAME1 == "disease_id"
    assert command_class.LINK_FIELD_NAME2 == "etiological_agent_id"


def test_association_command_with_matching_objs(disease_id, make_etiology) -> None:
    """Accept association objects that all belong to obj_id1."""
    objs = [make_etiology(disease_id), make_etiology(disease_id)]

    command = ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(
        obj_id1=disease_id, association_objs=objs
    )

    assert command.obj_id1 == disease_id
    assert command.obj_id2 is None
    assert command.association_objs == objs


def test_association_command_with_matching_obj_id2(disease_id, make_etiology) -> None:
    """Accept association objects that all reference obj_id2 as agent."""
    agent_id = uuid4()
    objs = [make_etiology(disease_id, agent_id), make_etiology(uuid4(), agent_id)]

    command = ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(
        obj_id2=agent_id, association_objs=objs
    )

    assert command.obj_id2 == agent_id


def test_association_command_requires_association_objs_field() -> None:
    """Reject omission of association_objs, which has no default."""
    with pytest.raises(ValueError):
        ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(obj_id1=uuid4())


def test_association_command_allows_id_with_empty_objs(disease_id) -> None:
    """Allow an empty list with an endpoint id, replacing with no links."""
    command = ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(
        obj_id1=disease_id, association_objs=[]
    )

    assert not command.association_objs


def test_association_command_rejects_empty_without_ids() -> None:
    """Reject empty objects without any endpoint id."""
    with pytest.raises(exc.DomainException):
        ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(association_objs=[])


def test_association_command_rejects_both_ids() -> None:
    """Reject both endpoint ids being set."""
    with pytest.raises(exc.DomainException):
        ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(
            obj_id1=uuid4(), obj_id2=uuid4(), association_objs=[]
        )


def test_association_command_rejects_mismatching_obj_id1(
    disease_id, make_etiology
) -> None:
    """Reject association objects belonging to another disease."""
    with pytest.raises(exc.DomainException):
        ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(
            obj_id1=disease_id,
            association_objs=[make_etiology(disease_id), make_etiology(uuid4())],
        )


def test_association_command_rejects_mismatching_obj_id2(
    disease_id, make_etiology
) -> None:
    """Reject association objects belonging to another agent."""
    with pytest.raises(exc.DomainException):
        ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(
            obj_id2=uuid4(), association_objs=[make_etiology(disease_id)]
        )


def test_association_command_rejects_wrong_object_type(disease_id) -> None:
    """Reject association objects that are not etiologies."""
    with pytest.raises(ValueError):
        ontology.DiseaseEtiologicalAgentUpdateAssociationCommand(
            obj_id1=disease_id, association_objs=[model.Disease(name="flu")]
        )
