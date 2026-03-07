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
        self._repo_case_type_cols: list[model.CaseTypeCol] | None = None
        self._repo_cols: list[model.RefCol] | None = None

        # Default ABAC mock
        self.case_abac: Any = Mock()
        self.case_abac.is_full_access = True
        self.case_abac.get_combinations_with_access_right = Mock(
            return_value={self.case_type_id}
        )
        self.case_abac.get_case_type_cols_with_access_rights = Mock(return_value=set())

    # Helpers

    def create_case_type(self, read_max_n_cases: int = 100) -> model.CaseType:
        return model.CaseType(
            name="TEST",
            description=None,
            disease_id=None,
            etiological_agent_id=None,
            create_max_n_cases=0,
            read_max_n_cases=read_max_n_cases,
            read_max_tree_size=0,
            update_max_n_cases=0,
            delete_max_n_cases=0,
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
            subject_id=None,
            created_in_data_collection_id=self.data_collection_id,
            count=None,
            case_date=case_date or datetime.now(timezone.utc),
            content=content,
        )

    def create_case_type_col(
        self,
        case_type_col_id: UUID,
        ref_col_id: UUID,
        col_type: enum.ColType,
        concept_set_id: UUID | None = None,
        region_set_id: UUID | None = None,
    ) -> tuple[model.CaseTypeCol, model.RefCol]:
        ref_dim_id: UUID = uuid4()
        ref_col: model.RefCol = model.RefCol(
            ref_dim_id=ref_dim_id,
            ref_dim=None,
            code_suffix=None,
            code=f"REF_DIM.{case_type_col_id.hex[:8]}",
            rank=0,
            label=None,
            col_type=col_type,
            concept_set_id=concept_set_id,
            concept_set=None,
            region_set_id=region_set_id,
            region_set=None,
            genetic_distance_protocol_id=None,
            genetic_distance_protocol=None,
            description=None,
            props={},
        )
        case_type_col: model.CaseTypeCol = model.CaseTypeCol(
            case_type_id=self.case_type_id,
            case_type=None,
            case_type_dim_id=uuid4(),
            case_type_dim=None,
            ref_col_id=ref_col_id,
            ref_col=ref_col,
            code=f"CTC.{case_type_col_id.hex[:8]}",
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
            genetic_sequence_case_type_col_id=None,
            tree_algorithm_codes=None,
            props={},
        )
        case_type_col.id = case_type_col_id
        ref_col.id = ref_col_id
        return case_type_col, ref_col

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
            _obj: Any,
            ids: list[UUID] | None,
            _op: Any,
        ) -> list[Any]:
            if cls is model.CaseType and ids == [self.case_type_id]:
                return [self._repo_case_type] if self._repo_case_type else []
            if cls is model.CaseTypeCol:
                if not ids or self._repo_case_type_cols is None:
                    return []
                # Preserve input order of ids to align filters → map functions
                return [
                    next(x for x in self._repo_case_type_cols if x.id == i) for i in ids
                ]
            if cls is model.RefCol:
                if not ids or self._repo_cols is None:
                    return []
                # Preserve input order of ids to align filters → map functions
                return [next(x for x in self._repo_cols if x.id == i) for i in ids]
            return []

        self.repository.crud.side_effect = _crud_side_effect

    def set_repository_case_type(self, case_type: model.CaseType) -> None:
        self._repo_case_type = case_type
        self._install_repo_side_effect()

    def set_repository_case_type_cols_and_cols(
        self, case_type_cols: list[model.CaseTypeCol], cols: list[model.RefCol]
    ) -> None:
        self._repo_case_type_cols = case_type_cols
        self._repo_cols = cols
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
            description="",
            created_at=datetime.now(timezone.utc),
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
        ctc_id: UUID = uuid4()
        ref_col_id: UUID = uuid4()
        case_type_col, ref_col = self.create_case_type_col(
            ctc_id, ref_col_id, enum.ColType.NOMINAL, concept_set_id=uuid4()
        )
        invalid_member: str = "invalid_member"
        filter: TypedCompositeFilter = self.create_composite_filter(
            [self.create_typed_string_set_filter(ctc_id, {invalid_member})]
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
        self.set_repository_case_type_cols_and_cols([case_type_col], [ref_col])
        # No concept IDs returned → invalid
        self.service.app.handle = Mock(return_value=[])
        # Provide minimal cases to reach filter validation
        self.service._retrieve_cases_with_content_right = Mock(return_value=[])

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError):
            case_service_retrieve_cases_by_query(self.service, cmd)

    def test_filter_invalid_type_raises(self) -> None:
        # 1. Input: concept-backed column, wrong filter type
        ctc_id: UUID = uuid4()
        ref_col_id: UUID = uuid4()
        case_type_col, ref_col = self.create_case_type_col(
            ctc_id, ref_col_id, enum.ColType.NOMINAL, concept_set_id=uuid4()
        )
        filter: TypedCompositeFilter = self.create_composite_filter(
            [self.create_typed_number_set_filter(ctc_id, {1.0})]
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
        self.set_repository_case_type_cols_and_cols([case_type_col], [ref_col])
        self.service._retrieve_cases_with_content_right = Mock(return_value=[])

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError):
            case_service_retrieve_cases_by_query(self.service, cmd)

    def test_happy_path_with_filters_case_sets_and_max_limit(self) -> None:
        # 1. Input: multiple columns to exercise mapping, plus case sets
        ctc_time_id: UUID = uuid4()
        ctc_dec_id: UUID = uuid4()
        # ctc_geo_id intentionally omitted to avoid NoFilter key issues
        ctc_nom_id: UUID = uuid4()
        ctc_reg_id: UUID = uuid4()

        col_time_id: UUID = uuid4()
        col_dec_id: UUID = uuid4()
        # col_geo_id intentionally omitted
        col_nom_id: UUID = uuid4()
        col_reg_id: UUID = uuid4()

        # Create cols & case type cols
        ctc_time, col_time = self.create_case_type_col(
            ctc_time_id, col_time_id, enum.ColType.TIME_DAY
        )
        ctc_dec, col_dec = self.create_case_type_col(
            ctc_dec_id, col_dec_id, enum.ColType.DECIMAL_1
        )
        ctc_nom, col_nom = self.create_case_type_col(
            ctc_nom_id, col_nom_id, enum.ColType.NOMINAL, concept_set_id=uuid4()
        )
        ctc_reg, col_reg = self.create_case_type_col(
            ctc_reg_id, col_reg_id, enum.ColType.GEO_REGION, region_set_id=uuid4()
        )

        # Filters compatible with mapping
        from gen_epix.filter.date_range import TypedDateRangeFilter

        filters: list[Any] = [
            TypedDateRangeFilter(
                type=FilterType.DATE_RANGE.value,
                key=str(ctc_time_id),
                lower_bound=date(2024, 1, 1),
                upper_bound=date(2025, 1, 1),
            ),
            self.create_typed_number_set_filter(ctc_dec_id, {Decimal("5.1")}),  # type: ignore[arg-type]
            self.create_typed_string_set_filter(
                ctc_nom_id, {"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}
            ),
            self.create_typed_string_set_filter(
                ctc_reg_id, {"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"}
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
            description="",
            created_at=datetime.now(timezone.utc),
            case_set_category_id=uuid4(),
            case_set_category=None,
            case_set_status_id=uuid4(),
            case_set_status=None,
        )
        self.service._retrieve_case_sets_with_content_right = Mock(
            side_effect=lambda *args, **kwargs: [authorized_case_set]
        )
        # Repository data for filter verification
        self.set_repository_case_type_cols_and_cols(
            [ctc_time, ctc_dec, ctc_nom, ctc_reg],
            [col_time, col_dec, col_nom, col_reg],
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
            ctc_time_id: "2024-01-01",
            ctc_dec_id: "5.1",
            ctc_nom_id: concept_id_str,
            ctc_reg_id: region_id_str,
        }
        case2_content: dict[UUID, str | None] = {
            ctc_time_id: "2024-02-02",
            ctc_dec_id: "5.1",
            ctc_nom_id: concept_id_str,
            ctc_reg_id: region_id_str,
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
    ctc_id: UUID = uuid4()
    ref_col_id: UUID = uuid4()
    case_type_col, ref_col = base.create_case_type_col(ctc_id, ref_col_id, col_type)
    # Compose an OR with Exists to avoid filtering away matching rows
    exists_filter: TypedExistsFilter = TypedExistsFilter(
        type=FilterType.EXISTS.value, key=str(ctc_id)
    )
    filter: TypedCompositeFilter = base.create_composite_filter(
        [filter_factory(base, ctc_id), exists_filter], operator=LogicalOperator.OR
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
    base.set_repository_case_type_cols_and_cols([case_type_col], [ref_col])
    case_content: dict[UUID, str | None] = {ctc_id: value_factory()}
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
    ctc_id: UUID = uuid4()
    ref_col_id: UUID = uuid4()
    case_type_col, ref_col = base.create_case_type_col(ctc_id, ref_col_id, col_type)
    # Compose an OR with Exists to avoid filtering away matching rows
    exists_filter: TypedExistsFilter = TypedExistsFilter(
        type=FilterType.EXISTS.value, key=str(ctc_id)
    )
    filter: TypedCompositeFilter = base.create_composite_filter(
        [filter_factory(base, ctc_id), exists_filter], operator=LogicalOperator.OR
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
    base.set_repository_case_type_cols_and_cols([case_type_col], [ref_col])
    case_content: dict[UUID, str | None] = {ctc_id: value_factory()}
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
