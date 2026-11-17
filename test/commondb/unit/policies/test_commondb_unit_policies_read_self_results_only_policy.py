"""Test CommonDB and OMOP self-only read-policy behavior."""

from test.util.mock_compat import Mock
from typing import Any
from uuid import uuid4

import pytest

from gen_epix.commondb.domain import command as common_command
from gen_epix.commondb.domain.model import User
from gen_epix.commondb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.omopdb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy as OmopReadSelfResultsOnlyPolicy,
)


@pytest.mark.parametrize(
    "policy_class",
    [CommonReadSelfResultsOnlyPolicy, OmopReadSelfResultsOnlyPolicy],
)
@pytest.mark.parametrize(
    ("operation", "obj_ids", "retval"),
    [
        (CrudOperation.EXISTS_ONE, uuid4(), True),
        (CrudOperation.EXISTS_SOME, [uuid4(), uuid4()], [True, False]),
    ],
)
def test_exists_operations_are_unsupported(
    policy_class: type[CommonReadSelfResultsOnlyPolicy],
    operation: CrudOperation,
    obj_ids: Any,
    retval: Any,
) -> None:
    policy = policy_class(Mock())
    cmd = common_command.UserCrudCommand(
        user=User(id=uuid4(), roles={"test-role"}, organization_id=uuid4()),
        operation=operation,
        obj_ids=obj_ids,
    )

    with pytest.raises(
        NotImplementedError, match="Exists operations are not supported"
    ):
        policy.filter(cmd, retval)
