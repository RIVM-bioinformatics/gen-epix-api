"""Validate default FastApp model and policy contracts."""

import pytest

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Command, CrudCommand, Policy


@pytest.mark.parametrize(
    "method_name", ["is_allowed", "get_content", "get_content_return_type", "filter"]
)
def test_unimplemented_policy_methods_share_error_contract(method_name: str) -> None:
    """Require unimplemented policy hooks to raise the documented exception."""
    policy = Policy()
    command = Command()
    method = getattr(policy, method_name)
    args = (command, None) if method_name == "filter" else (command,)

    with pytest.raises(
        NotImplementedError, match="^Method is not implemented for this policy$"
    ):
        method(*args)


@pytest.mark.parametrize(
    "operation, kwargs, is_valid",
    [
        (CrudOperation.DELETE_ALL, {"return_count": True}, True),
        (CrudOperation.DELETE_ALL, {"return_count": True, "limit": 10}, True),
        (CrudOperation.DELETE_ALL, {"return_id": True, "limit": 10}, True),
        (CrudOperation.DELETE_ALL, {"return_count": True, "return_id": True}, False),
        (CrudOperation.READ_ALL, {"return_count": True}, False),
        (CrudOperation.READ_ALL, {"limit": 10}, True),
        (CrudOperation.UNDELETE_ALL, {"limit": 10}, False),
    ],
)
def test_crud_command_validates_return_count_and_limit(
    operation: CrudOperation, kwargs: dict, is_valid: bool
) -> None:
    """Allow return_count only for delete all and limit for read and delete all."""
    if is_valid:
        assert CrudCommand(operation=operation, **kwargs).operation == operation
    else:
        with pytest.raises(ValueError):
            CrudCommand(operation=operation, **kwargs)
