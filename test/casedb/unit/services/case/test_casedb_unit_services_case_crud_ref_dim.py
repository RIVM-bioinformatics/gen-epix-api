"""Unit tests for reference-dimension CRUD service behavior."""

from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import patch
from uuid import UUID

import pytest

from gen_epix.casedb.domain import enum, exc, model
from gen_epix.casedb.services.case.crud_ref_dim import case_service_crud_ref_dim
from gen_epix.fastapp import CrudOperation


class BaseRefDimTestCase(BaseCrudTestCase):
    """Provide reference-dimension and reference-column fixtures."""

    ref_dim_id = UUID("550e8400-e29b-41d4-a716-446655440001")

    def create_ref_dim(self, dim_type: enum.DimType) -> model.RefDim:
        """Create a reference dimension with a stable identifier."""
        return model.RefDim(
            id=self.ref_dim_id,
            dim_type=dim_type,
            code="test.dimension",
            label="Test dimension",
        )

    def create_ref_col(self) -> model.RefCol:
        """Create a temporal reference column dependent on the test dimension."""
        return model.RefCol(
            ref_dim_id=self.ref_dim_id,
            code="test.column",
            col_type=enum.ColType.TIME_DAY,
        )


class TestRefDimReadAndWrite(BaseRefDimTestCase):
    """Test reference-dimension access filtering and write behavior."""

    def test_read_exempt_user_returns_crud_result(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        expected = [self.create_ref_dim(enum.DimType.TIME)]
        self.service.crud.return_value = expected
        self.service.app.pdp.is_exempted.return_value = True

        retval = case_service_crud_ref_dim(self.service, cmd)

        assert retval == expected
        self.service.crud.assert_called_once_with(cmd)
        self.service.app.pdp.get_ref_dim_id_filter.assert_not_called()

    def test_read_restricted_user_applies_pdp_filter(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        expected = [self.create_ref_dim(enum.DimType.TIME)]
        access_filter = object()
        self.service.app.pdp.get_ref_dim_id_filter.return_value = access_filter

        with patch(
            "gen_epix.casedb.services.case.crud_ref_dim.crud_with_access_filter",
            return_value=expected,
        ) as crud_with_filter:
            retval = case_service_crud_ref_dim(self.service, cmd)

        assert retval == expected
        self.service.app.pdp.get_ref_dim_id_filter.assert_called_once_with(
            cmd, ref_dim_id_field_name="id"
        )
        crud_with_filter.assert_called_once_with(
            self.service, self.uow, cmd, access_filter
        )

    @pytest.mark.parametrize(
        "operation",
        [CrudOperation.CREATE_ONE, CrudOperation.DELETE_ONE],
        ids=["create", "delete"],
    )
    def test_create_and_delete_return_crud_result(
        self, operation: CrudOperation
    ) -> None:
        cmd = self.create_crud_command(
            operation,
            objs=[self.create_ref_dim(enum.DimType.TIME)],
        )
        expected = self.ref_dim_id
        self.service.crud.return_value = expected

        retval = case_service_crud_ref_dim(self.service, cmd)

        assert retval == expected
        self.service.crud.assert_called_once_with(cmd)
        self.service.repository.crud.assert_not_called()

    def test_update_with_compatible_dependent_columns_returns_crud_result(self) -> None:
        ref_dim = self.create_ref_dim(enum.DimType.TIME)
        cmd = self.create_crud_command(CrudOperation.UPDATE_ONE, objs=[ref_dim])
        self.service.repository.crud.return_value = [self.create_ref_col()]
        self.service.crud.return_value = ref_dim

        retval = case_service_crud_ref_dim(self.service, cmd)

        assert retval is ref_dim
        self.service.crud.assert_called_once_with(cmd)

    def test_update_with_incompatible_dependent_column_raises(self) -> None:
        ref_dim = self.create_ref_dim(enum.DimType.TEXT)
        cmd = self.create_crud_command(CrudOperation.UPDATE_ONE, objs=[ref_dim])
        self.service.repository.crud.return_value = [self.create_ref_col()]

        with pytest.raises(
            exc.InvalidArgumentsError,
            match="dim_type must correspond to dependentRefCols.col_type",
        ):
            case_service_crud_ref_dim(self.service, cmd)

        self.service.crud.assert_not_called()
