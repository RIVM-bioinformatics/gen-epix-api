from contextlib import nullcontext
from test.util.mock_compat import MagicMock, patch
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, exc, model
from gen_epix.casedb.services.case.create_case_set import (
    case_service_create_case_set,
)
from gen_epix.casedb.services.case.service import CaseService
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.service import BaseService


@pytest.fixture
def case_set_service() -> CaseService:
    service = object.__new__(CaseService)
    app = SimpleNamespace(pdp=SimpleNamespace(is_allowed=MagicMock(return_value=True)))
    repository = MagicMock()
    repository.uow.return_value = nullcontext()
    service._app = cast(Any, app)
    service._repository = cast(Any, repository)
    return service


@pytest.fixture
def case_set() -> model.CaseSet:
    return model.CaseSet(
        id=uuid4(),
        case_type_id=uuid4(),
        created_in_data_collection_id=uuid4(),
        name="Example case set",
        code="example-case-set",
        description="Example",
        case_set_category_id=uuid4(),
        case_set_status_id=uuid4(),
    )


def _create_command(
    case_set: model.CaseSet,
    data_collection_ids: set[UUID] | None = None,
    case_ids: set[UUID] | None = None,
    user: model.User | None = None,
) -> command.CreateCaseSetCommand:
    return command.CreateCaseSetCommand(
        case_set=case_set,
        data_collection_ids=data_collection_ids or set(),
        case_ids=case_ids,
        user=user,
    )


def test_create_case_set_persists_requested_links_and_propagates_policies(
    case_set_service: CaseService, case_set: model.CaseSet
) -> None:
    data_collection_ids = {uuid4(), uuid4()}
    case_ids = {uuid4(), uuid4()}
    user = model.User(
        email="user@example.test", roles={"user"}, organization_id=uuid4()
    )
    policy = object()
    cmd = _create_command(case_set, data_collection_ids, case_ids, user)
    cmd._policies.append(policy)

    with patch.object(
        BaseService, "crud", autospec=True, side_effect=[case_set, [], []]
    ) as crud:
        result = case_service_create_case_set(case_set_service, cmd)

    assert result is case_set
    assert case_set_service.repository.uow.call_count == 1
    create_cmd, link_cmd, member_cmd = [call.args[1] for call in crud.call_args_list]
    assert isinstance(create_cmd, command.CaseSetCrudCommand)
    assert create_cmd.operation == CrudOperation.CREATE_ONE
    assert create_cmd.objs is case_set
    assert isinstance(link_cmd, command.CaseSetDataCollectionLinkCrudCommand)
    assert link_cmd.operation == CrudOperation.CREATE_SOME
    assert {link.data_collection_id for link in link_cmd.objs} == data_collection_ids
    assert {link.case_set_id for link in link_cmd.objs} == {case_set.id}
    assert isinstance(member_cmd, command.CaseSetMemberCrudCommand)
    assert member_cmd.operation == CrudOperation.CREATE_SOME
    assert {member.case_id for member in member_cmd.objs} == case_ids
    assert {member.case_set_id for member in member_cmd.objs} == {case_set.id}
    assert all(
        nested_cmd._policies == [policy] for nested_cmd in (link_cmd, member_cmd)
    )


def test_create_case_set_accepts_empty_associations(
    case_set_service: CaseService, case_set: model.CaseSet
) -> None:
    cmd = _create_command(case_set)

    with patch.object(
        BaseService, "crud", autospec=True, side_effect=[case_set, []]
    ) as crud:
        result = case_service_create_case_set(case_set_service, cmd)

    assert result is case_set
    assert crud.call_count == 2
    link_cmd = crud.call_args_list[1].args[1]
    assert isinstance(link_cmd, command.CaseSetDataCollectionLinkCrudCommand)
    assert link_cmd.objs == []


def test_create_case_set_denies_before_opening_unit_of_work(
    case_set_service: CaseService, case_set: model.CaseSet
) -> None:
    case_set_service.app.pdp.is_allowed.return_value = False
    cmd = _create_command(
        case_set,
        user=model.User(
            email="user@example.test", roles={"user"}, organization_id=uuid4()
        ),
    )

    with patch.object(BaseService, "crud", autospec=True) as crud:
        with pytest.raises(exc.UnauthorizedAuthError):
            case_service_create_case_set(case_set_service, cmd)

    assert case_set_service.repository.uow.call_count == 0
    crud.assert_not_called()
