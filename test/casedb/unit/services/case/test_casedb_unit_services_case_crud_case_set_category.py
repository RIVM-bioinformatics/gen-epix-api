from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import patch

import pytest

import gen_epix.casedb.services.case.crud_case_set_category as crud_case_set_category
from gen_epix.fastapp import CrudOperation


class TestCaseSetCategoryCrud(BaseCrudTestCase):
    """Test CRUD delegation for case-set categories."""

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
            f"{crud_case_set_category.__name__}._crud_cascade_delete"
        ) as cascade_mock:
            retval = crud_case_set_category.case_service_crud_case_set_category(
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
                f"{crud_case_set_category.__name__}._crud_cascade_delete",
                side_effect=error,
            ) as cascade_mock,
            pytest.raises(RuntimeError, match="cascade failed") as exc_info,
        ):
            crud_case_set_category.case_service_crud_case_set_category(
                self.service, cmd
            )

        assert exc_info.value is error
        cascade_mock.assert_called_once_with(self.service, self.uow, cmd)
        self.service.crud.assert_not_called()
