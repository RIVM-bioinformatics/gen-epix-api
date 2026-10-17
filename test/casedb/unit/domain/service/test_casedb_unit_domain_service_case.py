"""Unit tests for the Casedb case service base class."""

import inspect
from test.util.mock_compat import MagicMock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.service.case import BaseCaseService

_ABSTRACT_NAMES = sorted(BaseCaseService.__abstractmethods__)

_SHARED_HANDLER_NAMES = {
    command.CaseTypeSetCaseTypeUpdateAssociationCommand: "update_association",
    command.ColSetColUpdateAssociationCommand: "update_association",
    command.RetrieveCaseSetStatsCommand: "retrieve_case_stats",
    command.RetrieveCaseTypeStatsCommand: "retrieve_case_stats",
    command.RetrieveCaseRightsCommand: "retrieve_case_or_set_rights",
    command.RetrieveCaseSetRightsCommand: "retrieve_case_or_set_rights",
}


def _make_concrete_class() -> type[BaseCaseService]:
    """Create a subclass implementing every abstract method as a stub."""
    namespace = {name: (lambda self, cmd: None) for name in _ABSTRACT_NAMES}
    return type("ConcreteCaseService", (BaseCaseService,), namespace)


@pytest.fixture
def app() -> MagicMock:
    """Provide a mocked application."""
    mock_app = MagicMock()
    mock_app.generate_id.return_value = uuid4()
    return mock_app


@pytest.fixture
def service_class() -> type[BaseCaseService]:
    """Provide a concrete service class."""
    return _make_concrete_class()


@pytest.fixture
def make_service(app, service_class):
    """Provide a factory building concrete services on the mocked app."""

    def factory(**kwargs) -> BaseCaseService:
        return service_class(app, **kwargs)

    return factory


class TestClassConstants:
    def test_service_type(self):
        assert BaseCaseService.SERVICE_TYPE is ServiceType.CASE

    def test_default_limits(self):
        assert BaseCaseService.DEFAULT_CREATE_MAX_N_CASES == 1000
        assert BaseCaseService.DEFAULT_READ_MAX_N_CASES == 1000
        assert BaseCaseService.DEFAULT_READ_MAX_TREE_SIZE == 1000
        assert BaseCaseService.DEFAULT_UPDATE_MAX_N_CASES == 1000
        assert BaseCaseService.DEFAULT_DELETE_MAX_N_CASES == 1000

    def test_abac_command_sets_are_disjoint(self):
        no_abac = BaseCaseService.NO_ABAC_COMMAND_CLASSES
        refdata = BaseCaseService.ABAC_REFDATA_COMMAND_CLASSES
        data = BaseCaseService.ABAC_DATA_COMMAND_CLASSES
        assert not no_abac & refdata
        assert not no_abac & data
        assert not refdata & data

    @pytest.mark.parametrize(
        "parent, expected",
        [
            (model.CaseTypeSet, (model.CaseTypeSetMember,)),
            (model.CaseType, (model.CaseTypeSetMember,)),
            (model.ColSet, (model.ColSetMember,)),
            (model.Col, (model.ColSetMember,)),
            (
                model.CaseSet,
                (model.CaseSetDataCollectionLink, model.CaseSetMember),
            ),
            (model.Case, (model.CaseDataCollectionLink, model.CaseSetMember)),
        ],
        ids=lambda v: getattr(v, "__name__", None),
    )
    def test_cascade_delete_models(self, parent, expected):
        assert BaseCaseService.CASCADE_DELETE_MODEL_CLASSES[parent] == expected

    def test_cascade_delete_keys_exactly(self):
        assert set(BaseCaseService.CASCADE_DELETE_MODEL_CLASSES) == {
            model.CaseTypeSet,
            model.CaseType,
            model.ColSet,
            model.Col,
            model.CaseSet,
            model.Case,
        }


class TestAbstractInterface:
    def test_cannot_instantiate_base(self, app):
        with pytest.raises(TypeError):
            BaseCaseService(app)

    @pytest.mark.parametrize("name", _ABSTRACT_NAMES)
    def test_stub_raises_not_implemented(self, name):
        method = getattr(BaseCaseService, name)
        n_args = len(inspect.signature(method).parameters) - 1
        with pytest.raises(NotImplementedError):
            method(None, *([None] * n_args))

    def test_partial_subclass_cannot_instantiate(self, app):
        partial = type("Partial", (BaseCaseService,), {"crud_case": lambda s, c: 1})
        with pytest.raises(TypeError):
            partial(app)


class TestInit:
    def test_default_props_when_omitted(self, make_service):
        props = make_service()._default_props
        assert props.create_max_n_cases == BaseCaseService.DEFAULT_CREATE_MAX_N_CASES
        assert props.read_max_n_cases == BaseCaseService.DEFAULT_READ_MAX_N_CASES
        assert props.read_max_tree_size == BaseCaseService.DEFAULT_READ_MAX_TREE_SIZE
        assert props.update_max_n_cases == BaseCaseService.DEFAULT_UPDATE_MAX_N_CASES
        assert props.delete_max_n_cases == BaseCaseService.DEFAULT_DELETE_MAX_N_CASES

    def test_default_props_none_uses_builtins(self, make_service):
        assert make_service(default_props=None)._default_props.create_max_n_cases == (
            BaseCaseService.DEFAULT_CREATE_MAX_N_CASES
        )

    def test_explicit_default_props_used_as_is(self, make_service):
        props = model.CaseTypeProps(create_max_n_cases=5, read_max_n_cases=7)
        service = make_service(default_props=props)
        assert service._default_props is props

    def test_kwargs_forwarded_to_base(self, make_service, app):
        service = make_service(name="case-service", id="abc")
        assert service.name == "case-service"
        assert service.id == "abc"
        assert service.app is app

    def test_register_handlers_called_by_default(self, make_service, app):
        make_service()
        assert app.register_handler.called

    def test_register_handlers_skipped_when_disabled(self, make_service, app):
        make_service(register_handlers=False)
        app.register_handler.assert_not_called()


class TestRegisterHandlers:
    @pytest.fixture
    def registered(self, make_service, app):
        service = make_service()
        return service, {
            c.args[0]: c.args[1] for c in app.register_handler.call_args_list
        }

    def test_no_duplicate_registrations(self, make_service, app):
        make_service()
        classes = [c.args[0] for c in app.register_handler.call_args_list]
        assert len(classes) == len(set(classes))

    def test_all_crud_commands_in_abac_sets_are_registered(self, registered):
        _, handlers = registered
        for cls in (
            BaseCaseService.NO_ABAC_COMMAND_CLASSES
            | BaseCaseService.ABAC_REFDATA_COMMAND_CLASSES
            | BaseCaseService.ABAC_DATA_COMMAND_CLASSES
        ):
            assert cls in handlers

    def test_specialized_handlers_are_bound_methods(self, registered):
        service, handlers = registered
        for cls, handler in handlers.items():
            name = _SHARED_HANDLER_NAMES.get(cls)
            if name is not None:
                assert handler == getattr(service, name)
            else:
                assert handler.__self__ is service

    @pytest.mark.parametrize(
        "cmd_class, method_name",
        [
            (command.CaseCrudCommand, "crud_case"),
            (command.CaseSetCrudCommand, "crud_case_set"),
            (command.ColCrudCommand, "crud_col"),
            (command.UploadCasesCommand, "upload_cases"),
            (command.CreateCaseSetCommand, "create_case_set"),
            (command.RetrieveCasesByIdCommand, "retrieve_cases_by_id"),
            (command.RetrieveIsOwnCasesCommand, "retrieve_is_own_cases"),
            (command.RetrieveProtocolsCommand, "retrieve_protocols"),
            (command.CreateFileForSeqCommand, "create_file_for_seq"),
            (command.CreateFileForReadSetCommand, "create_file_for_read_set"),
            (
                command.UpdateCaseCreatedInDataCollectionCommand,
                "update_case_created_in_data_collection",
            ),
        ],
        ids=lambda v: getattr(v, "__name__", v),
    )
    def test_command_bound_to_method(self, registered, cmd_class, method_name):
        service, handlers = registered
        assert handlers[cmd_class] == getattr(service, method_name)

    @pytest.mark.parametrize(
        "cmd_class, method_name",
        list(_SHARED_HANDLER_NAMES.items()),
        ids=lambda v: getattr(v, "__name__", v),
    )
    def test_shared_handlers(self, registered, cmd_class, method_name):
        service, handlers = registered
        assert handlers[cmd_class] == getattr(service, method_name)
