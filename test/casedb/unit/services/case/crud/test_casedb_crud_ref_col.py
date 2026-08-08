"""Unit tests for RefCol CRUD service behavior and model state validation."""

from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import patch
from typing import ClassVar
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain import enum, exc, model
from gen_epix.casedb.services.case.crud_ref_col import case_service_crud_ref_col
from gen_epix.fastapp import CrudOperation


class BaseRefColTestCase(BaseCrudTestCase):
    ref_dim_id: ClassVar[UUID] = UUID("550e8400-e29b-41d4-a716-446655440001")
    other_ref_dim_id: ClassVar[UUID] = UUID("550e8400-e29b-41d4-a716-446655440002")
    ref_col_id: ClassVar[UUID] = UUID("550e8400-e29b-41d4-a716-446655440003")

    def create_ref_col(
        self,
        *,
        ref_dim_id: UUID | None = None,
        col_type: enum.ColType = enum.ColType.TEXT,
        **kwargs: object,
    ) -> model.RefCol:
        return model.RefCol(
            id=self.ref_col_id,
            ref_dim_id=ref_dim_id or self.ref_dim_id,
            code="test.code",
            col_type=col_type,
            **kwargs,
        )


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRefColReadAndDelete(BaseRefColTestCase):
    """Test read access handling and delete passthrough."""

    def test_read_without_policy_returns_crud_result(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        expected = [object()]
        self.service.crud.return_value = expected

        with patch(
            "gen_epix.casedb.services.case.crud_ref_col.get_ref_data_access_from_command",
            return_value=None,
        ):
            retval = case_service_crud_ref_col(self.service, cmd)

        assert retval == expected
        self.service.crud.assert_called_once_with(cmd)

    def test_read_with_restricted_policy_uses_access_filter(self) -> None:
        cmd = self.create_crud_command(CrudOperation.READ_ALL)
        expected = [object()]
        access_filter = object()
        ref_data_access = self.service.repository
        ref_data_access.is_full_access = False
        ref_data_access.get_ref_col_filter.return_value = access_filter

        with (
            patch(
                "gen_epix.casedb.services.case.crud_ref_col.get_ref_data_access_from_command",
                return_value=ref_data_access,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_ref_col.crud_with_access_filter",
                return_value=expected,
            ) as crud_with_filter,
        ):
            retval = case_service_crud_ref_col(self.service, cmd)

        assert retval == expected
        ref_data_access.get_ref_col_filter.assert_called_once_with("id")
        crud_with_filter.assert_called_once_with(
            self.service, self.uow, cmd, access_filter
        )

    def test_delete_returns_crud_result(self) -> None:
        cmd = self.create_crud_command(CrudOperation.DELETE_ONE)
        expected = True
        self.service.crud.return_value = expected

        retval = case_service_crud_ref_col(self.service, cmd)

        assert retval is expected
        self.service.crud.assert_called_once_with(cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRefColCreateAndUpdate(BaseRefColTestCase):
    """Test RefCol dimension/type consistency and immutable fields."""

    def test_create_with_matching_dimension_type_returns_crud_result(self) -> None:
        ref_col = self.create_ref_col(
            col_type=enum.ColType.GEO_REGION, region_set_id=uuid4()
        )
        ref_dim = model.RefDim(
            id=self.ref_dim_id,
            dim_type=enum.DimType.GEO,
            code="test",
            label="Test",
        )
        cmd = self.create_crud_command(CrudOperation.CREATE_ONE, objs=[ref_col])
        expected = [self.ref_col_id]
        self.service.crud.return_value = expected
        self.service.repository.crud.return_value = [ref_dim]

        retval = case_service_crud_ref_col(self.service, cmd)

        assert retval == expected
        self.service.crud.assert_called_once_with(cmd)
        self.service.repository.crud.assert_called_once()

    def test_create_with_mismatched_dimension_type_raises(self) -> None:
        ref_col = self.create_ref_col(
            col_type=enum.ColType.GEO_REGION, region_set_id=uuid4()
        )
        ref_dim = model.RefDim(
            id=self.ref_dim_id,
            dim_type=enum.DimType.TEXT,
            code="test",
            label="Test",
        )
        cmd = self.create_crud_command(CrudOperation.CREATE_ONE, objs=[ref_col])
        self.service.repository.crud.return_value = [ref_dim]

        with (
            patch(
                "gen_epix.casedb.services.case.crud_ref_col.get_ref_data_access_from_command",
                return_value=None,
            ),
            pytest.raises(exc.InvalidArgumentsError),
        ):
            case_service_crud_ref_col(self.service, cmd)

        self.service.crud.assert_not_called()

    @pytest.mark.parametrize("field", ["ref_dim_id", "col_type"])
    def test_update_immutable_field_raises(self, field: str) -> None:
        updated = self.create_ref_col(
            ref_dim_id=(
                self.other_ref_dim_id if field == "ref_dim_id" else self.ref_dim_id
            ),
            col_type=(
                enum.ColType.TEXT if field == "ref_dim_id" else enum.ColType.OTHER
            ),
        )
        stored = self.create_ref_col(
            ref_dim_id=self.ref_dim_id,
            col_type=enum.ColType.TEXT,
        )
        cmd = self.create_crud_command(CrudOperation.UPDATE_ONE, objs=[updated])
        self.service.repository.crud.return_value = [stored]

        with pytest.raises(exc.InvalidArgumentsError):
            case_service_crud_ref_col(self.service, cmd)

        self.service.crud.assert_not_called()

    def test_exists_operation_returns_crud_result(self) -> None:
        cmd = self.create_crud_command(CrudOperation.EXISTS_ONE)
        expected = [True]
        self.service.crud.return_value = expected

        with patch(
            "gen_epix.casedb.services.case.crud_ref_col.get_ref_data_access_from_command",
            return_value=None,
        ):
            retval = case_service_crud_ref_col(self.service, cmd)

        assert retval == expected
        self.service.crud.assert_called_once_with(cmd)


class TestRefColStateValidation:
    """Test type-specific linked-resource and schema requirements."""

    ref_dim_id = UUID("550e8400-e29b-41d4-a716-446655440001")

    @pytest.mark.parametrize(
        ("col_type", "field"),
        [
            (enum.ColType.NOMINAL, "concept_set_id"),
            (enum.ColType.GEO_REGION, "region_set_id"),
            (enum.ColType.GENETIC_DISTANCE, "genetic_distance_protocol_id"),
        ],
    )
    def test_required_linked_id_is_enforced(
        self, col_type: enum.ColType, field: str
    ) -> None:
        with pytest.raises(exc.InvalidArgumentsError):
            model.RefCol(
                ref_dim_id=self.ref_dim_id,
                code="test.code",
                col_type=col_type,
            )

        valid = model.RefCol(
            ref_dim_id=self.ref_dim_id,
            code="test.code",
            col_type=col_type,
            **{field: uuid4()},
        )
        assert valid.col_type is col_type

    def test_regex_requires_regex_value(self) -> None:
        with pytest.raises(ValidationError, match="requires regex"):
            model.RefCol(
                ref_dim_id=self.ref_dim_id,
                code="test.code",
                col_type=enum.ColType.REGULAR_LANGUAGE,
            )

        valid = model.RefCol(
            ref_dim_id=self.ref_dim_id,
            code="test.code",
            col_type=enum.ColType.REGULAR_LANGUAGE,
            regex=r"^[A-Z]+$",
        )
        assert valid.regex == r"^[A-Z]+$"

    @pytest.mark.parametrize(
        "col_type",
        [
            enum.ColType.CONTEXT_FREE_GRAMMAR_JSON,
            enum.ColType.CONTEXT_FREE_GRAMMAR_XML,
        ],
    )
    def test_schema_type_requires_one_schema_source(
        self, col_type: enum.ColType
    ) -> None:
        with pytest.raises(ValidationError, match="requires schema"):
            model.RefCol(
                ref_dim_id=self.ref_dim_id,
                code="test.code",
                col_type=col_type,
            )

        with pytest.raises(ValidationError, match="Only one"):
            model.RefCol(
                ref_dim_id=self.ref_dim_id,
                code="test.code",
                col_type=col_type,
                schema_definition="schema",
                schema_uri="https://example.test/schema",
            )

        valid = model.RefCol(
            ref_dim_id=self.ref_dim_id,
            code="test.code",
            col_type=col_type,
            schema_uri="https://example.test/schema",
        )
        assert valid.schema_uri == "https://example.test/schema"
