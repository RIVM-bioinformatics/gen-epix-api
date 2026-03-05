"""
Unit tests for case type dimension CRUD service.

Tests follow the structure and conventions of the commondb upload tests,
ensuring strict isolation and full coverage of the public entry point.
"""

from typing import Any, Iterable, List, Set
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import enum, exc, model
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


# Helpers
class CaseTypeDimLike:
    """Lightweight object mimicking CaseTypeDim for testing side effects."""

    def __init__(
        self,
        id: UUID,
        case_type_id: UUID,
        dim_id: UUID,
        occurrence: int = 0,
        is_case_date_dim: bool = False,
        is_time_stats_dim: bool = False,
        is_geo_stats_dim: bool = False,
    ) -> None:
        self.id = id
        self.case_type_id = case_type_id
        self.dim_id = dim_id
        self.occurrence = occurrence
        self.is_case_date_dim = is_case_date_dim
        self.is_time_stats_dim = is_time_stats_dim
        self.is_geo_stats_dim = is_geo_stats_dim


class DimLike:
    def __init__(self, id: UUID, code: str, dim_type: enum.DimType) -> None:
        self.id = id
        self.code = code
        self.dim_type = dim_type


def make_command(
    operation: CrudOperation,
    user_id: UUID,
    objs: Iterable[Any] | None = None,
    obj_ids: Iterable[UUID] | UUID | None = None,
) -> Any:
    """Build a mock CaseTypeDimCrudCommand with required API."""
    cmd: Any = Mock()
    cmd.operation = operation
    cmd.user = Mock()
    cmd.user.id = user_id
    cmd.get_objs.return_value = list(objs) if objs is not None else None
    cmd.obj_ids = obj_ids
    return cmd


def make_uow() -> BaseUnitOfWork:
    uow: BaseUnitOfWork = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class BaseCaseTypeDimTestCase(TestCase):
    def setUp(self) -> None:
        # Service mock
        self.service = Mock()
        self.service._compose_id_filter = Mock(side_effect=lambda *pairs: (pairs))

        # Repository + UOW
        self.uow = make_uow()
        self.service.repository = Mock()
        self.service.repository.uow.return_value = self.uow
        self.service.repository.crud.return_value = []

        # Top-level service crud
        self.service.crud = Mock(return_value=[])

        # IDs
        self.user_id = uuid4()
        self.case_type_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.dim_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.other_dim_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.ctd_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.other_ctd_id = UUID("550e8400-e29b-41d4-a716-446655440005")

    # Assertions
    def assertRepoCalled(self) -> None:
        self.assertTrue(self.service.repository.crud.called)

    def assertList(self, retval: Any) -> None:
        self.assertIsInstance(retval, list)


# Admin path tests
@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAdminCreate(BaseCaseTypeDimTestCase):
    def test_create_sets_occurrence_and_returns_service_crud(self) -> None:
        # 1. Input
        ctd: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
            is_case_date_dim=True,
        )
        cmd = make_command(CrudOperation.CREATE_ONE, self.user_id, objs=[ctd])

        # 2. Mocks
        # existing CaseTypeDim for same (case_type_id, dim_id): none
        # dim list: TIME
        dim_obj: DimLike = DimLike(self.dim_id, "Dim.TIME", enum.DimType.TIME)

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[5]
            if op == CrudOperation.READ_ALL:
                return []
            if op == CrudOperation.READ_SOME and args[2] == model.Dim:
                return [dim_obj]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect
        expected_retval: List[Any] = [object()]
        self.service.crud.return_value = expected_retval

        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=True,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ) as cascade_delete,
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute
            retval = case_service_crud_case_type_dim(self.service, cmd)

            # 4. Verify
            cascade_delete.assert_called_once()
            self.assertRepoCalled()
            self.assertEqual(ctd.occurrence, 1)
            self.assertEqual(retval, expected_retval)

    def test_create_sets_occurrence_max_plus_one_and_unsets_other_case_date(
        self,
    ) -> None:
        # 1. Input
        new_ctd: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
            is_case_date_dim=True,
        )
        existing_same_key: CaseTypeDimLike = CaseTypeDimLike(
            id=uuid4(),
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
            occurrence=2,
            is_case_date_dim=False,
        )
        other_for_same_case_type: CaseTypeDimLike = CaseTypeDimLike(
            id=self.other_ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.other_dim_id,
            occurrence=1,
            is_case_date_dim=True,
        )
        cmd = make_command(CrudOperation.CREATE_ONE, self.user_id, objs=[new_ctd])

        # 2. Mocks
        dim_obj: DimLike = DimLike(self.dim_id, "Dim.TIME", enum.DimType.TIME)

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[5]
            model_class = args[2]
            if op == CrudOperation.READ_ALL and model_class == model.CaseTypeDim:
                # First READ_ALL: existing dims with same key -> [existing_same_key]
                # Second READ_ALL: other dims for same case_type -> [other_for_same_case_type]
                # Use call count to branch
                count = self.service.repository.crud.call_count
                return [existing_same_key] if count <= 1 else [other_for_same_case_type]
            if op == CrudOperation.READ_SOME and model_class == model.Dim:
                return [dim_obj]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect
        self.service.crud.return_value = [object()]

        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=True,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute
            retval = case_service_crud_case_type_dim(self.service, cmd)

            # 4. Verify
            self.assertEqual(new_ctd.occurrence, 3)
            # Ensure other case date dim is unset and updated
            self.assertFalse(other_for_same_case_type.is_case_date_dim)
            self.service.repository.crud.assert_any_call(
                self.uow,
                self.user_id,
                model.CaseTypeDim,
                other_for_same_case_type,
                None,
                CrudOperation.UPDATE_ONE,
            )
            self.assertIsInstance(retval, list)

    def test_create_case_date_with_non_time_dim_raises(self) -> None:
        # 1. Input
        ctd: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
            is_case_date_dim=True,
        )
        cmd = make_command(CrudOperation.CREATE_ONE, self.user_id, objs=[ctd])

        # 2. Mocks
        non_time_dim: DimLike = DimLike(self.dim_id, "Dim.GEO", enum.DimType.GEO)

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[5]
            if op == CrudOperation.READ_ALL:
                return []
            if op == CrudOperation.READ_SOME and args[2] == model.Dim:
                return [non_time_dim]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=True,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute + 4. Verify
            with pytest.raises(exc.InvalidArgumentsError):
                case_service_crud_case_type_dim(self.service, cmd)

    def test_create_case_date_with_missing_dim_raises(self) -> None:
        # 1. Input
        ctd: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
            is_case_date_dim=True,
        )
        cmd = make_command(CrudOperation.CREATE_ONE, self.user_id, objs=[ctd])

        # 2. Mocks
        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[5]
            if op == CrudOperation.READ_ALL:
                return []
            if op == CrudOperation.READ_SOME and args[2] == model.Dim:
                return []
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=True,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute + 4. Verify
            with pytest.raises(exc.InvalidIdsError):
                case_service_crud_case_type_dim(self.service, cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAdminUpdate(BaseCaseTypeDimTestCase):
    def test_update_dim_id_changes_raises(self) -> None:
        # 1. Input
        updated: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
        )
        cmd = make_command(CrudOperation.UPDATE_ONE, self.user_id, objs=[updated])

        # 2. Mocks
        stored: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.other_dim_id,
        )

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[5]
            if op == CrudOperation.READ_SOME and args[2] == model.CaseTypeDim:
                return [stored]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=True,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute + 4. Verify
            with pytest.raises(exc.InvalidArgumentsError):
                case_service_crud_case_type_dim(self.service, cmd)

    def test_update_time_stats_exclusivity_unsets_others(self) -> None:
        # 1. Input
        updated: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
            is_case_date_dim=True,
        )
        cmd = make_command(CrudOperation.UPDATE_ONE, self.user_id, objs=[updated])

        # 2. Mocks
        stored: CaseTypeDimLike = CaseTypeDimLike(
            id=self.ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.dim_id,
        )
        other_time_true: CaseTypeDimLike = CaseTypeDimLike(
            id=self.other_ctd_id,
            case_type_id=self.case_type_id,
            dim_id=self.other_dim_id,
            is_case_date_dim=True,
        )

        def repo_crud_side_effect(*args: Any, **kwargs: Any) -> List[Any]:
            op: CrudOperation = args[5]
            model_class = args[2]
            if op == CrudOperation.READ_SOME and model_class == model.CaseTypeDim:
                return [stored]
            if op == CrudOperation.READ_ALL and model_class == model.CaseTypeDim:
                return [other_time_true]
            return []

        self.service.repository.crud.side_effect = repo_crud_side_effect

        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=True,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute
            retval = case_service_crud_case_type_dim(self.service, cmd)

            # 4. Verify
            self.assertFalse(other_time_true.is_case_date_dim)
            self.service.repository.crud.assert_any_call(
                self.uow,
                self.user_id,
                model.CaseTypeDim,
                other_time_true,
                None,
                CrudOperation.UPDATE_ONE,
            )
            self.assertIsInstance(retval, list)


# ABAC path tests
@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestAbacReadAndWrite(BaseCaseTypeDimTestCase):
    def test_abac_none_policy_returns_service_crud(self) -> None:
        # 1. Input
        cmd = make_command(CrudOperation.READ_ALL, self.user_id)
        expected: List[Any] = [object()]

        # 2. Mocks
        self.service.crud.return_value = expected
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.get_case_abac_from_command",
                return_value=None,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=False,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute
            retval = case_service_crud_case_type_dim(self.service, cmd)

            # 4. Verify
            self.assertEqual(retval, expected)
            self.service.crud.assert_called_once_with(cmd)

    def test_abac_non_read_operation_raises_assertion(self) -> None:
        # 1. Input
        cmd = make_command(CrudOperation.UPDATE_ONE, self.user_id)

        # 2. Mocks
        case_abac = Mock()
        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.get_case_abac_from_command",
                return_value=case_abac,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=False,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute + 4. Verify
            with pytest.raises(AssertionError):
                case_service_crud_case_type_dim(self.service, cmd)

    def test_abac_read_filters_by_access(self) -> None:
        # 1. Input
        cmd = make_command(CrudOperation.READ_ALL, self.user_id)
        allowed_dim_ids: Set[UUID] = {uuid4(), uuid4()}
        expected: List[Any] = [object()]

        # 2. Mocks
        case_abac = Mock()
        readable_ref_data = Mock()
        readable_ref_data.case_type_dim_ids = allowed_dim_ids

        with (
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.get_case_abac_from_command",
                return_value=case_abac,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.get_readable_reference_data_from_command",
                return_value=readable_ref_data,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.is_metadata_admin_or_above",
                return_value=False,
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
            ),
            patch(
                "gen_epix.casedb.services.case.crud_case_type_dim.crud_with_access_filter",
                return_value=expected,
            ) as caf,
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute
            retval = case_service_crud_case_type_dim(self.service, cmd)

            # 4. Verify
            self.assertEqual(retval, expected)
            # Filter must be composed from readable reference data case_type_dim_ids
            self.service._compose_id_filter.assert_called_once_with(
                ("id", allowed_dim_ids)
            )
            caf.assert_called_once()
            called_args = caf.call_args[0]
            self.assertIs(called_args[0], self.service)
            self.assertIs(called_args[1], self.uow)
            self.assertIs(called_args[2], cmd)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestPreconditions(BaseCaseTypeDimTestCase):
    def test_missing_user_raises(self) -> None:
        # 1. Input
        cmd = Mock()
        cmd.user = None

        # 2. Mocks
        with patch(
            "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute + 4. Verify
            with pytest.raises(AssertionError):
                case_service_crud_case_type_dim(self.service, cmd)

    def test_missing_user_id_raises(self) -> None:
        # 1. Input
        cmd = Mock()
        cmd.user = Mock()
        cmd.user.id = None

        # 2. Mocks
        with patch(
            "gen_epix.casedb.services.case.crud_case_type_dim._crud_cascade_delete"
        ):
            from gen_epix.casedb.services.case.crud_case_type_dim import \
                case_service_crud_case_type_dim

            # 3. Execute + 4. Verify
            with pytest.raises(AssertionError):
                case_service_crud_case_type_dim(self.service, cmd)
