import pytest

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command import system
from gen_epix.commondb.domain.command.base import Command, CrudCommand


@pytest.mark.parametrize(
    "command_class",
    [
        system.DeleteAllOperationalDataCommand,
        system.DeleteAllRefDataCommand,
        system.RetrieveOutagesCommand,
        system.RetrieveLicensesCommand,
        system.RetrieveFeatureFlagsCommand,
    ],
    ids=[
        "delete-operational-data",
        "delete-reference-data",
        "retrieve-outages",
        "retrieve-licenses",
        "retrieve-feature-flags",
    ],
)
def test_system_command_uses_shared_command_base(
    command_class: type[Command],
) -> None:
    command = command_class()

    assert isinstance(command, Command)
    assert command.user is None


def test_delete_all_commands_defer_model_selection_to_application() -> None:
    assert (
        system.DeleteAllOperationalDataCommand.SORTED_OPERATIONAL_DATA_MODEL_CLASSES
        == []
    )
    assert system.DeleteAllRefDataCommand.SORTED_REF_DATA_MODEL_CLASSES == []


def test_outage_crud_command_targets_outage_model() -> None:
    assert issubclass(system.OutageCrudCommand, CrudCommand)
    assert system.OutageCrudCommand.MODEL_CLASS is model.Outage
