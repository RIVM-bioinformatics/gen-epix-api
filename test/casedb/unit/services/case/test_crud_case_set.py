from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import exc as case_exc
from gen_epix.casedb.domain import model as case_model
from gen_epix.casedb.domain.enum import CaseRight
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_case_set import \
    case_service_crud_case_set
from gen_epix.commondb.domain.enum import Role
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class BaseCrudCaseSetTestCase(TestCase):
    """Base test case with common fixtures and utilities for CaseSet CRUD."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Test user
        self.user: User = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.ORG_USER.value},
            organization_id=uuid4(),
            is_active=True,
        )

        # Service mock
        self.service: BaseCaseService = Mock(spec=BaseCaseService)
        self.service.crud = Mock()
        self.service._retrieve_case_sets_with_content_right = Mock()
        self.service._retrieve_case_set_data_collections_map = Mock()

        # Repository + UOW mocks
        self.service.repository = Mock()
        self.uow: BaseUnitOfWork = Mock(spec=BaseUnitOfWork)
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.service.repository.uow.return_value = self.uow
        self.service.repository.crud = Mock()

    def create_command(
        self,
        operation: CrudOperation,
        user: User | None = None,
        ids: list[UUID] | None = None,
        query_filter: object | None = None,
        set_user_none: bool = False,
    ) -> Mock:
        """Create a mocked CaseSetCrudCommand with essential attributes."""
        cmd: Mock = Mock()
        if set_user_none:
            cmd.user = None
        else:
            cmd.user = user if user is not None else self.user
        cmd.operation = operation
        cmd.query_filter = query_filter
        cmd.get_obj_ids = Mock(return_value=ids or [uuid4()])
        return cmd

    def create_case_sets(self, n: int = 2) -> list[Mock]:
        """Create mocked CaseSet objects with required attributes."""
        case_sets: list[Mock] = []
        for _ in range(n):
            cs: Mock = Mock(spec=case_model.CaseSet)
            cs.id = uuid4()
            cs.case_type_id = uuid4()
            cs.created_in_data_collection_id = uuid4()
            case_sets.append(cs)
        return case_sets

    def create_case_abac(self, allowed: bool = True) -> Mock:
        """Create a mocked ABAC object with configurable allowance."""
        case_abac: Mock = Mock()
        case_abac.is_allowed = Mock(return_value=allowed)
        return case_abac


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAdminPath(BaseCrudCaseSetTestCase):
    """Tests for admin-level operations (no ABAC)."""

    def test_admin_user_calls_crud_and_returns_value(self) -> None:
        # 1. Input
        cmd: Mock = self.create_command(operation=CrudOperation.READ_SOME)

        # 2. Mocks
        expected_result: list[int] = [1, 2]
        self.service.crud.return_value = expected_result  # type: ignore[attr-defined]
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ) as cascade_mock,
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=True),
            ) as is_admin_mock,
        ):
            # 3. Execute
            retval = case_service_crud_case_set(self.service, cmd)

            # 4. Verify
            assert retval == expected_result
            self.service.crud.assert_called_once_with(cmd)  # type: ignore[attr-defined]
            self.service.repository.uow.assert_called_once()  # type: ignore[attr-defined]
            cascade_mock.assert_called_once()
            # Ensure cascade received uow
            args, _ = cascade_mock.call_args
            assert args[0] is self.service and args[1] is self.uow and args[2] is cmd
            is_admin_mock.assert_called_once_with(self.service, cmd.user)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAbacNoPolicy(BaseCrudCaseSetTestCase):
    """Tests for ABAC path when no policy is present."""

    def test_no_policy_returns_crud_value(self) -> None:
        # 1. Input
        cmd: Mock = self.create_command(operation=CrudOperation.READ_SOME)

        # 2. Mocks
        expected_result: list[str] = ["a"]
        self.service.crud.return_value = expected_result  # type: ignore[attr-defined]
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ) as cascade_mock,
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=None),
            ),
        ):
            # 3. Execute
            retval = case_service_crud_case_set(self.service, cmd)

            # 4. Verify
            assert retval == expected_result
            self.service.crud.assert_called_once_with(cmd)  # type: ignore[attr-defined]
            cascade_mock.assert_called_once()


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAbacCreateOperation(BaseCrudCaseSetTestCase):
    """Tests for ABAC path with create operation raising error."""

    def test_create_operation_raises_assertion(self) -> None:
        # 1. Input
        cmd: Mock = self.create_command(operation=CrudOperation.CREATE_ONE)

        # 2. Mocks
        case_abac: Mock = self.create_case_abac(allowed=True)
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ) as cascade_mock,
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute & Verify
            with pytest.raises(AssertionError):
                case_service_crud_case_set(self.service, cmd)
            cascade_mock.assert_called_once()
            self.service.crud.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestReadOperations(BaseCrudCaseSetTestCase):
    """Tests for read operations with ABAC policy."""

    def test_read_one_with_abac_returns_first(self) -> None:
        # 1. Input
        ids: list[UUID] = [uuid4(), uuid4()]
        query_filter: dict[str, str] = {"k": "v"}
        cmd: Mock = self.create_command(
            operation=CrudOperation.READ_ONE, ids=ids, query_filter=query_filter
        )

        # 2. Mocks
        case_abac: Mock = self.create_case_abac(allowed=True)
        case_sets: list[int] = [10, 20]
        self.service._retrieve_case_sets_with_content_right.return_value = case_sets  # type: ignore[attr-defined]
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute
            retval = case_service_crud_case_set(self.service, cmd)

            # 4. Verify
            assert retval == case_sets[0]
            self.service._retrieve_case_sets_with_content_right.assert_called_once()  # type: ignore[attr-defined]
            args, kwargs = self.service._retrieve_case_sets_with_content_right.call_args  # type: ignore[attr-defined]
            assert args[0] is self.uow
            assert args[1] == cmd.user.id
            assert args[2] is case_abac
            assert args[3] == CaseRight.READ_CASE_SET
            assert kwargs.get("case_set_ids") == ids
            assert kwargs.get("filter") == query_filter

    def test_read_some_with_abac_returns_list(self) -> None:
        # 1. Input
        ids: list[UUID] = [uuid4(), uuid4()]
        query_filter: dict[str, str] = {"k": "v"}
        cmd: Mock = self.create_command(
            operation=CrudOperation.READ_SOME, ids=ids, query_filter=query_filter
        )

        # 2. Mocks
        case_abac: Mock = self.create_case_abac(allowed=True)
        case_sets: list[int] = [10, 20]
        self.service._retrieve_case_sets_with_content_right.return_value = case_sets  # type: ignore[attr-defined]
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute
            retval = case_service_crud_case_set(self.service, cmd)

            # 4. Verify
            assert retval == case_sets
            self.service._retrieve_case_sets_with_content_right.assert_called_once()  # type: ignore[attr-defined]
            args, kwargs = self.service._retrieve_case_sets_with_content_right.call_args  # type: ignore[attr-defined]
            assert args[0] is self.uow
            assert args[1] == cmd.user.id
            assert args[2] is case_abac
            assert args[3] == CaseRight.READ_CASE_SET
            assert kwargs.get("case_set_ids") == ids
            assert kwargs.get("filter") == query_filter


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestUpdateOperation(BaseCrudCaseSetTestCase):
    """Tests for update operation with ABAC policy."""

    def test_update_with_abac_calls_retrieve_and_crud(self) -> None:
        # 1. Input
        ids: list[UUID] = [uuid4()]
        cmd: Mock = self.create_command(operation=CrudOperation.UPDATE_SOME, ids=ids)

        # 2. Mocks
        case_abac: Mock = self.create_case_abac(allowed=True)
        self.service._retrieve_case_sets_with_content_right.return_value = (  # type: ignore[attr-defined]
            self.create_case_sets(1)
        )
        expected_result: str = "updated"
        self.service.crud.return_value = expected_result  # type: ignore[attr-defined]
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute
            retval = case_service_crud_case_set(self.service, cmd)

            # 4. Verify
            assert retval == expected_result
            self.service._retrieve_case_sets_with_content_right.assert_called_once()  # type: ignore[attr-defined]
            self.service.crud.assert_called_once_with(cmd)  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestDeleteAllOperation(BaseCrudCaseSetTestCase):
    """Tests for delete-all operation denial with ABAC policy."""

    def test_delete_all_raises_unauthorized(self) -> None:
        # 1. Input
        cmd: Mock = self.create_command(operation=CrudOperation.DELETE_ALL)

        # 2. Mocks
        case_abac: Mock = self.create_case_abac(allowed=True)
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute & Verify
            with pytest.raises(case_exc.UnauthorizedAuthError):
                case_service_crud_case_set(self.service, cmd)
            self.service.crud.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestDeleteSomeOperation(BaseCrudCaseSetTestCase):
    """Tests for delete-some operation with ABAC policy."""

    def test_delete_some_allowed_calls_crud(self) -> None:
        # 1. Input
        ids: list[UUID] = [uuid4(), uuid4()]
        cmd: Mock = self.create_command(operation=CrudOperation.DELETE_SOME, ids=ids)

        # 2. Mocks
        case_sets: list[Mock] = self.create_case_sets(2)
        self.service.repository.crud.return_value = case_sets  # type: ignore[attr-defined]
        dc_map: dict[UUID, set[UUID]] = {
            case_sets[0].id: {uuid4()},
            case_sets[1].id: {uuid4(), uuid4()},
        }
        self.service._retrieve_case_set_data_collections_map.return_value = dc_map  # type: ignore[attr-defined]
        case_abac: Mock = self.create_case_abac(allowed=True)
        expected_result: bool = True
        self.service.crud.return_value = expected_result  # type: ignore[attr-defined]
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute
            retval = case_service_crud_case_set(self.service, cmd)

            # 4. Verify
            assert retval is expected_result
            # repository read to get case sets
            self.service.repository.crud.assert_called_once()  # type: ignore[attr-defined]
            args, kwargs = self.service.repository.crud.call_args  # type: ignore[attr-defined]
            assert args[0] is self.uow
            assert args[1] == cmd.user.id
            assert args[2] is case_model.CaseSet
            assert args[3] is None
            assert (
                kwargs.get("obj_ids") == ids or args[4] == ids
            )  # support positional/keyword in mock
            assert args[-1] == CrudOperation.READ_SOME
            # data collections map retrieval
            self.service._retrieve_case_set_data_collections_map.assert_called_once()  # type: ignore[attr-defined]
            self.service.crud.assert_called_once_with(cmd)  # type: ignore[attr-defined]

    def test_delete_some_unauthorized_raises(self) -> None:
        # 1. Input
        ids: list[UUID] = [uuid4()]
        cmd: Mock = self.create_command(operation=CrudOperation.DELETE_SOME, ids=ids)

        # 2. Mocks
        case_sets: list[Mock] = self.create_case_sets(1)
        self.service.repository.crud.return_value = case_sets  # type: ignore[attr-defined]
        dc_map: dict[UUID, set[UUID]] = {case_sets[0].id: {uuid4()}}
        self.service._retrieve_case_set_data_collections_map.return_value = dc_map  # type: ignore[attr-defined]
        case_abac: Mock = self.create_case_abac(allowed=False)
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute & Verify
            with pytest.raises(case_exc.UnauthorizedAuthError):
                case_service_crud_case_set(self.service, cmd)
            self.service.crud.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestUserAssertions(BaseCrudCaseSetTestCase):
    """Tests for user-related assertion paths."""

    def test_user_none_raises_assertion(self) -> None:
        # 1. Input
        cmd: Mock = self.create_command(
            operation=CrudOperation.READ_SOME, set_user_none=True
        )

        # 2. Mocks
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=True),
            ),
        ):
            # 3. Execute & Verify
            with pytest.raises(AssertionError):
                case_service_crud_case_set(self.service, cmd)
            # UOW entered before assertion
            self.service.repository.uow.assert_called_once()  # type: ignore[attr-defined]
            self.uow.__enter__.assert_called_once()  # type: ignore[attr-defined]

    def test_user_id_none_raises_assertion(self) -> None:
        # 1. Input
        bad_user: User = User(
            id=None,
            key="bad@example.com",
            email="bad@example.com",
            roles={Role.ORG_USER.value},
            organization_id=uuid4(),
            is_active=True,
        )
        cmd: Mock = self.create_command(
            operation=CrudOperation.READ_SOME, user=bad_user
        )

        # 2. Mocks
        case_abac: Mock = self.create_case_abac(allowed=True)
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_set._crud_cascade_delete",
                new=Mock(),
            ) as cascade_mock,
            patch(
                "gen_epix.casedb.services.case.crud_case_set.is_app_admin_or_above",
                new=Mock(return_value=False),
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_set.get_case_abac_from_command",
                new=Mock(return_value=case_abac),
            ),
        ):
            # 3. Execute & Verify
            with pytest.raises(AssertionError):
                case_service_crud_case_set(self.service, cmd)
            cascade_mock.assert_called_once()
            self.service.crud.assert_not_called()  # type: ignore[attr-defined]
