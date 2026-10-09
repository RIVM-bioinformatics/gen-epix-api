"""Unit tests for genetic-distance protocol CRUD service behavior."""

from test.casedb.unit.services.case.base import BaseCrudTestCase

import pytest

from gen_epix.casedb.services.case.crud_genetic_distance_protocol import (
    case_service_crud_genetic_distance_protocol,
)
from gen_epix.fastapp import CrudOperation


class TestGeneticDistanceProtocolCrud(BaseCrudTestCase):
    """Verify genetic-distance protocol CRUD delegates without modification."""

    @pytest.mark.parametrize("expected_result", [None, object()], ids=["none", "value"])
    def test_crud_delegates_command_and_returns_result(
        self, expected_result: object | None
    ) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        self.service.crud.return_value = expected_result

        retval = case_service_crud_genetic_distance_protocol(self.service, cmd)

        assert retval is expected_result
        self.service.crud.assert_called_once_with(cmd)

    def test_crud_propagates_exception(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        expected_error = RuntimeError("CRUD failed")
        self.service.crud.side_effect = expected_error

        with pytest.raises(RuntimeError) as error:
            case_service_crud_genetic_distance_protocol(self.service, cmd)

        assert error.value is expected_error
        self.service.crud.assert_called_once_with(cmd)
