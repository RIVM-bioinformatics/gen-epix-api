from datetime import datetime, timedelta, timezone
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

import gen_epix.casedb.domain.command as case_command
import gen_epix.casedb.domain.enum as case_enum
import gen_epix.casedb.domain.model as case_model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.retrieve_stats import (
    case_service_retrieve_case_stats,
)
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.datetime_range import TypedDatetimeRangeFilter
from gen_epix.filter.enum import FilterType


class BaseRetrieveStatsTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={"APP_ADMIN"},
            organization_id=uuid4(),
            is_active=True,
        )

        self.case_type_id1 = UUID("550e8400-e29b-41d4-a716-446655440021")
        self.case_type_id2 = UUID("550e8400-e29b-41d4-a716-446655440022")
        self.case_set_id1 = UUID("550e8400-e29b-41d4-a716-446655440031")
        self.case_set_id2 = UUID("550e8400-e29b-41d4-a716-446655440032")
        self.data_collection_id_private = UUID("550e8400-e29b-41d4-a716-446655440041")
        self.data_collection_id_public = UUID("550e8400-e29b-41d4-a716-446655440042")

        self.service = Mock()
        self.repository = Mock()
        self.uow = Mock()
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.repository.uow.return_value = self.uow

        # Default mock for repository.crud that returns CaseType IDs
        self.repository.crud = Mock(
            return_value=[self.case_type_id1, self.case_type_id2]
        )

        # Align service.repository and repository object returned by _get_user_and_repository
        self.service.repository = self.repository
        self.service._get_user_and_repository = Mock(
            return_value=(self.user, self.repository)
        )

        # Default mocks
        self.service.crud = Mock(return_value=[])
        self.service.app = Mock()
        self.service.app.handle = Mock(return_value=[])
        self.service.retrieve_complete_case_type = Mock()

        # Mock repository.retrieve_case_stats method which is now called by the implementation
        self.repository.retrieve_case_stats = Mock()
        self.repository.read_fields = Mock(return_value=[])

    def create_case(
        self,
        *,
        case_id: UUID | None = None,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        case_date: datetime | None = None,
        count: int | None = None,
    ) -> case_model.Case:
        return case_model.Case(
            id=case_id or uuid4(),
            code=None,
            case_type_id=case_type_id,
            created_in_data_collection_id=created_in_data_collection_id,
            count=count,
            case_date=case_date or datetime.now(timezone.utc),
            content={},
        )

    def create_complete_case_type(
        self,
        *,
        case_type_id: UUID,
        case_type_access_abacs: dict[UUID, case_model.CaseTypeAccessAbac] | None = None,
        case_date_col_type_map: dict[case_enum.ColType, UUID] | None = None,
    ) -> case_model.CompleteCaseType:
        return case_model.CompleteCaseType(
            id=case_type_id,
            user_id=self.user.id,
            name="Test CaseType",
            description="Test Description",
            etiologies={},
            etiological_agents={},
            ref_dims={},
            ref_cols={},
            dims={},
            cols={},
            genetic_distance_protocols={},
            tree_algorithms={},
            case_type_access_abacs=case_type_access_abacs or {},
            case_type_share_abacs={},
            case_date_col_type_map=case_date_col_type_map or {},
            case_date_dim_id=None,  # Add this required field
            props=case_model.CaseTypeProps(
                create_max_n_cases=1000,
                read_max_n_cases=1000,
                read_max_tree_size=1000,
                update_max_n_cases=1000,
                delete_max_n_cases=1000,
            ),
        )

    def create_case_set(
        self,
        *,
        case_set_id: UUID | None = None,
        case_type_id: UUID,
        name: str = "cs",
        code: str = "cs",
        description: str = "desc",
        created_in_data_collection_id: UUID | None = None,
    ) -> case_model.CaseSet:
        return case_model.CaseSet(
            id=case_set_id or uuid4(),
            case_type_id=case_type_id,
            created_in_data_collection_id=(
                created_in_data_collection_id or self.data_collection_id_public
            ),
            name=name,
            code=code,
            description=description,
            case_set_category_id=uuid4(),
            case_set_status_id=uuid4(),
        )

    def case_stats_cmd(
        self,
        *,
        case_type_ids: set[UUID] | None,
        case_set_ids: set[UUID] | None = None,
        datetime_range_filter: TypedDatetimeRangeFilter | None = None,
    ) -> case_command.RetrieveCaseStatsCommand:
        return case_command.RetrieveCaseStatsCommand(
            user=self.user,
            case_type_ids=case_type_ids,
            case_set_ids=case_set_ids,
            datetime_range_filter=datetime_range_filter,
        )

    def case_set_stats_cmd(
        self,
        *,
        case_type_ids: set[UUID] | None = None,
        case_set_ids: set[UUID] | None = None,
        datetime_range_filter: TypedDatetimeRangeFilter | None = None,
    ) -> case_command.RetrieveCaseStatsCommand:
        return case_command.RetrieveCaseStatsCommand(
            user=self.user,
            case_type_ids=case_type_ids,
            case_set_ids=case_set_ids,
            datetime_range_filter=datetime_range_filter,
        )

    def mock_abac(
        self,
        *,
        is_full_access: bool,
        readable_case_type_ids: set[UUID],
    ) -> Mock:
        abac = Mock()
        abac.is_full_access = is_full_access
        abac.get_case_types_with_access_right = Mock(
            return_value=readable_case_type_ids
        )
        return abac


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCaseTypeStats(BaseRetrieveStatsTestCase):
    def test_no_case_type_ids_full_access_reads_all(self) -> None:
        dt_filter = TypedDatetimeRangeFilter(
            type=FilterType.DATETIME_RANGE.value,
            lower_bound=datetime.now(timezone.utc) - timedelta(days=7),
            upper_bound=datetime.now(timezone.utc),
        )
        case_type_ids: list[UUID] = [self.case_type_id1, self.case_type_id2]

        # Mock repository.crud to return CaseType IDs
        self.repository.crud = Mock(return_value=case_type_ids)

        # Mock complete CaseTypes
        complete_case_type_1 = self.create_complete_case_type(
            case_type_id=self.case_type_id1
        )
        complete_case_type_2 = self.create_complete_case_type(
            case_type_id=self.case_type_id2
        )
        self.service.retrieve_complete_case_type = Mock(
            side_effect=[complete_case_type_1, complete_case_type_2]
        )

        # Mock repository.retrieve_case_stats
        stats_1 = case_model.CaseStats(
            case_type_id=self.case_type_id1,
            n_cases=4,
            first_case_date=datetime(2024, 1, 1, 12, 0, 0),
            last_case_date=datetime(2024, 1, 1, 12, 0, 0),
        )
        stats_2 = case_model.CaseStats(
            case_type_id=self.case_type_id2,
            n_cases=0,
        )
        self.repository.retrieve_case_stats = Mock(side_effect=[stats_1, stats_2])

        abac = self.mock_abac(is_full_access=True, readable_case_type_ids=set())

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ) as get_abac:
            cmd = self.case_stats_cmd(
                case_type_ids=None, datetime_range_filter=dt_filter
            )
            result: list[case_model.CaseStats] = case_service_retrieve_case_stats(
                self.service, cmd
            )

        # Verify
        self.assertEqual(len(result), 2)
        result_by_id: dict[UUID, case_model.CaseStats] = {
            x.case_type_id: x for x in result
        }
        self.assertEqual(result_by_id[self.case_type_id1].n_cases, 4)
        self.assertEqual(
            result_by_id[self.case_type_id1].first_case_date,
            datetime(2024, 1, 1, 12, 0, 0),
        )
        self.assertEqual(
            result_by_id[self.case_type_id1].last_case_date,
            datetime(2024, 1, 1, 12, 0, 0),
        )
        self.assertEqual(result_by_id[self.case_type_id2].n_cases, 0)
        self.assertIsNone(result_by_id[self.case_type_id2].first_case_date)
        self.assertIsNone(result_by_id[self.case_type_id2].last_case_date)

        get_abac.assert_called_once_with(cmd)
        self.repository.uow.assert_called()
        self.repository.crud.assert_called_once()
        # Assert repository.crud called with expected parameters
        _, _, model_class, _, _, operation = self.repository.crud.call_args[0][:6]
        self.assertIs(model_class, case_model.CaseType)
        self.assertEqual(operation, CrudOperation.READ_ALL)

        # Assert retrieve_complete_case_type interactions
        retrieve_calls = self.service.retrieve_complete_case_type.call_args_list
        self.assertEqual(len(retrieve_calls), 2)

        # Assert repository.retrieve_case_stats interactions
        stats_calls = self.repository.retrieve_case_stats.call_args_list
        self.assertEqual(len(stats_calls), 2)

    def test_no_case_type_ids_restricted_access_uses_abac_ids(self) -> None:
        readable_ids = {self.case_type_id1, self.case_type_id2}

        # Mock complete CaseTypes
        complete_case_type_1 = self.create_complete_case_type(
            case_type_id=self.case_type_id1
        )
        complete_case_type_2 = self.create_complete_case_type(
            case_type_id=self.case_type_id2
        )
        self.service.retrieve_complete_case_type = Mock(
            side_effect=[complete_case_type_1, complete_case_type_2]
        )

        # Mock repository.retrieve_case_stats
        stats_1 = case_model.CaseStats(
            case_type_id=self.case_type_id1,
            n_cases=1,
            first_case_date=datetime(2023, 6, 1, 0, 0, 0),
            last_case_date=datetime(2023, 6, 1, 0, 0, 0),
        )
        stats_2 = case_model.CaseStats(
            case_type_id=self.case_type_id2,
            n_cases=2,
            first_case_date=datetime(2023, 6, 2, 0, 0, 0),
            last_case_date=datetime(2023, 6, 2, 0, 0, 0),
        )
        self.repository.retrieve_case_stats = Mock(side_effect=[stats_1, stats_2])

        abac = self.mock_abac(is_full_access=False, readable_case_type_ids=readable_ids)

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            cmd = self.case_stats_cmd(case_type_ids=None)
            result: list[case_model.CaseStats] = case_service_retrieve_case_stats(
                self.service, cmd
            )

        # Verify stats aggregated for both readable IDs
        self.assertEqual({x.case_type_id for x in result}, readable_ids)
        by_id = {x.case_type_id: x for x in result}
        self.assertEqual(by_id[self.case_type_id1].n_cases, 1)
        self.assertEqual(by_id[self.case_type_id2].n_cases, 2)

        # repository.crud not called in restricted path without full access
        self.repository.crud.assert_not_called()

    def test_provided_case_type_ids_unauthorized_raises(self) -> None:
        requested_ids = {self.case_type_id1, self.case_type_id2}
        abac = self.mock_abac(
            is_full_access=False, readable_case_type_ids={self.case_type_id1}
        )

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            cmd = self.case_stats_cmd(case_type_ids=requested_ids)
            with self.assertRaisesRegex(Exception, "READ_CASE right for CaseTypes"):
                case_service_retrieve_case_stats(self.service, cmd)

        self.repository.crud.assert_not_called()

    def test_provided_case_type_ids_authorized_computes_stats(self) -> None:
        requested_ids = {self.case_type_id1}
        abac = self.mock_abac(
            is_full_access=False, readable_case_type_ids=requested_ids
        )

        # Mock complete CaseType
        complete_case_type_1 = self.create_complete_case_type(
            case_type_id=self.case_type_id1
        )
        self.service.retrieve_complete_case_type = Mock(
            return_value=complete_case_type_1
        )

        # Mock repository.retrieve_case_stats
        stats_1 = case_model.CaseStats(
            case_type_id=self.case_type_id1,
            n_cases=6,  # 1 + 4 + 1
            first_case_date=datetime(2022, 5, 1, 0, 0, 0),
            last_case_date=datetime(2022, 6, 1, 0, 0, 0),
        )
        self.repository.retrieve_case_stats = Mock(return_value=stats_1)

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            cmd = self.case_stats_cmd(case_type_ids=requested_ids)
            result: list[case_model.CaseStats] = case_service_retrieve_case_stats(
                self.service, cmd
            )

        self.assertEqual(len(result), 1)
        stat = result[0]
        self.assertEqual(stat.case_type_id, self.case_type_id1)
        self.assertEqual(stat.n_cases, 6)
        self.assertEqual(stat.first_case_date, datetime(2022, 5, 1, 0, 0, 0))
        self.assertEqual(stat.last_case_date, datetime(2022, 6, 1, 0, 0, 0))

    def test_missing_abac_policy_raises_assertion(self) -> None:
        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=None,
        ):
            cmd = self.case_stats_cmd(case_type_ids={self.case_type_id1})
            with self.assertRaises(AssertionError):
                case_service_retrieve_case_stats(self.service, cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCaseSetStats(BaseRetrieveStatsTestCase):
    def test_case_set_ids_filter_and_stats(self) -> None:
        # Input case sets and members
        cs1 = self.create_case_set(
            case_set_id=self.case_set_id1, case_type_id=self.case_type_id1
        )
        cs2 = self.create_case_set(
            case_set_id=self.case_set_id2, case_type_id=self.case_type_id1
        )

        # Mock repository.read_fields to return case set info
        def mock_read_fields(*args: Any, **kwargs: Any) -> list[tuple]:
            model_class = args[2]
            if model_class == case_model.CaseSet:
                return [
                    (self.case_set_id1, self.case_type_id1),
                    (self.case_set_id2, self.case_type_id1),
                ]
            elif model_class == case_model.CaseSetMember:
                filter_arg = kwargs.get("filter")
                if hasattr(filter_arg, "value"):
                    if filter_arg.value == self.case_set_id1:
                        return [(uuid4(),), (uuid4(),)]  # 2 case IDs for case set 1
                    elif filter_arg.value == self.case_set_id2:
                        return [(uuid4(),), (uuid4(),)]  # 2 case IDs for case set 2
                return []
            return []

        self.repository.read_fields = Mock(side_effect=mock_read_fields)

        # Mock repository.crud to return CaseType IDs when needed
        self.repository.crud = Mock(return_value=[self.case_type_id1])

        # Mock complete CaseType
        complete_case_type_1 = self.create_complete_case_type(
            case_type_id=self.case_type_id1
        )
        self.service.retrieve_complete_case_type = Mock(
            return_value=complete_case_type_1
        )

        # Mock repository.retrieve_case_stats
        stats_1 = case_model.CaseStats(
            case_type_id=self.case_type_id1,
            case_set_id=self.case_set_id1,
            n_cases=2,
            n_own_cases=1,
            first_case_date=datetime(2024, 1, 1),
            last_case_date=datetime(2024, 1, 2),
        )
        stats_2 = case_model.CaseStats(
            case_type_id=self.case_type_id1,
            case_set_id=self.case_set_id2,
            n_cases=2,
            n_own_cases=1,
            first_case_date=datetime(2024, 1, 2),
            last_case_date=datetime(2024, 1, 3),
        )
        self.repository.retrieve_case_stats = Mock(side_effect=[stats_1, stats_2])

        # Mock ABAC to allow access
        abac = self.mock_abac(
            is_full_access=True, readable_case_type_ids={self.case_type_id1}
        )

        cmd = self.case_stats_cmd(
            case_type_ids=None, case_set_ids={self.case_set_id1, self.case_set_id2}
        )

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            result: list[case_model.CaseStats] = case_service_retrieve_case_stats(
                self.service, cmd
            )

        # Verify result for both case sets
        self.assertEqual(len(result), 2)
        by_id: dict[UUID, case_model.CaseStats] = {x.case_set_id: x for x in result}
        self.assertEqual(by_id[self.case_set_id1].n_cases, 2)
        self.assertEqual(by_id[self.case_set_id1].n_own_cases, 1)
        self.assertEqual(by_id[self.case_set_id1].first_case_date, datetime(2024, 1, 1))
        self.assertEqual(by_id[self.case_set_id1].last_case_date, datetime(2024, 1, 2))

        self.assertEqual(by_id[self.case_set_id2].n_cases, 2)
        self.assertEqual(by_id[self.case_set_id2].n_own_cases, 1)
        self.assertEqual(by_id[self.case_set_id2].first_case_date, datetime(2024, 1, 2))
        self.assertEqual(by_id[self.case_set_id2].last_case_date, datetime(2024, 1, 3))

    def test_no_case_sets_initially_sets_ids_from_members_and_returns_empty(
        self,
    ) -> None:
        # Mock ABAC to allow access
        abac = self.mock_abac(is_full_access=True, readable_case_type_ids=set())

        # Mock repository.crud to return empty list for CaseTypes
        self.repository.crud = Mock(return_value=[])
        cmd = self.case_stats_cmd(case_type_ids=None, case_set_ids=None)

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            result: list[case_model.CaseStats] = case_service_retrieve_case_stats(
                self.service, cmd
            )

        # When no case_set_ids provided and no case_type_ids, should return empty
        # as case_type_ids will be set() after processing
        self.assertEqual(result, [])

    def test_special_case_case_set_with_no_members(self) -> None:
        cs = self.create_case_set(
            case_set_id=self.case_set_id1, case_type_id=self.case_type_id1
        )

        # Mock repository.read_fields to return case set info but no members
        def mock_read_fields(*args: Any, **kwargs: Any) -> list[tuple]:
            model_class = args[2]
            if model_class == case_model.CaseSet:
                return [(self.case_set_id1, self.case_type_id1)]
            elif model_class == case_model.CaseSetMember:
                return []  # No members
            return []

        self.repository.read_fields = Mock(side_effect=mock_read_fields)

        # Mock repository.crud to return CaseType IDs when needed
        self.repository.crud = Mock(return_value=[self.case_type_id1])

        # Mock complete CaseType
        complete_case_type_1 = self.create_complete_case_type(
            case_type_id=self.case_type_id1
        )
        self.service.retrieve_complete_case_type = Mock(
            return_value=complete_case_type_1
        )

        # Mock repository.retrieve_case_stats to return zero stats for empty case set
        stats_empty = case_model.CaseStats(
            case_type_id=self.case_type_id1,
            case_set_id=self.case_set_id1,
            n_cases=0,
            n_own_cases=0,
        )
        self.repository.retrieve_case_stats = Mock(return_value=stats_empty)

        # Mock ABAC to allow access
        abac = self.mock_abac(
            is_full_access=True, readable_case_type_ids={self.case_type_id1}
        )

        cmd = self.case_stats_cmd(case_type_ids=None, case_set_ids={self.case_set_id1})

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            result: list[case_model.CaseStats] = case_service_retrieve_case_stats(
                self.service, cmd
            )

        self.assertEqual(len(result), 1)
        stat = result[0]
        self.assertEqual(stat.case_set_id, self.case_set_id1)
        self.assertEqual(stat.n_cases, 0)
        self.assertEqual(stat.n_own_cases, 0)
        self.assertIsNone(stat.first_case_date)
        self.assertIsNone(stat.last_case_date)
