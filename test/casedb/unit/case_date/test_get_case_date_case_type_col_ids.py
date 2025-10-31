# import logging
# from test.casedb.casedb_test_client import CasedbTestClient as Env
# from test.test_client.enum import TestType
# from uuid import uuid4

# import pytest

# from gen_epix.casedb.domain import enum
# from gen_epix.casedb.services import CaseService
# from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
# from gen_epix.commondb.util import get_app_cfgs
# from gen_epix.seqdb.domain import enum as seqdb_enum

# TEST_TYPE = TestType.CASEDB_UNIT_CASE_DATE
# DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_DEMO

# SEQDB_APP_CFGS = get_app_cfgs(
#     AppType.SEQDB,
#     seqdb_enum.ServiceType,
#     seqdb_enum.RepositoryType,
#     TEST_TYPE,
# )
# CASEDB_APP_CFGS = get_app_cfgs(
#     AppType.CASEDB,
#     enum.ServiceType,
#     enum.RepositoryType,
#     TEST_TYPE,
#     seqdb_app_cfgs=SEQDB_APP_CFGS,
# )


# @pytest.fixture(scope="module", name="env")
# def get_test_client() -> Env:
#     return Env.get_test_client(  # type: ignore[return-value]
#         test_type=TEST_TYPE.value,
#         app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
#         verbose=False,
#         log_level=logging.ERROR,
#         use_endpoints=False,
#     )


# class TestGetCaseDateCaseTypeColIds:
#     """Unit tests for CaseService.get_case_date_case_type_col_ids() method."""

#     def test_returns_empty_dict_when_no_case_type_settings_exist(
#         self, env: Env
#     ) -> None:
#         """Should return empty lists for all case_type_ids when no settings exist."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         case_type_ids = {uuid4(), uuid4()}

#         with env.repositories[enum.RepositoryType.DICT].uow() as uow:
#             result = case_service.get_case_date_case_type_col_ids(
#                 uow, user, case_type_ids
#             )

#         assert result == {case_type_id: [] for case_type_id in case_type_ids}

#     def test_returns_time_cols_ordered_by_rank(self, env: Env) -> None:
#         """Should return time cols sorted by rank_in_dim when stats_time_dim_id is set."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Dim with dim_type=DimType.TIME
#         # - CaseType with CaseTypeSettings.stats_time_dim_id = dim.id
#         # - Multiple Cols with col_type in {TIME_DAY, TIME_WEEK, TIME_MONTH}
#         #   and different rank_in_dim values (e.g., 2, None, 1)
#         # - Verify returned list is ordered: [col_rank_1, col_rank_2, col_no_rank]

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_ignores_non_time_cols_in_time_dim(self, env: Env) -> None:
#         """Should filter out non-TIME_ col_types even if they belong to stats_time_dim."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Dim with dim_type=DimType.TIME
#         # - CaseType with CaseTypeSettings.stats_time_dim_id = dim.id
#         # - Cols with mixed col_types: TIME_DAY, TEXT, NOMINAL
#         # - Verify only TIME_DAY is returned

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_returns_empty_when_stats_time_dim_id_is_none(self, env: Env) -> None:
#         """Should return empty list when CaseTypeSettings.stats_time_dim_id is None."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - CaseType with CaseTypeSettings.stats_time_dim_id = None
#         # - Verify returned list is empty

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_handles_multiple_case_types_with_different_dims(self, env: Env) -> None:
#         """Should return correct cols for each case_type when they use different dims."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Two Dims (dim1, dim2) both with dim_type=DimType.TIME
#         # - Two CaseTypes with different stats_time_dim_ids
#         # - Cols for each dim
#         # - Verify each case_type_id maps to its corresponding dim's cols

#         pytest.skip("TODO: Implement fixture creation in TestClient")
