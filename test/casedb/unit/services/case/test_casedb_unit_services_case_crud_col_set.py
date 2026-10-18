from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock, patch

import gen_epix.casedb.services.case.crud_col_set as crud_col_set
from gen_epix.fastapp import CrudOperation


class TestColSetCrud(BaseCrudTestCase):
    """Test access-controlled CRUD dispatch for column sets."""

    def test_exempt_command_uses_unfiltered_crud_and_cascades(self) -> None:
        cmd = self.create_crud_command(CrudOperation.DELETE_ONE)
        expected_result = object()
        self.service.crud.return_value = expected_result
        self.service.app.pdp.is_exempted.return_value = True

        with patch(f"{crud_col_set.__name__}._crud_cascade_delete") as cascade_mock:
            result = crud_col_set.case_service_crud_col_set(self.service, cmd)

        assert result is expected_result
        self.service.app.pdp.is_exempted.assert_called_once_with(cmd)
        cascade_mock.assert_called_once_with(self.service, self.uow, cmd)
        self.service.crud.assert_called_once_with(cmd)
        self.service.app.pdp.get_col_set_id_filter.assert_not_called()

    def test_constrained_command_uses_col_set_filter_without_cascading(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        cmd.access_filter = None
        expected_result = object()
        access_filter = object()
        observed_filters: list[object | None] = []
        self.service.app.pdp.is_exempted.return_value = False
        self.service.app.pdp.get_col_set_id_filter.return_value = access_filter

        def crud_side_effect(received_command: Mock) -> object:
            observed_filters.append(received_command.access_filter)
            return expected_result

        self.service.crud.side_effect = crud_side_effect

        with patch(f"{crud_col_set.__name__}._crud_cascade_delete") as cascade_mock:
            result = crud_col_set.case_service_crud_col_set(self.service, cmd)

        assert result is expected_result
        assert observed_filters == [access_filter]
        assert cmd.access_filter is None
        self.service.app.pdp.is_exempted.assert_called_once_with(cmd)
        self.service.app.pdp.get_col_set_id_filter.assert_called_once_with(
            cmd, col_set_id_field_name="id"
        )
        cascade_mock.assert_not_called()
