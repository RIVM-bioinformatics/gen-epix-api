"""Test updating the creating data collection for existing cases."""

from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.services.case.update_case_created_in_data_collection import (
    case_service_update_case_created_in_data_collection,
)
from gen_epix.commondb.domain.enum import Role, RoleSet
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.exc import InvalidIdsError


def _case(created_in_data_collection_id):
    return model.Case(
        id=uuid4(),
        case_type_id=uuid4(),
        created_in_data_collection_id=created_in_data_collection_id,
        content={},
    )


@pytest.fixture
def service():
    user = model.User(
        id=uuid4(),
        key="admin@example.com",
        email="admin@example.com",
        roles={Role.APP_ADMIN.value},
        organization_id=uuid4(),
        is_active=True,
    )
    service = Mock()
    service.role_set_map = {RoleSet.GE_APP_ADMIN: frozenset({Role.APP_ADMIN.value})}
    service._get_user_and_repository.return_value = (user, service.repository)
    service.uow = Mock()
    service.uow.__enter__ = Mock(return_value=service.uow)
    service.uow.__exit__ = Mock(return_value=None)
    service.repository.uow.return_value = service.uow
    return service


def test_updates_all_cases_in_one_batch(service):
    old_data_collection_id = uuid4()
    new_data_collection_id = uuid4()
    cases = [_case(old_data_collection_id), _case(old_data_collection_id)]
    service.repository.crud.side_effect = [cases, cases]
    cmd = command.UpdateCaseCreatedInDataCollectionCommand(
        user=service._get_user_and_repository.return_value[0],
        case_ids=[case.id for case in cases],
        data_collection_id=new_data_collection_id,
    )

    result = case_service_update_case_created_in_data_collection(service, cmd)

    assert result == cases
    assert all(
        case.created_in_data_collection_id == new_data_collection_id for case in cases
    )
    assert service.repository.crud.call_args_list[0].kwargs == {
        "obj_ids": [case.id for case in cases]
    }
    assert service.repository.crud.call_args_list[0].args[2:] == (
        model.Case,
        CrudOperation.READ_SOME,
    )
    assert service.repository.crud.call_args_list[1].args[2:] == (
        model.Case,
        CrudOperation.UPDATE_SOME,
    )


def test_does_not_update_when_read_fails(service):
    service.repository.crud.side_effect = InvalidIdsError(
        "8b5592ee", "case not found", ids=[uuid4()]
    )
    cmd = command.UpdateCaseCreatedInDataCollectionCommand(
        user=service._get_user_and_repository.return_value[0],
        case_ids=[uuid4()],
        data_collection_id=uuid4(),
    )

    with pytest.raises(InvalidIdsError):
        case_service_update_case_created_in_data_collection(service, cmd)

    assert service.repository.crud.call_count == 1


def test_rejects_users_below_app_admin(service):
    user = service._get_user_and_repository.return_value[0]
    user.roles = {Role.ORG_USER.value}
    cmd = command.UpdateCaseCreatedInDataCollectionCommand(
        user=user,
        case_ids=[uuid4()],
        data_collection_id=uuid4(),
    )

    with pytest.raises(AssertionError):
        case_service_update_case_created_in_data_collection(service, cmd)

    service.repository.uow.assert_not_called()
