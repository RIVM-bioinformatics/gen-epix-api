"""Validate default FastApp model and policy contracts."""

import pytest

from gen_epix.fastapp.model import Command, Policy


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
