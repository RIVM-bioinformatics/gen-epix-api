"""Test shared system service operations."""

import json
from importlib import import_module
from test.util.mock_compat import Mock

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
