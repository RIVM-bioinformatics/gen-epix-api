from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import exc, model
from gen_epix.casedb.services.case import crud_col
from gen_epix.fastapp import CrudOperation


class TestColCrud(BaseCrudTestCase):
    """Verify column relationship validation across authorization paths."""

    def _configure_write(
        self,
        operation: CrudOperation,
        *,
        case_type_matches: bool = True,
        ref_dim_matches: bool = True,
    ) -> tuple[Mock, Mock, Mock, Mock]:
        case_type_id = uuid4()
        ref_dim_id = uuid4()
        other_id = uuid4()
        dim = Mock(spec=model.Dim)
        dim.id = uuid4()
        dim.case_type_id = case_type_id if case_type_matches else other_id
        dim.ref_dim_id = ref_dim_id
        ref_col = Mock(spec=model.RefCol)
        ref_col.id = uuid4()
        ref_col.ref_dim_id = ref_dim_id if ref_dim_matches else other_id
        col = Mock(spec=model.Col)
        col.dim_id = dim.id
        col.ref_col_id = ref_col.id
        col.case_type_id = case_type_id
        cmd = self.create_crud_command(operation, objs=[col])
        cmd.is_write = Mock(return_value=True)
        self.service.repository.crud.side_effect = [[dim], [ref_col]]
        return cmd, col, dim, ref_col

    @pytest.mark.parametrize(
        ("case_type_matches", "ref_dim_matches", "message"),
        [
            pytest.param(
                False,
                True,
                "case_type_id must match case_type_id of Dim",
                id="case-type-mismatch",
            ),
            pytest.param(
                True,
                False,
                "ref_col.ref_dim_id must match ref_dim_id of Dim",
                id="reference-dimension-mismatch",
            ),
        ],
    )
    def test_non_exempt_write_rejects_invalid_relationships_before_crud(
        self,
        case_type_matches: bool,
        ref_dim_matches: bool,
        message: str,
    ) -> None:
        cmd, _, _, _ = self._configure_write(
            CrudOperation.CREATE_ONE,
            case_type_matches=case_type_matches,
            ref_dim_matches=ref_dim_matches,
        )
        self.service.app.pdp.get_col_id_filter.return_value = None

        with pytest.raises(exc.InvalidArgumentsError, match=message):
            crud_col._crud_col_with_abac(self.service, self.uow, cmd)

        self.service.crud.assert_not_called()

    def test_non_exempt_valid_write_validates_then_uses_access_filter(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cmd, _, _, _ = self._configure_write(CrudOperation.CREATE_ONE)
        access_filter = object()
        self.service.app.pdp.get_col_id_filter.return_value = access_filter
        expected_result = object()
        crud_with_filter = Mock(return_value=expected_result)
        monkeypatch.setattr(crud_col, "crud_with_access_filter", crud_with_filter)

        result = crud_col._crud_col_with_abac(self.service, self.uow, cmd)

        assert result is expected_result
        assert self.service.repository.crud.call_count == 2
        crud_with_filter.assert_called_once_with(
            self.service, self.uow, cmd, access_filter
        )
