"""Validate the Casedb ABAC case policy CRUD commands."""

import pytest

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.command import abac
from gen_epix.commondb.domain.command import CrudCommand
from gen_epix.fastapp.enum import CrudOperation

COMMAND_MODEL_PAIRS = [
    pytest.param(
        abac.OrganizationAccessCasePolicyCrudCommand,
        model.OrganizationAccessCasePolicy,
        id="organization_access",
    ),
    pytest.param(
        abac.UserAccessCasePolicyCrudCommand,
        model.UserAccessCasePolicy,
        id="user_access",
    ),
    pytest.param(
        abac.OrganizationShareCasePolicyCrudCommand,
        model.OrganizationShareCasePolicy,
        id="organization_share",
    ),
    pytest.param(
        abac.UserShareCasePolicyCrudCommand,
        model.UserShareCasePolicy,
        id="user_share",
    ),
]


@pytest.mark.parametrize("command_class, model_class", COMMAND_MODEL_PAIRS)
def test_command_is_crud_command_for_its_policy_model(
    command_class: type[CrudCommand], model_class: type
) -> None:
    """Each command extends CrudCommand and binds its policy model."""
    assert issubclass(command_class, CrudCommand)
    assert command_class.MODEL_CLASS is model_class


def test_commands_map_to_distinct_models() -> None:
    """Each command targets a different policy model."""
    model_classes = [pair.values[1] for pair in COMMAND_MODEL_PAIRS]
    assert len(set(model_classes)) == len(COMMAND_MODEL_PAIRS)


@pytest.mark.parametrize("command_class, model_class", COMMAND_MODEL_PAIRS)
def test_command_instantiates_with_defaults(
    command_class: type[CrudCommand], model_class: type
) -> None:
    """Only the operation is required; user and object IDs default to None."""
    command = command_class(operation=CrudOperation.READ_ALL)
    assert command.MODEL_CLASS is model_class
    assert command.user is None
    assert command.obj_ids is None
