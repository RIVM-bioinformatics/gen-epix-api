from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import patch

import pytest

import gen_epix.casedb.services.case.crud_col_set_member as crud_col_set_member
from gen_epix.fastapp import CrudOperation


class TestColSetMemberCrud(BaseCrudTestCase):
    """Test CRUD delegation for column-set members."""

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
    def test_crud_calls_cascade_and_returns_result(
        self, operation: CrudOperation
    ) -> None:
        cmd = self.create_crud_command(operation)
        expected_result = object()
        self.service.crud.return_value = expected_result

        with patch(
            f"{crud_col_set_member.__name__}._crud_cascade_delete"
        ) as cascade_mock:
            retval = crud_col_set_member.case_service_crud_col_set_member(
                self.service, cmd
            )

        assert retval is expected_result
        self.service.repository.uow.assert_called_once_with()
        self.uow.__enter__.assert_called_once_with()
        self.uow.__exit__.assert_called_once_with(None, None, None)
        cascade_mock.assert_called_once_with(self.service, self.uow, cmd)
        self.service.crud.assert_called_once_with(cmd)

    def test_cascade_failure_propagates_without_crud(self) -> None:
        cmd = self.create_crud_command(CrudOperation.DELETE_ONE)
        error = RuntimeError("cascade failed")

        with (
            patch(
                f"{crud_col_set_member.__name__}._crud_cascade_delete",
                side_effect=error,
            ) as cascade_mock,
            pytest.raises(RuntimeError, match="cascade failed") as exc_info,
        ):
            crud_col_set_member.case_service_crud_col_set_member(self.service, cmd)

        assert exc_info.value is error
        cascade_mock.assert_called_once_with(self.service, self.uow, cmd)
        self.service.crud.assert_not_called()

    def test_without_abac_delegates_to_crud(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        expected_result = object()
        self.service.crud.return_value = expected_result

        retval = crud_col_set_member._crud_col_set_member_without_abac(
            self.service, self.uow, cmd
        )

        assert retval is expected_result
        self.service.crud.assert_called_once_with(cmd)

    def test_with_abac_passes_col_set_filter_to_crud_helper(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        access_filter = self.service.app.pdp.get_col_set_id_filter.return_value
        expected_result = object()

        with patch(
            f"{crud_col_set_member.__name__}.crud_with_access_filter",
            return_value=expected_result,
        ) as crud_mock:
            retval = crud_col_set_member._crud_col_set_member_with_abac(
                self.service, self.uow, cmd
            )

        assert retval is expected_result
        self.service.app.pdp.get_col_set_id_filter.assert_called_once_with(
            cmd, col_set_id_field_name="col_set_id"
        )
        crud_mock.assert_called_once_with(self.service, self.uow, cmd, access_filter)

    def test_with_abac_rejects_non_read_operation(self) -> None:
        cmd = self.create_crud_command(CrudOperation.CREATE_ONE)

        with pytest.raises(AssertionError, match="Not a read operation"):
            crud_col_set_member._crud_col_set_member_with_abac(
                self.service, self.uow, cmd
            )

        self.service.app.pdp.get_col_set_id_filter.assert_not_called()
