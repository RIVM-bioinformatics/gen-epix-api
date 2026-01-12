from datetime import datetime, timedelta
from typing import Iterable, cast
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import gen_epix.casedb.domain.command as case_command
import gen_epix.casedb.domain.enum as case_enum
import gen_epix.casedb.domain.model as case_model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.retrieve_stats import (
    case_service_retrieve_case_set_stats,
    case_service_retrieve_case_type_stats,
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
        # Align service.repository and repository object returned by _get_user_and_repository
        self.service.repository = self.repository
        self.service._get_user_and_repository = Mock(
            return_value=(self.user, self.repository)
        )

        # Default mocks
        self.service.crud = Mock(return_value=[])
        self.service.app = Mock()
        self.service.app.handle = Mock(return_value=[])
        self.service._retrieve_cases_with_content_right = Mock(return_value=[])

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
            subject_id=None,
            created_in_data_collection_id=created_in_data_collection_id,
            count=count,
            case_date=case_date or datetime.now(),
            content={},
        )

    def create_case_set(
        self,
        *,
        case_set_id: UUID | None = None,
        case_type_id: UUID,
        name: str = "cs",
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
            description=description,
            case_set_category_id=uuid4(),
            case_set_status_id=uuid4(),
        )

    def case_type_stats_cmd(
        self,
        *,
        case_type_ids: set[UUID] | None,
        dt_filter: TypedDatetimeRangeFilter | None = None,
    ) -> case_command.RetrieveCaseTypeStatsCommand:
        return case_command.RetrieveCaseTypeStatsCommand(
            user=self.user,
            case_type_ids=case_type_ids,
            datetime_range_filter=dt_filter,
        )

    def case_set_stats_cmd(
        self, *, case_set_ids: list[UUID] | None
    ) -> case_command.RetrieveCaseSetStatsCommand:
        return case_command.RetrieveCaseSetStatsCommand(
            user=self.user,
            case_set_ids=case_set_ids,
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


class TestCaseTypeStats(BaseRetrieveStatsTestCase):
    def test_no_case_type_ids_full_access_reads_all(self) -> None:
        dt_filter = TypedDatetimeRangeFilter(
            type=FilterType.DATETIME_RANGE.value,
            lower_bound=datetime.now() - timedelta(days=7),
            upper_bound=datetime.now(),
        )
        case_ids: list[UUID] = [self.case_type_id1, self.case_type_id2]

        self.repository.crud = Mock(return_value=case_ids)

        case1 = self.create_case(
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=datetime(2024, 1, 1, 12, 0, 0),
            count=None,
        )
        case2 = self.create_case(
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=case1.case_date,  # ignored in date stats
            count=3,
        )
        self.service._retrieve_cases_with_content_right = Mock(
            side_effect=[[case1, case2], []]
        )

        abac = self.mock_abac(is_full_access=True, readable_case_type_ids=set())

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ) as get_abac:
            cmd = self.case_type_stats_cmd(case_type_ids=None, dt_filter=dt_filter)
            result: list[case_model.CaseTypeStat] = (
                case_service_retrieve_case_type_stats(self.service, cmd)
            )

        # Verify
        self.assertEqual(len(result), 2)
        result_by_id: dict[UUID, case_model.CaseTypeStat] = {
            x.case_type_id: x for x in result
        }
        self.assertEqual(result_by_id[self.case_type_id1].n_cases, 1 + 3)
        self.assertEqual(
            result_by_id[self.case_type_id1].first_case_date, case1.case_date
        )
        self.assertEqual(
            result_by_id[self.case_type_id1].last_case_date, case1.case_date
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

        # Assert _retrieve_cases_with_content_right interactions
        calls = self.service._retrieve_cases_with_content_right.call_args_list
        self.assertEqual(len(calls), 2)
        for i, ct_id in enumerate(case_ids):
            args, kwargs = calls[i]
            self.assertEqual(args[3], case_enum.CaseRight.READ_CASE)  # right
            self.assertEqual(args[4], ct_id)  # case_type_id
            self.assertTrue(kwargs.get("calculate_case_date"))
            self.assertFalse(kwargs.get("apply_max_n_cases"))
            self.assertIs(kwargs.get("datetime_range_filter"), dt_filter)

    def test_no_case_type_ids_restricted_access_uses_abac_ids(self) -> None:
        readable_ids = {self.case_type_id1, self.case_type_id2}
        case1 = self.create_case(
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=datetime(2023, 6, 1, 0, 0, 0),
            count=None,
        )
        case2 = self.create_case(
            case_type_id=self.case_type_id2,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=datetime(2023, 6, 2, 0, 0, 0),
            count=2,
        )
        self.service._retrieve_cases_with_content_right = Mock(
            side_effect=[[case1], [case2]]
        )

        abac = self.mock_abac(is_full_access=False, readable_case_type_ids=readable_ids)

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            cmd = self.case_type_stats_cmd(case_type_ids=None)
            result: list[case_model.CaseTypeStat] = (
                case_service_retrieve_case_type_stats(self.service, cmd)
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
            cmd = self.case_type_stats_cmd(case_type_ids=requested_ids)
            with self.assertRaisesRegex(Exception, "READ_CASE right for case types"):
                case_service_retrieve_case_type_stats(self.service, cmd)

        self.repository.crud.assert_not_called()

    def test_provided_case_type_ids_authorized_computes_stats(self) -> None:
        requested_ids = {self.case_type_id1}
        abac = self.mock_abac(
            is_full_access=False, readable_case_type_ids=requested_ids
        )

        case1 = self.create_case(
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=datetime(2022, 5, 1, 0, 0, 0),
            count=None,
        )
        case2 = self.create_case(
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=datetime(2022, 6, 1, 0, 0, 0),
            count=4,
        )
        case3 = self.create_case(
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=case1.case_date,
            count=1,
        )
        self.service._retrieve_cases_with_content_right = Mock(
            return_value=[case1, case2, case3]
        )

        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=abac,
        ):
            cmd = self.case_type_stats_cmd(case_type_ids=requested_ids)
            result: list[case_model.CaseTypeStat] = (
                case_service_retrieve_case_type_stats(self.service, cmd)
            )

        self.assertEqual(len(result), 1)
        stat = result[0]
        self.assertEqual(stat.case_type_id, self.case_type_id1)
        self.assertEqual(stat.n_cases, 1 + 4 + 1)
        self.assertEqual(stat.first_case_date, case1.case_date)
        self.assertEqual(stat.last_case_date, case2.case_date)

    def test_missing_abac_policy_raises_assertion(self) -> None:
        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=None,
        ):
            cmd = self.case_type_stats_cmd(case_type_ids={self.case_type_id1})
            with self.assertRaises(AssertionError):
                case_service_retrieve_case_type_stats(self.service, cmd)


class TestCaseSetStats(BaseRetrieveStatsTestCase):
    def test_case_set_ids_filter_and_stats(self) -> None:
        # Input case sets and members
        cs1 = self.create_case_set(
            case_set_id=self.case_set_id1, case_type_id=self.case_type_id1
        )
        cs2 = self.create_case_set(
            case_set_id=self.case_set_id2, case_type_id=self.case_type_id1
        )

        def crud_side_effect(cmd: case_command.Command) -> list[object]:
            if isinstance(cmd, case_command.CaseSetCrudCommand):
                return [cs1, cs2]
            if isinstance(cmd, case_command.CaseSetMemberCrudCommand):
                # This return value is ignored by patched map_paired_elements below
                return []
            return []

        self.service.crud.side_effect = crud_side_effect

        # Build cases for the single case_type
        c1 = self.create_case(
            case_id=uuid4(),
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_private,
            case_date=datetime(2024, 1, 1),
        )
        c2 = self.create_case(
            case_id=uuid4(),
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_public,
            case_date=datetime(2024, 1, 2),
        )
        c3 = self.create_case(
            case_id=uuid4(),
            case_type_id=self.case_type_id1,
            created_in_data_collection_id=self.data_collection_id_private,
            case_date=datetime(2024, 1, 3),
        )

        # Patch map_paired_elements to return our mapping
        def map_pairs(
            _: Iterable[tuple[UUID, UUID]], as_set: bool = True
        ) -> dict[UUID, set[UUID]]:
            _use_as_set = as_set
            id_c1: UUID = cast(UUID, c1.id)
            id_c2: UUID = cast(UUID, c2.id)
            id_c3: UUID = cast(UUID, c3.id)
            return {
                self.case_set_id1: {id_c1, id_c2},
                self.case_set_id2: {id_c2, id_c3},
            }

        # app.handle side effects: first for OrganizationAccessCasePolicy, then for RetrieveCasesById
        def app_handle_side_effect(cmd: case_command.Command) -> list[object]:
            if isinstance(cmd, case_command.OrganizationAccessCasePolicyCrudCommand):
                policy_private = case_model.OrganizationAccessCasePolicy(
                    id=self.data_collection_id_private,
                    organization_id=self.user.organization_id,
                    data_collection_id=self.data_collection_id_private,
                    case_type_set_id=uuid4(),
                    is_active=True,
                    is_private=True,
                    add_case=False,
                    remove_case=False,
                    add_case_set=False,
                    remove_case_set=False,
                    read_case_set=False,
                    write_case_set=False,
                )
                policy_public = case_model.OrganizationAccessCasePolicy(
                    id=self.data_collection_id_public,
                    organization_id=self.user.organization_id,
                    data_collection_id=self.data_collection_id_public,
                    case_type_set_id=uuid4(),
                    is_active=True,
                    is_private=False,
                    add_case=False,
                    remove_case=False,
                    add_case_set=False,
                    remove_case_set=False,
                    read_case_set=False,
                    write_case_set=False,
                )
                return [policy_private, policy_public]
            if isinstance(cmd, case_command.RetrieveCasesByIdCommand):
                return [c1, c2, c3]
            return []

        self.service.app.handle.side_effect = app_handle_side_effect

        cmd = self.case_set_stats_cmd(
            case_set_ids=[self.case_set_id1, self.case_set_id2]
        )

        with patch(
            "gen_epix.casedb.services.case.retrieve_stats.map_paired_elements",
            new=map_pairs,
        ):
            result: list[case_model.CaseSetStat] = case_service_retrieve_case_set_stats(
                self.service, cmd
            )

        # Verify result for both case sets
        self.assertEqual(len(result), 2)
        by_id: dict[UUID, case_model.CaseSetStat] = {x.case_set_id: x for x in result}
        self.assertEqual(by_id[self.case_set_id1].n_cases, 2)
        self.assertEqual(by_id[self.case_set_id1].n_own_cases, 1)  # c1 only
        self.assertEqual(by_id[self.case_set_id1].first_case_date, datetime(2024, 1, 1))
        self.assertEqual(by_id[self.case_set_id1].last_case_date, datetime(2024, 1, 2))

        self.assertEqual(by_id[self.case_set_id2].n_cases, 2)
        self.assertEqual(by_id[self.case_set_id2].n_own_cases, 1)  # c3 only
        self.assertEqual(by_id[self.case_set_id2].first_case_date, datetime(2024, 1, 2))
        self.assertEqual(by_id[self.case_set_id2].last_case_date, datetime(2024, 1, 3))

        # Verify CRUD calls and filters
        crud_calls = self.service.crud.call_args_list
        self.assertEqual(len(crud_calls), 2)
        cs_cmd = crud_calls[0].args[0]
        self.assertIsInstance(cs_cmd, case_command.CaseSetCrudCommand)
        self.assertEqual(cs_cmd.operation, CrudOperation.READ_ALL)
        self.assertIsNotNone(cs_cmd.query_filter)
        cs_member_cmd = crud_calls[1].args[0]
        self.assertIsInstance(cs_member_cmd, case_command.CaseSetMemberCrudCommand)
        self.assertEqual(cs_member_cmd.operation, CrudOperation.READ_ALL)
        self.assertIsNotNone(cs_member_cmd.query_filter)

        # Verify app.handle was called with OrganizationAccessCasePolicy and RetrieveCasesById
        handle_types = [type(x.args[0]) for x in self.service.app.handle.call_args_list]
        self.assertIn(
            case_command.OrganizationAccessCasePolicyCrudCommand, handle_types
        )
        self.assertIn(case_command.RetrieveCasesByIdCommand, handle_types)

    def test_no_case_sets_initially_sets_ids_from_members_and_returns_empty(
        self,
    ) -> None:
        # No case sets returned initially
        def crud_side_effect(cmd: case_command.Command) -> list[object]:
            if isinstance(cmd, case_command.CaseSetCrudCommand):
                return []
            if isinstance(cmd, case_command.CaseSetMemberCrudCommand):
                return []
            return []

        self.service.crud.side_effect = crud_side_effect

        # Mapping from members (unused here, ensure callable still returns a dict)
        def map_pairs(
            _: Iterable[tuple[UUID, UUID]], as_set: bool = True
        ) -> dict[UUID, set[UUID]]:
            _use_as_set = as_set
            return {}

        cmd = self.case_set_stats_cmd(case_set_ids=None)
        with patch(
            "gen_epix.casedb.services.case.retrieve_stats.map_paired_elements",
            new=map_pairs,
        ):
            result: list[case_model.CaseSetStat] = case_service_retrieve_case_set_stats(
                self.service, cmd
            )

        self.assertEqual(result, [])
        crud_calls = self.service.crud.call_args_list
        self.assertEqual(len(crud_calls), 2)
        self.assertIsInstance(crud_calls[0].args[0], case_command.CaseSetCrudCommand)
        self.assertIsInstance(
            crud_calls[1].args[0], case_command.CaseSetMemberCrudCommand
        )

    def test_special_case_case_set_with_no_members(self) -> None:
        # One case set without members
        cs = self.create_case_set(
            case_set_id=self.case_set_id1, case_type_id=self.case_type_id1
        )

        def crud_side_effect(cmd: case_command.Command) -> list[object]:
            if isinstance(cmd, case_command.CaseSetCrudCommand):
                return [cs]
            if isinstance(cmd, case_command.CaseSetMemberCrudCommand):
                return []
            return []

        self.service.crud.side_effect = crud_side_effect

        # Map includes the case set id with an empty set to avoid KeyError in union
        def map_pairs(
            _: Iterable[tuple[UUID, UUID]], as_set: bool = True
        ) -> dict[UUID, set[UUID]]:
            _use_as_set = as_set
            return {self.case_set_id1: set()}

        # Policies: none, and retrieving cases for empty list returns empty
        self.service.app.handle = Mock(return_value=[])

        cmd = self.case_set_stats_cmd(case_set_ids=[self.case_set_id1])
        with patch(
            "gen_epix.casedb.services.case.retrieve_stats.map_paired_elements",
            new=map_pairs,
        ):
            result: list[case_model.CaseSetStat] = case_service_retrieve_case_set_stats(
                self.service, cmd
            )

        self.assertEqual(len(result), 1)
        stat = result[0]
        self.assertEqual(stat.case_set_id, self.case_set_id1)
        self.assertEqual(stat.n_cases, 0)
        self.assertEqual(stat.n_own_cases, 0)
        self.assertIsNone(stat.first_case_date)
        self.assertIsNone(stat.last_case_date)
