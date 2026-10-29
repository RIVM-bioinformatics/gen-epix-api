"""Unit tests for the casedb Seqdb service base class."""

from test.util.mock_compat import Mock, call

import pytest

import gen_epix.seqdb.domain.command as seqdb_command
from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.service import seqdb
from gen_epix.casedb.domain.service.seqdb import BaseSeqdbService

ABSTRACT_METHODS = {
    "retrieve_phylogenetic_tree",
    "retrieve_genetic_sequence_fasta_by_id",
    "upload_samples",
    "create_file",
    "retrieve_similar_profiles",
    "retrieve_seq_distances_by_seq_profiles",
}

HANDLER_BINDINGS = [
    (
        command.RetrievePhylogeneticTreeByProfilesCommand,
        "retrieve_phylogenetic_tree",
    ),
    (
        command.RetrieveGeneticSequenceFastaByIdCommand,
        "retrieve_genetic_sequence_fasta_by_id",
    ),
    (seqdb_command.UploadSamplesCommand, "upload_samples"),
    (seqdb_command.CreateFileCommand, "create_file"),
    (seqdb_command.ProtocolCrudCommand, "crud"),
    (seqdb_command.ReadSetCrudCommand, "crud"),
    (seqdb_command.FileCrudCommand, "crud"),
    (seqdb_command.SeqCrudCommand, "crud"),
    (
        seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand,
        "retrieve_seq_distances_by_seq_profiles",
    ),
    (seqdb_command.RetrieveSimilarProfilesCommand, "retrieve_similar_profiles"),
]


class _SeqdbService(BaseSeqdbService):
    def retrieve_phylogenetic_tree(self, cmd):  # type: ignore[no-untyped-def]
        return None

    def retrieve_genetic_sequence_fasta_by_id(self, cmd):  # type: ignore[no-untyped-def]
        return []

    def upload_samples(self, cmd):  # type: ignore[no-untyped-def]
        return None

    def create_file(self, cmd):  # type: ignore[no-untyped-def]
        return None

    def retrieve_similar_profiles(self, cmd):  # type: ignore[no-untyped-def]
        return []

    def retrieve_seq_distances_by_seq_profiles(self, cmd):  # type: ignore[no-untyped-def]
        return []


@pytest.fixture
def app() -> Mock:
    app = Mock()
    app.generate_id.return_value = "id-1"
    app.domain.get_crud_commands_for_service_type.return_value = []
    return app


@pytest.fixture
def make_service(app: Mock):
    def _make(**kwargs) -> _SeqdbService:  # type: ignore[no-untyped-def]
        kwargs.setdefault("service_type", ServiceType.SEQDB)
        return _SeqdbService(app, **kwargs)

    return _make


def test_service_type_is_seqdb() -> None:
    assert BaseSeqdbService.SERVICE_TYPE == ServiceType.SEQDB


def test_module_exports_service_class() -> None:
    assert seqdb.BaseSeqdbService is BaseSeqdbService


def test_abstract_methods_are_exactly_the_remote_operations() -> None:
    assert set(BaseSeqdbService.__abstractmethods__) == ABSTRACT_METHODS


def test_base_class_is_abstract(app: Mock) -> None:
    with pytest.raises(TypeError, match="abstract"):
        BaseSeqdbService(app)  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated


@pytest.mark.parametrize("method_name", sorted(ABSTRACT_METHODS))
def test_abstract_method_bodies_raise_not_implemented(
    make_service, method_name: str
) -> None:
    service = make_service()

    with pytest.raises(NotImplementedError):
        getattr(BaseSeqdbService, method_name)(service, Mock())


@pytest.mark.parametrize(
    "command_class, handler_name",
    HANDLER_BINDINGS,
    ids=[b[0].__name__ for b in HANDLER_BINDINGS],
)
def test_register_handlers_registers_command_handler(
    app: Mock, make_service, command_class, handler_name: str
) -> None:
    service = make_service()

    assert (
        call(command_class, getattr(service, handler_name))
        in app.register_handler.call_args_list
    )


def test_register_handlers_registers_each_command_once(app: Mock, make_service) -> None:
    make_service()

    registered = [c.args[0] for c in app.register_handler.call_args_list]
    assert len(registered) == len(set(registered))


def test_register_handlers_registers_default_crud_commands(
    app: Mock, make_service
) -> None:
    crud_cmd_class = Mock()
    app.domain.get_crud_commands_for_service_type.return_value = [crud_cmd_class]

    service = make_service()

    app.domain.get_crud_commands_for_service_type.assert_called_once_with(
        ServiceType.SEQDB
    )
    assert call(crud_cmd_class, service.crud) in app.register_handler.call_args_list
