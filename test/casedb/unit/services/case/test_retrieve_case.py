"""
Unit tests for casedb case retrieval services.

Tests follow the style and conventions of the commondb upload tests,
using typed variables, explicit mocking, and clear structure.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Callable
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_case import (
    case_service_retrieve_case_cohort_links_by_case_type,
    case_service_retrieve_cases_by_id,
    case_service_retrieve_cases_by_query,
)
from gen_epix.commondb.domain.enum import Role
from gen_epix.filter.composite import TypedCompositeFilter
from gen_epix.filter.enum import FilterType, LogicalOperator
from gen_epix.filter.exists import TypedExistsFilter
from gen_epix.filter.number_set import TypedNumberSetFilter
from gen_epix.filter.string_set import TypedStringSetFilter


class _FakeCaseAbacPolicy(BaseCaseAbacPolicy):
    """Lightweight policy to inject a case ABAC object into commands."""

    def __init__(self, abac: Any):
        super().__init__(abac_service=Mock(), abac=abac)
        self._abac = abac

    def get_content(self, cmd: Any) -> Any:  # noqa: ARG002
        return self._abac


class BaseRetrieveCaseTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        # Test user
        self.user: model.User = model.User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.APP_ADMIN.value},
            organization_id=uuid4(),
            is_active=True,
        )

        # Common IDs
        self.case_type_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440021")
        self.case_id1: UUID = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.case_id2: UUID = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.case_set_id1: UUID = UUID("550e8400-e29b-41d4-a716-446655440101")
        self.case_set_id2: UUID = UUID("550e8400-e29b-41d4-a716-446655440102")
        self.cohort_id1: UUID = UUID("550e8400-e29b-41d4-a716-446655440201")
        self.cohort_id2: UUID = UUID("550e8400-e29b-41d4-a716-446655440202")
        self.cohort_definition_id1: UUID = UUID("550e8400-e29b-41d4-a716-446655440301")
        self.cohort_definition_id2: UUID = UUID("550e8400-e29b-41d4-a716-446655440302")
        self.data_collection_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440501")

        # Service and repository mocks
        self.service: Any = Mock(spec=BaseCaseService)
        self.repository: Any = Mock()
        self.uow: Any = Mock()
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.repository.uow = Mock(return_value=self.uow)
        self.service.repository = self.repository
        self.service.app = Mock()
        self.service._get_user_and_repository = Mock(
            return_value=(self.user, self.repository)
        )

        # Default repository behaviors
        self.repository.crud.return_value = []
        self.repository.read_fields.return_value = []

        # Storage for unified repo side-effect
        self._repo_case_type: model.CaseType | None = None
        self._repo_cols: list[model.Col] | None = None
        self._repo_ref_cols: list[model.RefCol] | None = None

        # Default ABAC mock
        self.case_abac: Any = Mock()
        self.case_abac.is_full_access = True
        self.case_abac.get_combinations_with_access_right = Mock(
            return_value={self.case_type_id}
        )
        self.case_abac.get_cols_with_access_rights = Mock(return_value=set())

    # Helpers

    def create_case_type(self, read_max_n_cases: int = 100) -> model.CaseType:
        return model.CaseType(
            name="TEST",
            description=None,
            disease_id=None,
            etiological_agent_id=None,
            props=model.CaseTypeProps(read_max_n_cases=read_max_n_cases),
        )

    def create_case(
        self,
        case_id: UUID,
        content: dict[UUID, str | None],
        case_date: datetime | None = None,
    ) -> model.Case:
        return model.Case(
            id=case_id,
            code=None,
            case_type_id=self.case_type_id,
            created_in_data_collection_id=self.data_collection_id,
            count=None,
            case_date=case_date or datetime.now(timezone.utc),
            content=content,
        )

    def create_col(
        self,
        col_id: UUID,
        ref_col_id: UUID,
        col_type: enum.ColType,
        concept_set_id: UUID | None = None,
        region_set_id: UUID | None = None,
    ) -> tuple[model.Col, model.RefCol]:
        ref_dim_id: UUID = uuid4()
        ref_col: model.RefCol = model.RefCol(
            ref_dim_id=ref_dim_id,
            ref_dim=None,
            code_suffix=None,
            code=f"REF_DIM.{col_id.hex[:8]}",
            rank=0,
            label=None,
            col_type=col_type,
            concept_set_id=concept_set_id,
            concept_set=None,
            region_set_id=region_set_id,
            region_set=None,
            protocol_id=None,
            protocol=None,
            description=None,
            props={},
        )
        col: model.Col = model.Col(
            case_type_id=self.case_type_id,
            case_type=None,
            dim_id=uuid4(),
            dim=None,
            ref_col_id=ref_col_id,
            ref_col=ref_col,
            code=f"col.{col_id.hex[:8]}",
            rank=0,
            label=None,
            description=None,
            min_value=None,
            max_value=None,
            min_datetime=None,
            max_datetime=None,
            min_length=None,
            max_length=None,
            pattern=None,
            ncbi_taxid=None,
            genetic_sequence_col_id=None,
            tree_algorithm_codes=None,
            props={},
        )
        col.id = col_id
        ref_col.id = ref_col_id
        return col, ref_col

    def create_typed_string_set_filter(
        self, key: UUID, members: set[str]
    ) -> TypedStringSetFilter:
        return TypedStringSetFilter(
            type=FilterType.STRING_SET.value, key=str(key), members=frozenset(members)
        )

    def create_typed_number_set_filter(
        self, key: UUID, members: set[float]
    ) -> TypedNumberSetFilter:
        return TypedNumberSetFilter(
            type=FilterType.NUMBER_SET.value, key=str(key), members=frozenset(members)
        )

    # NoFilter not used due to composite key semantics

    def create_composite_filter(
        self,
        filters: list[Any],
        operator: LogicalOperator = LogicalOperator.AND,
    ) -> TypedCompositeFilter:
        return TypedCompositeFilter(
            type=FilterType.COMPOSITE.value,
            filters=filters,
            operator=operator,
        )

    def _install_repo_side_effect(self) -> None:
        def _crud_side_effect(
            _uow: Any,
            _user_id: UUID,
            cls: type[model.Model],
            _operation: Any,
            _filter: Any = None,
            _objs: Any = None,
            obj_ids: list[UUID] | None = None,
            **kwargs: Any,
        ) -> list[Any]:
            if cls is model.CaseType and obj_ids == [self.case_type_id]:
                return [self._repo_case_type] if self._repo_case_type else []
            if cls is model.Col:
                if not obj_ids or self._repo_cols is None:
                    return []
                # Preserve input order of ids to align filters → map functions
                return [next(x for x in self._repo_cols if x.id == i) for i in obj_ids]
            if cls is model.RefCol:
                if not obj_ids or self._repo_ref_cols is None:
                    return []
                # Preserve input order of ids to align filters → map functions
                return [
                    next(x for x in self._repo_ref_cols if x.id == i) for i in obj_ids
                ]
            return []

        self.repository.crud.side_effect = _crud_side_effect

    def set_repository_case_type(self, case_type: model.CaseType) -> None:
        self._repo_case_type = case_type
        self._install_repo_side_effect()

    def set_repository_cols_and_ref_cols(
        self, cols: list[model.Col], ref_cols: list[model.RefCol]
    ) -> None:
        self._repo_cols = cols
        self._repo_ref_cols = ref_cols
        self._install_repo_side_effect()

    def attach_abac_policy(self, cmd: command.Command, abac: Any | None = None) -> None:
        """Attach a fake ABAC policy to the command for retrieval."""
        cmd._policies = [
            _FakeCaseAbacPolicy(abac if abac is not None else self.case_abac)
        ]

    # Assertions

    def assertQueryResult(
        self,
        result: model.CaseQueryResult,
        expected_ids: list[UUID],
        is_limited: bool,
    ) -> None:
        assert result.case_ids == expected_ids
        assert result.is_max_results_exceeded == is_limited


# Tests for query-based retrieval
@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveCasesByQuery(BaseRetrieveCaseTestCase):
    """Tests covering branches of case_service_retrieve_cases_by_query."""

    def test_zero_case_set_ids_raises_not_implemented(self) -> None:
        # 1. Input
        cq: model.CaseQuery = model.CaseQuery(
            label=None,
            case_type_id=self.case_type_id,
            case_set_ids=set(),
            datetime_range_filter=None,
            filter=None,
        )
        cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
            user=self.user, case_query=cq
        )

        # 2. Mocks: none beyond defaults

        # 3. Execute
        with pytest.raises(NotImplementedError):
            case_service_retrieve_cases_by_query(self.service, cmd)

    def test_unauthorized_case_type_raises(self) -> None:
        # 1. Input
        cq: model.CaseQuery = model.CaseQuery(
            label=None,
            case_type_id=self.case_type_id,
            case_set_ids=None,
            datetime_range_filter=None,
            filter=None,
        )
        cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
            user=self.user, case_query=cq
        )

        # 2. Mocks
        case_abac: Any = Mock()
        case_abac.is_full_access = False
        case_abac.get_combinations_with_access_right = Mock(return_value=set())
        self.attach_abac_policy(cmd, case_abac)

        # 3. Execute
        with pytest.raises(exc.UnauthorizedAuthError):
            case_service_retrieve_cases_by_query(self.service, cmd)

    def test_case_sets_unauthorized_raises(self) -> None:
        # 1. Input
        cq: model.CaseQuery = model.CaseQuery(
            label=None,
            case_type_id=self.case_type_id,
            case_set_ids={self.case_set_id1, self.case_set_id2},
            datetime_range_filter=None,
            filter=None,
        )
        cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
            user=self.user, case_query=cq
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        # Only one authorized case set returned between READ and WRITE rights
        authorized_case_set: model.CaseSet = model.CaseSet(
            id=self.case_set_id1,
            case_type_id=self.case_type_id,
            case_type=None,
            created_in_data_collection_id=self.data_collection_id,
            created_in_data_collection=None,
            name="authorized",
            code="authorized",
            description="",
            case_set_date=datetime.now(timezone.utc),
            case_set_category_id=uuid4(),
            case_set_category=None,
            case_set_status_id=uuid4(),
            case_set_status=None,
        )
        self.service._retrieve_case_sets_with_content_right = Mock(
            side_effect=[[authorized_case_set], []]
        )

        # 3. Execute
        with pytest.raises(exc.UnauthorizedAuthError):
            case_service_retrieve_cases_by_query(self.service, cmd)

        # 4. Verify interactions
        assert self.service._retrieve_case_sets_with_content_right.call_count == 2

    def test_filter_invalid_members_raises(self) -> None:
        # 1. Input: one concept-backed column, invalid member
        col_id: UUID = uuid4()
        ref_col_id: UUID = uuid4()
        col, ref_col = self.create_col(
            col_id, ref_col_id, enum.ColType.NOMINAL, concept_set_id=uuid4()
        )
        invalid_member: str = "invalid_member"
        filter: TypedCompositeFilter = self.create_composite_filter(
            [self.create_typed_string_set_filter(col_id, {invalid_member})]
        )
        cq: model.CaseQuery = model.CaseQuery(
            label=None,
            case_type_id=self.case_type_id,
            case_set_ids=None,
            datetime_range_filter=None,
            filter=filter,
        )
        cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
            user=self.user, case_query=cq
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        self.set_repository_cols_and_ref_cols([col], [ref_col])
        # No concept IDs returned → invalid
        self.service.app.handle = Mock(return_value=[])
        # Provide minimal cases to reach filter validation
        self.service._retrieve_cases_with_content_right = Mock(return_value=[])

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError):
            case_service_retrieve_cases_by_query(self.service, cmd)

    def test_filter_invalid_type_raises(self) -> None:
        # 1. Input: concept-backed column, wrong filter type
        col_id: UUID = uuid4()
        ref_col_id: UUID = uuid4()
        col, ref_col = self.create_col(
            col_id, ref_col_id, enum.ColType.NOMINAL, concept_set_id=uuid4()
        )
        filter: TypedCompositeFilter = self.create_composite_filter(
            [self.create_typed_number_set_filter(col_id, {1.0})]
        )
        case_query: model.CaseQuery = model.CaseQuery(
            label=None,
            case_type_id=self.case_type_id,
            case_set_ids=None,
            datetime_range_filter=None,
            filter=filter,
        )
        cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
            user=self.user, case_query=case_query
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        self.set_repository_cols_and_ref_cols([col], [ref_col])
        self.service._retrieve_cases_with_content_right = Mock(return_value=[])

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError):
            case_service_retrieve_cases_by_query(self.service, cmd)

    def test_happy_path_with_filters_case_sets_and_max_limit(self) -> None:
        # 1. Input: multiple columns to exercise mapping, plus case sets
        time_col_id: UUID = uuid4()
        dec_col_id: UUID = uuid4()
        # geo_col_id intentionally omitted to avoid NoFilter key issues
        nom_col_id: UUID = uuid4()
        reg_col_id: UUID = uuid4()

        time_ref_col_id: UUID = uuid4()
        dec_ref_col_id: UUID = uuid4()
        # geo_ref_col_id intentionally omitted
        nom_ref_col_id: UUID = uuid4()
        reg_ref_col_id: UUID = uuid4()

        # Create cols & Cols
        time_col, time_ref_col = self.create_col(
            time_col_id, time_ref_col_id, enum.ColType.TIME_DAY
        )
        dec_col, dec_ref_col = self.create_col(
            dec_col_id, dec_ref_col_id, enum.ColType.DECIMAL_1
        )
        nom_col, nom_ref_col = self.create_col(
            nom_col_id, nom_ref_col_id, enum.ColType.NOMINAL, concept_set_id=uuid4()
        )
        reg_col, reg_ref_col = self.create_col(
            reg_col_id, reg_ref_col_id, enum.ColType.GEO_REGION, region_set_id=uuid4()
        )

        # Filters compatible with mapping
        from gen_epix.filter.date_range import TypedDateRangeFilter

        filters: list[Any] = [
            TypedDateRangeFilter(
                type=FilterType.DATE_RANGE.value,
                key=str(time_col_id),
                lower_bound=date(2024, 1, 1),
                upper_bound=date(2025, 1, 1),
            ),
            self.create_typed_number_set_filter(dec_col_id, {Decimal("5.1")}),  # type: ignore[arg-type]
            self.create_typed_string_set_filter(
                nom_col_id, {"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}
            ),
            self.create_typed_string_set_filter(
                reg_col_id, {"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"}
            ),
        ]
        filt: TypedCompositeFilter = self.create_composite_filter(filters)

        cq: model.CaseQuery = model.CaseQuery(
            label=None,
            case_type_id=self.case_type_id,
            case_set_ids={self.case_set_id1},
            datetime_range_filter=None,
            filter=filt,
        )
        cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
            user=self.user, case_query=cq
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        # Ensure case set authorization check passes
        authorized_case_set: model.CaseSet = model.CaseSet(
            id=self.case_set_id1,
            case_type_id=self.case_type_id,
            case_type=None,
            created_in_data_collection_id=self.data_collection_id,
            created_in_data_collection=None,
            name="authorized",
            code="authorized",
            description="",
            case_set_date=datetime.now(timezone.utc),
            case_set_category_id=uuid4(),
            case_set_category=None,
            case_set_status_id=uuid4(),
            case_set_status=None,
        )
        self.service._retrieve_case_sets_with_content_right = Mock(
            side_effect=lambda *args, **kwargs: [authorized_case_set]
        )
        # Repository data for filter verification
        self.set_repository_cols_and_ref_cols(
            [time_col, dec_col, nom_col, reg_col],
            [time_ref_col, dec_ref_col, nom_ref_col, reg_ref_col],
        )
        # Concepts & regions available
        concept_id_str: str = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        region_id_str: str = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        concept: Any = Mock()
        concept.id = UUID(concept_id_str)
        region: Any = Mock()
        region.id = UUID(region_id_str)
        # First call (ConceptCrudCommand) returns concepts, second (RegionCrudCommand) returns regions
        self.service.app.handle = Mock(side_effect=[[concept], [region]])

        # Cases to be returned (2 cases → max limit will truncate)
        case1_content: dict[UUID, str | None] = {
            time_col_id: "2024-01-01",
            dec_col_id: "5.1",
            nom_col_id: concept_id_str,
            reg_col_id: region_id_str,
        }
        case2_content: dict[UUID, str | None] = {
            time_col_id: "2024-02-02",
            dec_col_id: "5.1",
            nom_col_id: concept_id_str,
            reg_col_id: region_id_str,
        }
        cases: list[model.Case] = [
            self.create_case(self.case_id1, case1_content),
            self.create_case(self.case_id2, case2_content),
        ]
        self.service._retrieve_cases_with_content_right = Mock(return_value=cases)
        # Case sets mapping → both cases in requested set
        self.service._retrieve_case_case_sets_map = Mock(
            return_value={
                self.case_id1: {self.case_set_id1},
                self.case_id2: {self.case_set_id1},
            }
        )
        # CaseType limit = 1 (to trigger truncation)
        self.set_repository_case_type(self.create_case_type(read_max_n_cases=1))

        # 3. Execute
        result: model.CaseQueryResult = case_service_retrieve_cases_by_query(
            self.service, cmd
        )

        # 4. Verify results (truncated to first case)
        self.assertQueryResult(result, [self.case_id1], True)

    def test_happy_path_without_filters_or_case_sets(self) -> None:
        # 1. Input: simple query
        cq: model.CaseQuery = model.CaseQuery(
            label=None,
            case_type_id=self.case_type_id,
            case_set_ids=None,
            datetime_range_filter=None,
            filter=None,
        )
        cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
            user=self.user, case_query=cq
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        cases: list[model.Case] = [
            self.create_case(self.case_id1, {}),
            self.create_case(self.case_id2, {}),
        ]
        self.service._retrieve_cases_with_content_right = Mock(return_value=cases)
        self.set_repository_case_type(self.create_case_type(read_max_n_cases=10))

        # 3. Execute
        result: model.CaseQueryResult = case_service_retrieve_cases_by_query(
            self.service, cmd
        )

        # 4. Verify
        self.assertQueryResult(result, [self.case_id1, self.case_id2], False)


# Tests for ID-based retrieval
@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveCasesById(BaseRetrieveCaseTestCase):
    """Tests covering branches of case_service_retrieve_cases_by_id."""

    def test_empty_case_ids_returns_empty(self) -> None:
        # 1. Input
        cmd: command.RetrieveCasesByIdCommand = command.RetrieveCasesByIdCommand(
            user=self.user, case_type_id=self.case_type_id, case_ids=[]
        )

        # 2. Mocks: none beyond defaults

        # 3. Execute
        result: list[model.Case] = case_service_retrieve_cases_by_id(self.service, cmd)

        # 4. Verify
        assert result == []
        assert self.repository.uow.call_count == 0

    def test_no_cases_found_returns_empty(self) -> None:
        # 1. Input
        cmd: command.RetrieveCasesByIdCommand = command.RetrieveCasesByIdCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            case_ids=[self.case_id1],
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        self.service._retrieve_cases_with_content_right = Mock(return_value=[])

        # 3. Execute
        result: list[model.Case] = case_service_retrieve_cases_by_id(self.service, cmd)

        # 4. Verify
        assert result == []

    def test_invalid_case_type_raises(self) -> None:
        # 1. Input
        cmd: command.RetrieveCasesByIdCommand = command.RetrieveCasesByIdCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            case_ids=[self.case_id1],
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        self.service._retrieve_cases_with_content_right = Mock(
            return_value=[self.create_case(self.case_id1, {})]
        )
        # CaseType not found
        self.repository.crud.return_value = []

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError):
            case_service_retrieve_cases_by_id(self.service, cmd)

    def test_max_limit_truncates_cases(self) -> None:
        # 1. Input
        cmd: command.RetrieveCasesByIdCommand = command.RetrieveCasesByIdCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            case_ids=[self.case_id1, self.case_id2],
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        cases: list[model.Case] = [
            self.create_case(self.case_id1, {}),
            self.create_case(self.case_id2, {}),
        ]
        self.service._retrieve_cases_with_content_right = Mock(return_value=cases)
        self.set_repository_case_type(self.create_case_type(read_max_n_cases=1))

        # 3. Execute
        result: list[model.Case] = case_service_retrieve_cases_by_id(self.service, cmd)

        # 4. Verify
        assert [x.id for x in result] == [self.case_id1]

    def test_zero_read_max_falls_back_to_service_default(self) -> None:
        # When props.read_max_n_cases == 0 (unconfigured), the service's
        # _default_props.read_max_n_cases is used as the limit instead of 0.
        # 1. Input
        cmd: command.RetrieveCasesByIdCommand = command.RetrieveCasesByIdCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            case_ids=[self.case_id1, self.case_id2],
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        cases: list[model.Case] = [
            self.create_case(self.case_id1, {}),
            self.create_case(self.case_id2, {}),
        ]
        self.service._retrieve_cases_with_content_right = Mock(return_value=cases)
        # CaseType has 0 → service default of 1 should be applied
        self.set_repository_case_type(self.create_case_type(read_max_n_cases=0))
        self.service._default_props = model.CaseTypeProps(read_max_n_cases=1)

        # 3. Execute
        result: list[model.Case] = case_service_retrieve_cases_by_id(self.service, cmd)

        # 4. Verify: only 1 case returned, not 0 and not 2
        assert [x.id for x in result] == [self.case_id1]

    def test_happy_path_returns_cases(self) -> None:
        # 1. Input
        cmd: command.RetrieveCasesByIdCommand = command.RetrieveCasesByIdCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            case_ids=[self.case_id1],
        )

        # 2. Mocks
        self.attach_abac_policy(cmd)
        self.service._retrieve_cases_with_content_right.return_value = [
            self.create_case(self.case_id1, {})
        ]
        self.set_repository_case_type(self.create_case_type(read_max_n_cases=10))

        # 3. Execute
        result: list[model.Case] = case_service_retrieve_cases_by_id(self.service, cmd)

        # 4. Verify
        assert [x.id for x in result] == [self.case_id1]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveCaseCohortLinksByCaseType(BaseRetrieveCaseTestCase):
    """Tests covering case_service_retrieve_case_cohort_links_by_case_type."""

    def test_happy_path_returns_all_with_identity_cohort_mapping(self) -> None:
        # Only case IDs are fetched (read_fields); no full Case objects loaded.
        # 1. Input
        cmd: command.RetrieveCaseCohortLinksByCaseTypeCommand = (
            command.RetrieveCaseCohortLinksByCaseTypeCommand(
                user=self.user, case_type_id=self.case_type_id
            )
        )

        # 2. Mocks: read_fields returns (id,) tuples — no content fields
        self.repository.read_fields = Mock(
            return_value=[
                (self.case_id1, {self.cohort_id1: self.cohort_definition_id1}),
                (self.case_id2, {self.cohort_id2: self.cohort_definition_id2}),
            ]
        )

        # 3. Execute
        result: list[model.CaseCohortLink] = (
            case_service_retrieve_case_cohort_links_by_case_type(self.service, cmd)
        )

        # 4. Verify: two entries, identity mapping, no full-case or CaseType lookup
        assert len(result) == 2
        assert result[0].case_id == self.case_id1
        assert result[0].cohort_id == self.cohort_id1
        assert result[0].cohort_definition_id == self.cohort_definition_id1
        assert result[1].case_id == self.case_id2
        assert result[1].cohort_id == self.cohort_id2
        assert result[1].cohort_definition_id == self.cohort_definition_id2
        assert self.repository.read_fields.call_count == 1
        assert self.repository.crud.call_count == 0

    def test_empty_cases_returns_empty_list(self) -> None:
        # 1. Input
        cmd: command.RetrieveCaseCohortLinksByCaseTypeCommand = (
            command.RetrieveCaseCohortLinksByCaseTypeCommand(
                user=self.user, case_type_id=self.case_type_id
            )
        )

        # 2. Mocks
        self.repository.read_fields = Mock(return_value=[])

        # 3. Execute
        result: list[model.CaseCohortLink] = (
            case_service_retrieve_case_cohort_links_by_case_type(self.service, cmd)
        )

        # 4. Verify
        assert result == []


@pytest.mark.scenario_ids("TC-SEC-29-02")
def test_mapping_branches_decimal_col_type() -> None:
    # 1. Setup minimal class instance
    base: BaseRetrieveCaseTestCase = BaseRetrieveCaseTestCase()
    base.setUp()

    col_type: enum.ColType = enum.ColType.DECIMAL_1
    filter_factory: Callable[[BaseRetrieveCaseTestCase, UUID], Any] = (
        lambda self, key: self.create_typed_number_set_filter(key, {Decimal("5.1")})  # type: ignore[arg-type]
    )
    value_factory: Callable[[], str] = lambda: "5.1"

    # Prepare column and filter
    col_id: UUID = uuid4()
    ref_col_id: UUID = uuid4()
    col, ref_col = base.create_col(col_id, ref_col_id, col_type)
    # Compose an OR with Exists to avoid filtering away matching rows
    exists_filter: TypedExistsFilter = TypedExistsFilter(
        type=FilterType.EXISTS.value, key=str(col_id)
    )
    filter: TypedCompositeFilter = base.create_composite_filter(
        [filter_factory(base, col_id), exists_filter], operator=LogicalOperator.OR
    )
    cq: model.CaseQuery = model.CaseQuery(
        label=None,
        case_type_id=base.case_type_id,
        case_set_ids=None,
        datetime_range_filter=None,
        filter=filter,
    )
    cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
        user=base.user, case_query=cq
    )

    # 2. Mocks
    base.attach_abac_policy(cmd)
    base.set_repository_cols_and_ref_cols([col], [ref_col])
    case_content: dict[UUID, str | None] = {col_id: value_factory()}
    base.service._retrieve_cases_with_content_right = Mock(
        return_value=[base.create_case(base.case_id1, case_content)]
    )
    base.set_repository_case_type(base.create_case_type(read_max_n_cases=5))

    # 3. Execute
    result: model.CaseQueryResult = case_service_retrieve_cases_by_query(
        base.service, cmd
    )

    # 4. Verify
    base.assertQueryResult(result, [base.case_id1], False)


@pytest.mark.scenario_ids("TC-SEC-29-02")
def test_mapping_branches_text_col_type() -> None:
    # 1. Setup minimal class instance
    base: BaseRetrieveCaseTestCase = BaseRetrieveCaseTestCase()
    base.setUp()

    col_type: enum.ColType = enum.ColType.TEXT
    filter_factory: Callable[[BaseRetrieveCaseTestCase, UUID], Any] = (
        lambda self, key: self.create_typed_string_set_filter(key, {"alpha"})
    )
    value_factory: Callable[[], str] = lambda: "alpha"

    # Prepare column and filter
    col_id: UUID = uuid4()
    ref_col_id: UUID = uuid4()
    col, ref_col = base.create_col(col_id, ref_col_id, col_type)
    # Compose an OR with Exists to avoid filtering away matching rows
    exists_filter: TypedExistsFilter = TypedExistsFilter(
        type=FilterType.EXISTS.value, key=str(col_id)
    )
    filter: TypedCompositeFilter = base.create_composite_filter(
        [filter_factory(base, col_id), exists_filter], operator=LogicalOperator.OR
    )
    case_query: model.CaseQuery = model.CaseQuery(
        label=None,
        case_type_id=base.case_type_id,
        case_set_ids=None,
        datetime_range_filter=None,
        filter=filter,
    )
    cmd: command.RetrieveCasesByQueryCommand = command.RetrieveCasesByQueryCommand(
        user=base.user, case_query=case_query
    )

    # 2. Mocks
    base.attach_abac_policy(cmd)
    base.set_repository_cols_and_ref_cols([col], [ref_col])
    case_content: dict[UUID, str | None] = {col_id: value_factory()}
    base.service._retrieve_cases_with_content_right = Mock(
        return_value=[base.create_case(base.case_id1, case_content)]
    )
    base.set_repository_case_type(base.create_case_type(read_max_n_cases=5))

    # 3. Execute
    result: model.CaseQueryResult = case_service_retrieve_cases_by_query(
        base.service, cmd
    )

    # 4. Verify
    base.assertQueryResult(result, [base.case_id1], False)
