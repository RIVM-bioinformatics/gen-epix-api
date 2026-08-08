"""
Unit tests for CaseType dimension CRUD service.

Tests follow the structure and conventions of the commondb upload tests,
ensuring strict isolation and full coverage of the public entry point.
"""

from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock, patch
from typing import Any, List
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import enum, exc, model
from gen_epix.fastapp import CrudOperation


# Helpers
class DimLike:
    """Lightweight object mimicking Dim for testing side effects."""

    def __init__(
        self,
        id: UUID,
        case_type_id: UUID,
        ref_dim_id: UUID,
        occurrence: int = 0,
        is_case_date_dim: bool = False,
        is_time_stats_dim: bool = False,
        is_geo_stats_dim: bool = False,
    ) -> None:
        self.id = id
        self.case_type_id = case_type_id
        self.ref_dim_id = ref_dim_id
        self.occurrence = occurrence
        self.is_case_date_dim = is_case_date_dim
        self.is_time_stats_dim = is_time_stats_dim
        self.is_geo_stats_dim = is_geo_stats_dim


class RefDimLike:
    def __init__(self, id: UUID, code: str, dim_type: enum.DimType) -> None:
        self.id = id
        self.code = code
        self.dim_type = dim_type


class BaseDimTestCase(BaseCrudTestCase):
    def setup_method(self) -> None:
        super().setup_method()
        self.service._compose_id_filter = Mock(side_effect=lambda *pairs: (pairs))

        # IDs
        self.user_id = uuid4()
        self.case_type_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.ref_dim_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.other_ref_dim_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.ctd_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.other_ctd_id = UUID("550e8400-e29b-41d4-a716-446655440005")

    # Assertions
    def expectRepoCalled(self) -> None:
        assert self.service.repository.crud.called

    def expectList(self, retval: Any) -> None:
        assert isinstance(retval, list)


# Admin path tests
@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAdminCreate(BaseDimTestCase):
    def test_create_sets_occurrence_and_returns_service_crud(self) -> None:
        # 1. Input
        ctd: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            is_case_date_dim=True,
        )
        cmd = self.create_crud_command(
            CrudOperation.CREATE_ONE, user_id=self.user_id, objs=[ctd]
        )

        # 2. Mocks
        # existing Dim for same (case_type_id, ref_dim_id): none
        # ref_dim list: TIME
        ref_dim_obj: RefDimLike = RefDimLike(
            self.ref_dim_id, "RefDim.TIME", enum.DimType.TIME
        )

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[-1]
            if op == CrudOperation.READ_ALL:
                return []
            if op == CrudOperation.READ_SOME and args[2] == model.RefDim:
                return [ref_dim_obj]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect
        expected_retval: List[Any] = [object()]
        self.service.crud.return_value = expected_retval

        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=True,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"
            ) as cascade_delete,
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute
            retval = case_service_crud_dim(self.service, cmd)

            # 4. Verify
            cascade_delete.assert_called_once()
            self.expectRepoCalled()
            assert ctd.occurrence == 1
            assert retval == expected_retval

    def test_create_sets_occurrence_max_plus_one_and_unsets_other_case_date(
        self,
    ) -> None:
        # 1. Input
        new_ctd: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            is_case_date_dim=True,
        )
        existing_same_key: DimLike = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=2,
            is_case_date_dim=False,
        )
        other_for_same_case_type: DimLike = DimLike(
            id=self.other_ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.other_ref_dim_id,
            occurrence=1,
            is_case_date_dim=True,
        )
        cmd = self.create_crud_command(
            CrudOperation.CREATE_ONE, user_id=self.user_id, objs=[new_ctd]
        )

        # 2. Mocks
        ref_dim_obj: RefDimLike = RefDimLike(
            self.ref_dim_id, "RefDim.TIME", enum.DimType.TIME
        )

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[-1]
            model_class = args[2]
            if op == CrudOperation.READ_ALL and model_class == model.Dim:
                # First READ_ALL: existing dims with same key -> [existing_same_key]
                # Second READ_ALL: other dims for same case_type -> [other_for_same_case_type]
                # Use call count to branch
                count = self.service.repository.crud.call_count
                return [existing_same_key] if count <= 1 else [other_for_same_case_type]
            if op == CrudOperation.READ_SOME and model_class == model.RefDim:
                return [ref_dim_obj]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect
        self.service.crud.return_value = [object()]

        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=True,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute
            retval = case_service_crud_dim(self.service, cmd)

            # 4. Verify
            assert new_ctd.occurrence == 3
            # Ensure other case_date_dim is unset and updated
            assert not other_for_same_case_type.is_case_date_dim
            self.service.repository.crud.assert_any_call(
                self.uow,
                self.user_id,
                model.Dim,
                CrudOperation.UPDATE_ONE,
                objs=other_for_same_case_type,
            )
            assert isinstance(retval, list)

    def test_create_case_date_with_non_time_dim_raises(self) -> None:
        # 1. Input
        ctd: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            is_case_date_dim=True,
        )
        cmd = self.create_crud_command(
            CrudOperation.CREATE_ONE, user_id=self.user_id, objs=[ctd]
        )

        # 2. Mocks
        non_time_dim: RefDimLike = RefDimLike(
            self.ref_dim_id, "RefDim.GEO", enum.DimType.GEO
        )

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[-1]
            if op == CrudOperation.READ_ALL:
                return []
            if op == CrudOperation.READ_SOME and args[2] == model.RefDim:
                return [non_time_dim]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=True,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute + 4. Verify
            with pytest.raises(exc.InvalidArgumentsError):
                case_service_crud_dim(self.service, cmd)

    def test_create_case_date_with_missing_dim_raises(self) -> None:
        # 1. Input
        ctd: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            is_case_date_dim=True,
        )
        cmd = self.create_crud_command(
            CrudOperation.CREATE_ONE, user_id=self.user_id, objs=[ctd]
        )

        # 2. Mocks
        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[-1]
            if op == CrudOperation.READ_ALL:
                return []
            if op == CrudOperation.READ_SOME and args[2] == model.RefDim:
                return []
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=True,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute + 4. Verify
            with pytest.raises(exc.InvalidIdsError):
                case_service_crud_dim(self.service, cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAdminUpdate(BaseDimTestCase):
    def test_update_ref_dim_id_changes_raises(self) -> None:
        # 1. Input
        updated: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        cmd = self.create_crud_command(
            CrudOperation.UPDATE_ONE, user_id=self.user_id, objs=[updated]
        )

        # 2. Mocks
        stored: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.other_ref_dim_id,
        )

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[-1]
            if op == CrudOperation.READ_SOME and args[2] == model.Dim:
                return [stored]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=True,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute + 4. Verify
            with pytest.raises(exc.InvalidArgumentsError):
                case_service_crud_dim(self.service, cmd)

    def test_update_time_stats_exclusivity_unsets_others(self) -> None:
        # 1. Input
        updated: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            is_case_date_dim=True,
        )
        cmd = self.create_crud_command(
            CrudOperation.UPDATE_ONE, user_id=self.user_id, objs=[updated]
        )

        # 2. Mocks
        stored: DimLike = DimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        other_time_true: DimLike = DimLike(
            id=self.other_ctd_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.other_ref_dim_id,
            is_case_date_dim=True,
        )

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[-1]
            model_class = args[2]
            if op == CrudOperation.READ_SOME and model_class == model.Dim:
                return [stored]
            if op == CrudOperation.READ_ALL and model_class == model.Dim:
                return [other_time_true]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=True,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute
            retval = case_service_crud_dim(self.service, cmd)

            # 4. Verify
            assert not other_time_true.is_case_date_dim
            self.service.repository.crud.assert_any_call(
                self.uow,
                self.user_id,
                model.Dim,
                CrudOperation.UPDATE_ONE,
                objs=other_time_true,
            )
            assert isinstance(retval, list)


# ABAC path tests
@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAbacReadAndWrite(BaseDimTestCase):
    def test_abac_none_policy_returns_service_crud(self) -> None:
        # 1. Input
        cmd = self.create_crud_command(CrudOperation.READ_ALL, user_id=self.user_id)
        expected: List[Any] = [object()]

        # 2. Mocks
        self.service.crud.return_value = expected
        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.get_ref_data_access_from_command",
                return_value=None,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=False,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute
            retval = case_service_crud_dim(self.service, cmd)

            # 4. Verify
            assert retval == expected
            self.service.crud.assert_called_once_with(cmd)

    def test_abac_non_read_operation_raises_assertion(self) -> None:
        # 1. Input
        cmd = self.create_crud_command(CrudOperation.UPDATE_ONE, user_id=self.user_id)

        # 2. Mocks
        ref_data_access = Mock()
        ref_data_access.is_full_access = False
        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.get_ref_data_access_from_command",
                return_value=ref_data_access,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=False,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute + 4. Verify
            with pytest.raises(AssertionError):
                case_service_crud_dim(self.service, cmd)

    def test_abac_read_filters_by_access(self) -> None:
        # 1. Input
        cmd = self.create_crud_command(CrudOperation.READ_ALL, user_id=self.user_id)
        expected: List[Any] = [object()]
        access_filter = Mock()

        # 2. Mocks
        ref_data_access = Mock()
        ref_data_access.is_full_access = False
        ref_data_access.get_dim_filter.return_value = access_filter

        with (
            patch(
                "gen_epix.casedb.services.case.crud_dim.get_ref_data_access_from_command",
                return_value=ref_data_access,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_dim.is_refdata_admin_or_above",
                return_value=False,
            ),
            patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"),
            patch(
                "gen_epix.casedb.services.case.crud_dim.crud_with_access_filter",
                return_value=expected,
            ) as caf,
        ):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute
            retval = case_service_crud_dim(self.service, cmd)

            # 4. Verify
            assert retval == expected
            ref_data_access.get_dim_filter.assert_called_once_with("id")
            caf.assert_called_once()
            called_args = caf.call_args[0]
            assert called_args[0] is self.service
            assert called_args[1] is self.uow
            assert called_args[2] is cmd
            assert called_args[3] is access_filter


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestPreconditions(BaseDimTestCase):
    def test_missing_user_raises(self) -> None:
        # 1. Input
        cmd = Mock()
        cmd.user = None

        # 2. Mocks
        with patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute + 4. Verify
            with pytest.raises(AssertionError):
                case_service_crud_dim(self.service, cmd)

    def test_missing_user_id_raises(self) -> None:
        # 1. Input
        cmd = Mock()
        cmd.user = Mock()
        cmd.user.id = None

        # 2. Mocks
        with patch("gen_epix.casedb.services.case.crud_dim._crud_cascade_delete"):
            from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim

            # 3. Execute + 4. Verify
            with pytest.raises(AssertionError):
                case_service_crud_dim(self.service, cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestSetDimOccurrence(BaseDimTestCase):
    """
    Unit tests for _set_dim_occurrence function.

    Tests ensure deterministic, order-independent occurrence assignment for
    Dim objects. The algorithm uses only persisted dimensions for the baseline
    and assigns occurrences based on stable sorted position within batch.
    """

    def test_no_existing_dims_assigns_occurrence_1(self) -> None:
        """When no existing dimensions exist, first new dim gets occurrence 1."""
        # 1. Input
        new_dim = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim, [], [new_dim])

        # 3. Verify
        assert new_dim.occurrence == 1

    def test_one_existing_dim_assigns_occurrence_2(self) -> None:
        """When one persisted dimension exists, next dim gets occurrence 2."""
        # 1. Input
        existing_dim = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=1,
        )
        new_dim = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim, [existing_dim], [new_dim])

        # 3. Verify
        assert new_dim.occurrence == 2

    def test_multiple_existing_dims_assigns_max_plus_one(self) -> None:
        """When multiple persisted dims exist, next dim gets max + 1."""
        # 1. Input
        existing_dim1 = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=1,
        )
        existing_dim2 = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=2,
        )
        new_dim = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim, [existing_dim1, existing_dim2], [new_dim])

        # 3. Verify
        assert new_dim.occurrence == 3

    def test_existing_dims_with_gaps_assigns_max_plus_one(self) -> None:
        """
        When persisted dims have gaps (e.g., 1 and 3), next dim gets max + 1.

        This is expected behavior: we use the maximum persisted occurrence
        to ensure no collisions, even if there are gaps. The database
        constraint prevents duplicate (case_type_id, ref_dim_id, occurrence)
        tuples, so sequentiality is enforced at commit time.
        """
        # 1. Input
        existing_dim1 = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=1,
        )
        existing_dim2 = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=3,  # Gap: no occurrence 2
        )
        new_dim = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim, [existing_dim1, existing_dim2], [new_dim])

        # 3. Verify
        assert new_dim.occurrence == 4

    def test_two_new_dims_same_batch_get_sequential_occurrences(self) -> None:
        """
        Two new dims in same batch with same (case_type_id, ref_dim_id)
        get sequential occurrences 1 and 2 when no persisted dims exist.
        """
        # 1. Input
        new_dim1 = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440010"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        new_dim2 = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440011"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        batch = [new_dim1, new_dim2]

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim1, [], batch)
        _set_dim_occurrence(new_dim2, [], batch)

        # 3. Verify
        assert new_dim1.occurrence == 1
        assert new_dim2.occurrence == 2

    def test_two_new_dims_deterministic_regardless_of_initial_values(self) -> None:
        """
        Two new dims get the same occurrences regardless of their
        initial (temporary) occurrence values.

        This tests the core bug fix: temporary occurrence values should
        not influence the final assignment.
        """
        # 1. Input - Scenario A: dim1 starts with 2, dim2 with 1
        new_dim1a = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440010"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=2,  # Temporary initial value
        )
        new_dim2a = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440011"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=1,  # Temporary initial value
        )
        batch_a = [new_dim1a, new_dim2a]

        # Scenario B: dim1 starts with 0, dim2 with 99
        new_dim1b = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440010"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=0,  # Different temporary initial value
        )
        new_dim2b = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440011"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=99,  # Different temporary initial value
        )
        batch_b = [new_dim1b, new_dim2b]

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim1a, [], batch_a)
        _set_dim_occurrence(new_dim2a, [], batch_a)

        _set_dim_occurrence(new_dim1b, [], batch_b)
        _set_dim_occurrence(new_dim2b, [], batch_b)

        # 3. Verify - both scenarios yield identical results
        assert new_dim1a.occurrence == new_dim1b.occurrence
        assert new_dim2a.occurrence == new_dim2b.occurrence
        assert new_dim1a.occurrence == 1
        assert new_dim2a.occurrence == 2

    def test_two_new_dims_deterministic_regardless_of_processing_order(
        self,
    ) -> None:
        """
        Two new dims get the same occurrences regardless of the order
        they are processed.

        Tests that the algorithm is order-independent by processing
        them in different orders and verifying identical results.
        """
        # 1. Input - create two dims with stable IDs
        dim1_id = UUID("550e8400-e29b-41d4-a716-446655440010")
        dim2_id = UUID("550e8400-e29b-41d4-a716-446655440011")

        # Scenario A: process dim1 then dim2
        new_dim1a = DimLike(
            id=dim1_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        new_dim2a = DimLike(
            id=dim2_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        batch_a = [new_dim1a, new_dim2a]

        # Scenario B: process dim2 then dim1 (reverse order)
        new_dim1b = DimLike(
            id=dim1_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        new_dim2b = DimLike(
            id=dim2_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        batch_b = [new_dim1b, new_dim2b]

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        # Scenario A: forward order
        _set_dim_occurrence(new_dim1a, [], batch_a)
        _set_dim_occurrence(new_dim2a, [], batch_a)

        # Scenario B: reverse order
        _set_dim_occurrence(new_dim2b, [], batch_b)
        _set_dim_occurrence(new_dim1b, [], batch_b)

        # 3. Verify - both scenarios yield identical results per dim
        assert new_dim1a.occurrence == new_dim1b.occurrence
        assert new_dim2a.occurrence == new_dim2b.occurrence
        # By ID sort: dim1 (lower ID) is first → occurrence 1
        assert new_dim1a.occurrence == 1
        assert new_dim2a.occurrence == 2

    def test_three_new_dims_same_batch_get_sequential_occurrences(self) -> None:
        """Three new dims in same batch get sequential occurrences 1, 2, 3."""
        # 1. Input
        new_dim1 = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440010"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        new_dim2 = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440011"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        new_dim3 = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440012"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        batch = [new_dim1, new_dim2, new_dim3]

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim1, [], batch)
        _set_dim_occurrence(new_dim2, [], batch)
        _set_dim_occurrence(new_dim3, [], batch)

        # 3. Verify
        assert new_dim1.occurrence == 1
        assert new_dim2.occurrence == 2
        assert new_dim3.occurrence == 3

    def test_new_dims_with_existing_dims_get_correct_sequence(self) -> None:
        """
        When persisted dims and new dims exist together, new dims
        continue the sequence from the max persisted occurrence.
        """
        # 1. Input
        existing_dim1 = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=1,
        )
        existing_dim2 = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=2,
        )
        new_dim1 = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440010"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        new_dim2 = DimLike(
            id=UUID("550e8400-e29b-41d4-a716-446655440011"),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        batch = [new_dim1, new_dim2]

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim1, [existing_dim1, existing_dim2], batch)
        _set_dim_occurrence(new_dim2, [existing_dim1, existing_dim2], batch)

        # 3. Verify
        assert new_dim1.occurrence == 3
        assert new_dim2.occurrence == 4

    def test_different_case_types_not_included_in_calculation(self) -> None:
        """
        Dims with different case_type_id in batch are not included
        in occurrence calculation for another case_type_id.

        Note: existing_dims is already filtered by case_type at the
        caller level (_load_existing_dims), so we only test batch filtering.
        """
        # 1. Input
        other_case_type_id = UUID("550e8400-e29b-41d4-a716-446655440020")
        batch_dim_other_case = DimLike(
            id=uuid4(),
            case_type_id=other_case_type_id,
            ref_dim_id=self.ref_dim_id,
            occurrence=100,  # High occurrence - should not be considered
        )
        new_dim = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        batch = [batch_dim_other_case, new_dim]

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim, [], batch)

        # 3. Verify - occurrence should be 1 (batch dim is filtered by case_type)
        assert new_dim.occurrence == 1

    def test_different_ref_dims_not_included_in_calculation(self) -> None:
        """
        Dims with different ref_dim_id in batch are not included
        in occurrence calculation for another ref_dim_id.

        Note: existing_dims is already filtered by ref_dim at the
        caller level (_load_existing_dims), so we only test batch filtering.
        """
        # 1. Input
        other_ref_dim_id = UUID("550e8400-e29b-41d4-a716-446655440030")
        batch_dim_other_ref = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=other_ref_dim_id,
            occurrence=100,  # High occurrence - should not be considered
        )
        new_dim = DimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            ref_dim_id=self.ref_dim_id,
        )
        batch = [batch_dim_other_ref, new_dim]

        # 2. Execute
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        _set_dim_occurrence(new_dim, [], batch)

        # 3. Verify - occurrence should be 1 (batch dim is filtered by ref_dim)
        assert new_dim.occurrence == 1


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestGroupDimsByKey(BaseDimTestCase):
    """Unit tests for _group_dims_by_key."""

    def test_empty_list_returns_empty_dict(self) -> None:
        from gen_epix.casedb.services.case.crud_dim import _group_dims_by_key

        assert _group_dims_by_key([]) == {}

    def test_single_dim_produces_one_group(self) -> None:
        dim = DimLike(
            id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id
        )
        from gen_epix.casedb.services.case.crud_dim import _group_dims_by_key

        groups = _group_dims_by_key([dim])
        assert len(groups) == 1
        assert (self.case_type_id, self.ref_dim_id) in groups
        assert groups[(self.case_type_id, self.ref_dim_id)][0] is dim

    def test_same_key_dims_grouped_together(self) -> None:
        dim1 = DimLike(
            id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id
        )
        dim2 = DimLike(
            id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id
        )
        from gen_epix.casedb.services.case.crud_dim import _group_dims_by_key

        groups = _group_dims_by_key([dim1, dim2])
        assert len(groups) == 1
        group = groups[(self.case_type_id, self.ref_dim_id)]
        assert dim1 in group
        assert dim2 in group

    def test_different_keys_produce_separate_groups(self) -> None:
        other_ref = UUID("550e8400-e29b-41d4-a716-446655440099")
        dim_a = DimLike(
            id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id
        )
        dim_b = DimLike(
            id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=other_ref
        )
        from gen_epix.casedb.services.case.crud_dim import _group_dims_by_key

        groups = _group_dims_by_key([dim_a, dim_b])
        assert len(groups) == 2
        assert groups[(self.case_type_id, self.ref_dim_id)] == [dim_a]
        assert groups[(self.case_type_id, other_ref)] == [dim_b]

    def test_insertion_order_preserved_within_group(self) -> None:
        dims = [
            DimLike(
                id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id
            )
            for _ in range(5)
        ]
        from gen_epix.casedb.services.case.crud_dim import _group_dims_by_key

        groups = _group_dims_by_key(dims)
        group = groups[(self.case_type_id, self.ref_dim_id)]
        assert group == dims


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCrudCreateDimBatch(BaseDimTestCase):
    """
    Integration-style unit tests for _crud_create_dim with large batches.

    These tests exercise the O(n log n) occurrence assignment path that
    replaced the previous per-dim O(n²) loop.
    """

    def _make_cmd(self, dims: list) -> Any:
        return self.create_crud_command(
            CrudOperation.CREATE_SOME, user_id=self.user_id, objs=dims
        )

    def test_large_batch_same_key_sequential_occurrences(self) -> None:
        """
        50 dims sharing (case_type_id, ref_dim_id) with no existing dims
        get occurrences 1..50 assigned deterministically by str(id) sort.
        """
        n = 50
        dims = [
            DimLike(
                id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id
            )
            for _ in range(n)
        ]
        cmd = self._make_cmd(dims)
        self.service.repository.crud.return_value = []  # no existing dims

        from gen_epix.casedb.services.case.crud_dim import _crud_create_dim

        _crud_create_dim(dims, cmd, self.service, self.uow)

        occurrences = sorted(d.occurrence for d in dims)
        assert occurrences == list(range(1, n + 1))

    def test_large_batch_matches_pre_refactor_set_dim_occurrence(self) -> None:
        """
        The new grouping approach assigns identical occurrences to what
        _set_dim_occurrence would have computed when called per-dim.
        """
        from gen_epix.casedb.services.case.crud_dim import _set_dim_occurrence

        dim_ids = [
            UUID(f"550e8400-e29b-41d4-a716-4466554400{i:02d}") for i in range(20)
        ]
        # New approach: group-based assignment
        dims_new = [
            DimLike(id=d_id, case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id)
            for d_id in dim_ids
        ]
        # Old approach: per-dim _set_dim_occurrence calls
        dims_old = [
            DimLike(id=d_id, case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id)
            for d_id in dim_ids
        ]

        # --- new approach (group-based) ---
        cmd = self._make_cmd(dims_new)
        self.service.repository.crud.return_value = []

        from gen_epix.casedb.services.case.crud_dim import _crud_create_dim

        _crud_create_dim(dims_new, cmd, self.service, self.uow)

        # --- old approach (per-dim) ---
        for d in dims_old:
            _set_dim_occurrence(d, [], dims_old)

        # Both must produce identical occurrences for each dim by id
        new_by_id = {d.id: d.occurrence for d in dims_new}
        old_by_id = {d.id: d.occurrence for d in dims_old}
        assert new_by_id == old_by_id

    def test_two_groups_independent_occurrence_sequences(self) -> None:
        """
        Dims belonging to different (case_type_id, ref_dim_id) groups
        each get independent sequential occurrences starting from 1.
        """
        other_ref = UUID("550e8400-e29b-41d4-a716-446655440099")
        group_a = [
            DimLike(
                id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=self.ref_dim_id
            )
            for _ in range(3)
        ]
        group_b = [
            DimLike(id=uuid4(), case_type_id=self.case_type_id, ref_dim_id=other_ref)
            for _ in range(3)
        ]
        all_dims = group_a + group_b
        cmd = self._make_cmd(all_dims)
        self.service.repository.crud.return_value = []

        from gen_epix.casedb.services.case.crud_dim import _crud_create_dim

        _crud_create_dim(all_dims, cmd, self.service, self.uow)

        occs_a = sorted(d.occurrence for d in group_a)
        occs_b = sorted(d.occurrence for d in group_b)
        assert occs_a == [1, 2, 3]
        assert occs_b == [1, 2, 3]
