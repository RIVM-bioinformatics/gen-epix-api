"""Test shared system service operations."""

import json
from importlib import import_module
from test.util.mock_compat import Mock, patch

import pytest

from gen_epix.commondb.services.system import SystemService
from gen_epix.fastapp import CrudOperation


def _make_operational_data_service(
    app_name: str, handle
) -> tuple[Mock, type, SystemService]:
    """Create a system service whose app dispatches commands to ``handle``."""
    domain_module = import_module(f"gen_epix.{app_name}.domain")
    command_module = import_module(f"gen_epix.{app_name}.domain.command")
    app = Mock()
    app.domain = domain_module.DOMAIN
    app.handle.side_effect = handle
    service = object.__new__(SystemService)
    service._app = app
    return app, command_module.DeleteAllOperationalDataCommand, service


@pytest.mark.parametrize("app_name", ["casedb", "seqdb", "omopdb"])
def test_delete_all_operational_data_dispatches_each_model_in_order(
    app_name: str,
) -> None:
    """Delete every declared operational model and report individual failures."""
    failed_index = 1
    failed_models: list = []

    def handle(crud_command):
        if crud_command.MODEL_CLASS is failed_models[0]:
            raise RuntimeError("delete failed")
        return 7

    app, command_class, service = _make_operational_data_service(app_name, handle)
    failed_models.append(
        command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES[failed_index]
    )

    result = service.delete_all_operational_data(command_class(user=None))

    expected_models = command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES
    dispatched_commands = [call.args[0] for call in app.handle.call_args_list]
    assert [
        crud_command.MODEL_CLASS for crud_command in dispatched_commands
    ] == expected_models
    assert all(
        crud_command.operation == CrudOperation.DELETE_ALL
        and crud_command.return_count
        and not crud_command.return_id
        for crud_command in dispatched_commands
    )
    assert result.success is False
    assert result.details == {
        model_class.ENTITY.name: (
            "RuntimeError: delete failed" if model_class is failed_models[0] else "7"
        )
        for model_class in expected_models
    }


@pytest.mark.parametrize("app_name", ["casedb", "seqdb", "omopdb"])
def test_delete_all_operational_data_deletes_in_batches_until_a_short_batch(
    app_name: str,
) -> None:
    """Repeat the delete per model until a batch is smaller than the batch size."""
    remaining: dict = {}

    def handle(crud_command):
        n_remaining = remaining.setdefault(crud_command.MODEL_CLASS, 2500)
        n_deleted = min(n_remaining, crud_command.limit)
        remaining[crud_command.MODEL_CLASS] = n_remaining - n_deleted
        return n_deleted

    app, command_class, service = _make_operational_data_service(app_name, handle)

    result = service.delete_all_operational_data(command_class(user=None))

    assert result.success is True
    assert set(result.details.values()) == {"2500"}
    for model_class in command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES:
        batch_size = command_class.get_batch_size(model_class)
        calls = [
            call.args[0]
            for call in app.handle.call_args_list
            if call.args[0].MODEL_CLASS is model_class
        ]
        assert all(crud_command.limit == batch_size for crud_command in calls)
        assert len(calls) == 2500 // batch_size + 1


def test_delete_all_operational_data_one_more_call_when_the_last_batch_is_full() -> (
    None
):
    """A table with exactly a batch of rows needs a second call to see it is empty."""
    remaining: dict = {}

    def handle(crud_command):
        n_remaining = remaining.setdefault(crud_command.MODEL_CLASS, crud_command.limit)
        n_deleted = min(n_remaining, crud_command.limit)
        remaining[crud_command.MODEL_CLASS] = n_remaining - n_deleted
        return n_deleted

    app, command_class, service = _make_operational_data_service("casedb", handle)

    result = service.delete_all_operational_data(command_class(user=None))

    assert result.success is True
    n_models = len(command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES)
    assert app.handle.call_count == 2 * n_models
    assert set(result.details.values()) == {str(command_class.BATCH_SIZE)}


def test_seqdb_seq_distance_uses_a_smaller_batch_size() -> None:
    """Delete the largest SEQDB table in smaller batches than the default."""
    from gen_epix.seqdb.domain import model as seqdb_model
    from gen_epix.seqdb.domain.command import DeleteAllOperationalDataCommand

    assert (
        DeleteAllOperationalDataCommand.get_batch_size(seqdb_model.SeqDistance) == 500
    )
    assert (
        DeleteAllOperationalDataCommand.get_batch_size(seqdb_model.Sample)
        == DeleteAllOperationalDataCommand.BATCH_SIZE
    )


@pytest.mark.parametrize("app_name", ["casedb", "seqdb", "omopdb"])
def test_delete_all_ref_data_requires_empty_operational_models(app_name: str) -> None:
    """Do not delete reference data while a domain operational model has records."""
    domain_module = import_module(f"gen_epix.{app_name}.domain")
    command_module = import_module(f"gen_epix.{app_name}.domain.command")
    command_class = command_module.DeleteAllRefDataCommand
    app = Mock()
    app.domain = domain_module.DOMAIN
    ref_models = set(command_class.SORTED_REF_DATA_MODEL_CLASSES)
    linked_models = set(ref_models)
    persistable_models = app.domain.get_dag_sorted_models(persistable=True)
    while True:
        newly_linked_models = {
            model_class
            for model_class in persistable_models
            if model_class not in linked_models
            and any(
                link.link_model_class in linked_models
                for link in app.domain.get_model_links(model_class).values()
            )
        }
        if not newly_linked_models:
            break
        linked_models.update(newly_linked_models)
    operational_models = [
        model_class
        for model_class in app.domain.get_dag_sorted_models(
            persistable=True, reverse=True
        )
        if model_class in linked_models and model_class not in ref_models
    ]
    remaining_model = operational_models[0]

    def handle(crud_command):
        if crud_command.operation is CrudOperation.READ_ALL:
            return [object()] if crud_command.MODEL_CLASS is remaining_model else []
        raise AssertionError("reference deletion should not start")

    app.handle.side_effect = handle
    service = object.__new__(SystemService)
    service._app = app

    result = service.delete_all_ref_data(command_class(user=None))

    assert result.success is False
    assert remaining_model.ENTITY.name in result.details
    assert "delete all operational data" in result.details[remaining_model.ENTITY.name]
    assert all(
        call.args[0].operation is CrudOperation.READ_ALL
        for call in app.handle.call_args_list
    )
    assert all(call.args[0].limit == 1 for call in app.handle.call_args_list)
    assert all(call.args[0].return_id for call in app.handle.call_args_list)


def test_delete_all_ref_data_deletes_casedb_policy_models_before_references() -> None:
    """Delete casedb policy rows before their CaseTypeSet and ColSet references."""
    from gen_epix.casedb.domain import DOMAIN, command, model

    app = Mock()
    app.domain = DOMAIN
    app.handle.return_value = []
    service = object.__new__(SystemService)
    service._app = app

    result = service.delete_all_ref_data(command.DeleteAllRefDataCommand(user=None))

    assert result.success
    delete_commands = [
        call.args[0]
        for call in app.handle.call_args_list
        if call.args[0].operation is CrudOperation.DELETE_ALL
    ]
    deleted_models = [crud_command.MODEL_CLASS for crud_command in delete_commands]
    policy_models = {
        model.OrganizationAccessCasePolicy,
        model.OrganizationShareCasePolicy,
        model.UserAccessCasePolicy,
        model.UserShareCasePolicy,
    }
    assert policy_models <= set(deleted_models)
    assert max(deleted_models.index(policy) for policy in policy_models) < min(
        deleted_models.index(model.CaseTypeSet), deleted_models.index(model.ColSet)
    )


def test_delete_all_ref_data_reports_missing_crud_command() -> None:
    """Report a missing CRUD mapping instead of silently leaving data behind."""
    from gen_epix.casedb.domain import DOMAIN, command

    app = Mock()
    app.domain = DOMAIN
    app.handle.return_value = []
    missing_model = command.DeleteAllRefDataCommand.SORTED_REF_DATA_MODEL_CLASSES[0]
    original_get_crud_command = DOMAIN.get_crud_command_for_model

    def get_crud_command(model_class):
        if model_class is missing_model:
            raise LookupError("missing CRUD command")
        return original_get_crud_command(model_class)

    service = object.__new__(SystemService)
    service._app = app

    with patch.object(
        DOMAIN, "get_crud_command_for_model", side_effect=get_crud_command
    ):
        result = service.delete_all_ref_data(command.DeleteAllRefDataCommand(user=None))

    assert result.success is False
    assert (
        result.details[missing_model.ENTITY.name] == "LookupError: missing CRUD command"
    )
