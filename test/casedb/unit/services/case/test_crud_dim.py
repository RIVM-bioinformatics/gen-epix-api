"""
Unit tests for CaseType dimension CRUD service.

Tests follow the structure and conventions of the commondb upload tests,
ensuring strict isolation and full coverage of the public entry point.
"""

from test.casedb.unit.services.case.base import BaseCrudTestCase
from typing import Any, List
from unittest.mock import Mock, patch
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
    def setUp(self) -> None:
        super().setUp()
        self.service._compose_id_filter = Mock(side_effect=lambda *pairs: (pairs))

        # IDs
        self.user_id = uuid4()
        self.case_type_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.ref_dim_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.other_ref_dim_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.ctd_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.other_ctd_id = UUID("550e8400-e29b-41d4-a716-446655440005")

    # Assertions
    def assertRepoCalled(self) -> None:
        self.assertTrue(self.service.repository.crud.called)

    def assertList(self, retval: Any) -> None:
        self.assertIsInstance(retval, list)


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
            op: CrudOperation = args[5]
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
            self.assertRepoCalled()
            self.assertEqual(ctd.occurrence, 1)
            self.assertEqual(retval, expected_retval)

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
            op: CrudOperation = args[5]
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
            self.assertEqual(new_ctd.occurrence, 3)
            # Ensure other case_date_dim is unset and updated
            self.assertFalse(other_for_same_case_type.is_case_date_dim)
            self.service.repository.crud.assert_any_call(
                self.uow,
                self.user_id,
                model.Dim,
                other_for_same_case_type,
                None,
                CrudOperation.UPDATE_ONE,
            )
            self.assertIsInstance(retval, list)

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
            op: CrudOperation = args[5]
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
            op: CrudOperation = args[5]
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
            op: CrudOperation = args[5]
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
            op: CrudOperation = args[5]
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
            self.assertFalse(other_time_true.is_case_date_dim)
            self.service.repository.crud.assert_any_call(
                self.uow,
                self.user_id,
                model.Dim,
                other_time_true,
                None,
                CrudOperation.UPDATE_ONE,
            )
            self.assertIsInstance(retval, list)


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
            self.assertEqual(retval, expected)
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
            self.assertEqual(retval, expected)
            ref_data_access.get_dim_filter.assert_called_once_with("id")
            caf.assert_called_once()
            called_args = caf.call_args[0]
            self.assertIs(called_args[0], self.service)
            self.assertIs(called_args[1], self.uow)
            self.assertIs(called_args[2], cmd)
            self.assertIs(called_args[3], access_filter)


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
