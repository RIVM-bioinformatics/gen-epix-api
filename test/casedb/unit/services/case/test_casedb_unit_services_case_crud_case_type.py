from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock
from uuid import UUID, uuid4

import pytest

import gen_epix.casedb.services.case.crud_case_type as crud_case_type
from gen_epix.casedb.domain import exc
from gen_epix.fastapp import CrudOperation


class TestCaseTypeCrud(BaseCrudTestCase):
    """Verify CaseType deletes preserve link constraints on both CRUD routes."""

    def _configure_delete(
        self, operation: CrudOperation, ids: list[UUID]
    ) -> tuple[Mock, Mock]:
        cmd = self.create_crud_command(operation, ids=ids)
        access_filter = Mock()
        self.service.app.pdp.get_case_type_id_filter.return_value = access_filter
        return cmd, access_filter

    @pytest.mark.parametrize(
        "operation",
        [CrudOperation.DELETE_ALL, CrudOperation.DELETE_SOME, CrudOperation.DELETE_ONE],
    )
    def test_abac_route_propagates_link_constraint_violation(
        self, operation: CrudOperation
    ) -> None:
        cmd, access_filter = self._configure_delete(operation, [uuid4()])
        cmd.access_filter = None
        link_violation = exc.LinkConstraintViolationError(
            "test", "CaseType is still linked", [uuid4()], [uuid4()]
        )
        self.service.crud.side_effect = link_violation

        with pytest.raises(exc.LinkConstraintViolationError) as raised:
            crud_case_type.case_service_crud_case_type(self.service, cmd)

        assert raised.value is link_violation
        self.service.crud.assert_called_once_with(cmd)
        assert cmd.access_filter is access_filter

    @pytest.mark.parametrize(
        "operation",
        [CrudOperation.DELETE_ALL, CrudOperation.DELETE_SOME, CrudOperation.DELETE_ONE],
    )
    def test_non_abac_route_propagates_link_constraint_violation(
        self, operation: CrudOperation
    ) -> None:
        cmd = self.create_crud_command(operation)
        self.service.app.pdp.is_exempted.return_value = True
        link_violation = exc.LinkConstraintViolationError(
            "test", "CaseType is still linked", [uuid4()], [uuid4()]
        )
        self.service.crud.side_effect = link_violation

        with pytest.raises(exc.LinkConstraintViolationError) as raised:
            crud_case_type.case_service_crud_case_type(self.service, cmd)

        assert raised.value is link_violation
        self.service.crud.assert_called_once_with(cmd)

    @pytest.mark.parametrize(
        "operation",
        [CrudOperation.DELETE_ALL, CrudOperation.DELETE_SOME, CrudOperation.DELETE_ONE],
    )
    def test_abac_delete_delegates_original_command_with_access_filter(
        self, monkeypatch, operation: CrudOperation
    ) -> None:
        cmd, access_filter = self._configure_delete(operation, [uuid4()])
        result = object()
        filtered_crud = Mock(return_value=result)
        monkeypatch.setattr(crud_case_type, "crud_with_access_filter", filtered_crud)

        assert (
            crud_case_type._crud_case_type_with_abac(self.service, self.uow, cmd)
            is result
        )
        filtered_crud.assert_called_once_with(
            self.service, self.uow, cmd, access_filter
        )

    def test_non_exempt_dispatches_to_abac_handler(self, monkeypatch) -> None:
        cmd = self.create_crud_command(CrudOperation.DELETE_ONE)
        self.service._RETRIEVE_COMPLETE_CASE_TYPE_CACHE = Mock()
        expected_result = object()
        abac_handler = Mock(return_value=expected_result)
        monkeypatch.setattr(crud_case_type, "_crud_case_type_with_abac", abac_handler)

        result = crud_case_type.case_service_crud_case_type(self.service, cmd)

        assert result is expected_result
        abac_handler.assert_called_once_with(self.service, self.uow, cmd)
