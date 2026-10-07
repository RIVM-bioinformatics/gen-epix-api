"""Test shared system service operations."""

import json
from importlib import import_module
from test.util.mock_compat import Mock, patch

import pytest

from gen_epix.commondb.services.system import SystemService
from gen_epix.fastapp import CrudOperation


@pytest.mark.parametrize("app_name", ["casedb", "seqdb", "omopdb"])
def test_delete_all_operational_data_dispatches_each_model_in_order(
    app_name: str,
) -> None:
    """Delete every declared operational model and report individual failures."""
    domain_module = import_module(f"gen_epix.{app_name}.domain")
    command_module = import_module(f"gen_epix.{app_name}.domain.command")
    command_class = command_module.DeleteAllOperationalDataCommand
    app = Mock()
    app.domain = domain_module.DOMAIN
    failed_model = command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES[1]
    deleted_ids = ["deleted-id-1", "deleted-id-2"]

    def handle(crud_command):
        if crud_command.MODEL_CLASS is failed_model:
            raise RuntimeError("delete failed")
        return deleted_ids

    app.handle.side_effect = handle
    service = object.__new__(SystemService)
    service._app = app

    result = service.delete_all_operational_data(command_class(user=None))

    expected_models = command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES
    dispatched_commands = [call.args[0] for call in app.handle.call_args_list]
    assert [
        crud_command.MODEL_CLASS for crud_command in dispatched_commands
    ] == expected_models
    assert all(
        crud_command.operation == CrudOperation.DELETE_ALL
        for crud_command in dispatched_commands
    )
    assert result.success is False
    assert result.details == {
        model_class.ENTITY.name: (
            "RuntimeError: delete failed"
            if model_class is failed_model
            else json.dumps(deleted_ids)
        )
        for model_class in expected_models
    }


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
