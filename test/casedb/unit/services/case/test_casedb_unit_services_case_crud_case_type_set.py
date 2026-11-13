from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock, patch

import pytest

import gen_epix.casedb.services.case.crud_case_type_set as crud_case_type_set
from gen_epix.fastapp import CrudOperation


class TestCaseTypeSetCrud(BaseCrudTestCase):
    """Exercise case-type-set CRUD dispatch and access-filter helpers."""

    @pytest.mark.parametrize(
        "operation",
        [
            CrudOperation.CREATE_ONE,
            CrudOperation.READ_ALL,
            CrudOperation.UPDATE_ONE,
            CrudOperation.DELETE_ONE,
            CrudOperation.DELETE_ALL,
        ],
        ids=["create", "read", "update", "delete", "delete-all"],
    )
    def test_crud_cascades_and_returns_result(self, operation: CrudOperation) -> None:
        cmd = self.create_crud_command(operation)
        expected_result = object()
        self.service.crud.return_value = expected_result

        with patch(
            f"{crud_case_type_set.__name__}._crud_cascade_delete"
        ) as cascade_mock:
            retval = crud_case_type_set.case_service_crud_case_type_set(
                self.service, cmd
            )

        assert retval is expected_result
        self.service.repository.uow.assert_called_once_with()
        self.uow.__enter__.assert_called_once_with()
        self.uow.__exit__.assert_called_once_with(None, None, None)
        cascade_mock.assert_called_once_with(self.service, self.uow, cmd)
        self.service.crud.assert_called_once_with(cmd)

    def test_missing_user_raises_before_cascade_or_crud(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL, set_user_none=True)

        with (
            patch(
                f"{crud_case_type_set.__name__}._crud_cascade_delete"
            ) as cascade_mock,
            pytest.raises(AssertionError),
        ):
            crud_case_type_set.case_service_crud_case_type_set(self.service, cmd)

        cascade_mock.assert_not_called()
        self.service.crud.assert_not_called()

    def test_without_abac_delegates_crud(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_SOME)
        expected_result = object()
        self.service.crud.return_value = expected_result

        retval = crud_case_type_set._crud_case_type_set_without_abac(
            self.service, self.uow, cmd
        )

        assert retval is expected_result
        self.service.crud.assert_called_once_with(cmd)

    @pytest.mark.parametrize("has_access_metadata", [False, True])
    def test_unrestricted_abac_helper_delegates_crud(
        self, has_access_metadata: bool
    ) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        expected_result = object()
        self.service.crud.return_value = expected_result
        access = Mock(is_full_access=True) if has_access_metadata else None

        with patch(
            f"{crud_case_type_set.__name__}.get_ref_data_access_from_command",
            return_value=access,
        ):
            retval = crud_case_type_set._crud_case_type_set_with_abac(
                self.service, self.uow, cmd
            )

        assert retval is expected_result
        self.service.crud.assert_called_once_with(cmd)

    def test_restricted_read_uses_case_type_set_filter(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_SOME)
        access_filter = object()
        access = Mock(is_full_access=False)
        access.get_case_type_set_filter.return_value = access_filter
        expected_result = object()

        with (
            patch(
                f"{crud_case_type_set.__name__}.get_ref_data_access_from_command",
                return_value=access,
            ),
            patch(
                f"{crud_case_type_set.__name__}.crud_with_access_filter",
                return_value=expected_result,
            ) as crud_mock,
        ):
            retval = crud_case_type_set._crud_case_type_set_with_abac(
                self.service, self.uow, cmd
            )

        assert retval is expected_result
        access.get_case_type_set_filter.assert_called_once_with("id")
        crud_mock.assert_called_once_with(self.service, self.uow, cmd, access_filter)
        self.service.crud.assert_not_called()

    def test_restricted_write_raises_without_crud(self) -> None:
        cmd = self.create_crud_command(CrudOperation.UPDATE_ONE)
        access = Mock(is_full_access=False)

        with (
            patch(
                f"{crud_case_type_set.__name__}.get_ref_data_access_from_command",
                return_value=access,
            ),
            pytest.raises(AssertionError, match="Not a read operation"),
        ):
            crud_case_type_set._crud_case_type_set_with_abac(
                self.service, self.uow, cmd
            )

        access.get_case_type_set_filter.assert_not_called()
        self.service.crud.assert_not_called()
