# import logging
# from datetime import date
# from test.casedb.casedb_test_client import CasedbTestClient as Env
# from test.test_client.enum import TestType
# from uuid import UUID, uuid4

# import pytest

# from gen_epix.casedb.domain import command, enum, model
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


# class TestGetCaseDate:
#     """Unit tests for CaseService.get_case_date() method."""

#     def test_returns_none_when_case_type_col_ids_is_empty(self, env: Env) -> None:
#         """Should return None immediately if case_type_col_ids list is empty."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         case_id = uuid4()
#         case_type_col_ids: list[UUID] = []

#         with env.repositories[enum.RepositoryType.DICT].uow() as uow:
#             result = case_service.get_case_date(uow, user, case_id, case_type_col_ids)

#         assert result is None

#     def test_returns_time_day_date_when_present(self, env: Env) -> None:
#         """Should return datetime.date object when TIME_DAY value is in case content."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content containing col_id -> "2024-01-15"
#         # - Col with col_type=ColType.TIME_DAY
#         # - Verify returned date is date(2024, 1, 15)

#         # 1. Create TIME dimension
#         time_dim: model.Dim = env.create_dim(
#             user_or_str=user, code="test_time_dim", dim_type=enum.DimType.TIME
#         )

#         # 2. Create TIME_DAY column linked to the dimension
#         time_day_col: model.Col = env.create_col(
#             user_or_str=user,
#             code="test_time_day_col",
#             col_type=enum.ColType.TIME_DAY,
#             dim=time_dim,
#             set_dummy_dim=False,  # Use our own dim instead of auto-generated
#         )
#         # Link col to dim if not done automatically

#         # 3. Create a CaseType (required for cases)
#         case_type: model.CaseType = env.create_case_type(
#             user_or_str=user,
#             case_type="test_case_type_for_date",
#             disease=None,  # or create/use existing disease
#             etiological_agent=None,
#             set_dummy_disease=True,
#             set_dummy_etiological_agent=True,
#         )

#         # 4. Create CaseTypeCol linking CaseType to Col
#         case_type_col: model.CaseTypeCol = env.create_case_type_col(
#             user_or_str=user,
#             code="test_case_type_col_time_day",
#             col=time_day_col,
#             set_dummy_case_type=False,  # We already created case_type
#             set_dummy_col=False,
#         )

#         # 5. Create DataCollection (required for cases)
#         data_collection: model.DataCollection = env.create_data_collection(
#             user_or_str=user, name="test_data_collection_date"
#         )

#         # 6. Create Case with content containing the date value
#         case: model.Case = model.Case(
#             id=uuid4(),
#             case_type_id=case_type.id,
#             subject_id=None,
#             created_in_data_collection_id=data_collection.id,
#             case_date=date(2024, 1, 15),
#             content={case_type_col.id: "2024-01-15"},
#         )

#         created_case: model.Case = env.app.handle(
#             command.CreateCasesCommand(
#                 user=user,
#                 cases=[case],
#                 data_collection_ids=[data_collection.id],
#                 case_type_id=case_type.id,
#                 is_update=False,
#             )
#         )

#         with env.repositories[enum.RepositoryType.DICT].uow() as uow:
#             result = case_service.get_case_date(
#                 uow,
#                 user,
#                 created_case.id,
#                 [case_type_col.id],  # List of CaseTypeCol IDs to check
#             )
#         assert result is not None
#         assert result == date(2024, 1, 15)

#     def test_returns_first_valid_date_when_multiple_cols_provided(
#         self, env: Env
#     ) -> None:
#         """Should return date from first col_id with valid content, iterating in order."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content: {col_id1: None, col_id2: "2024-02-20", col_id3: "2024-03-30"}
#         # - Cols for each col_id
#         # - Verify returned date is from col_id2 (first non-None)

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_converts_time_week_to_monday_of_week(self, env: Env) -> None:
#         """Should convert TIME_WEEK format '2024-W08' to Monday of that week."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content containing col_id -> "2024-W08"
#         # - Col with col_type=ColType.TIME_WEEK
#         # - Verify returned date is date.fromisocalendar(2024, 8, 1)

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_converts_time_month_to_first_day_of_month(self, env: Env) -> None:
#         """Should convert TIME_MONTH format '2024-06' to first day of that month."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content containing col_id -> "2024-06"
#         # - Col with col_type=ColType.TIME_MONTH
#         # - Verify returned date is date(2024, 6, 1)

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_converts_time_quarter_to_first_day_of_quarter(self, env: Env) -> None:
#         """Should convert TIME_QUARTER format '2024-Q3' to first day of quarter."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content containing col_id -> "2024-Q3"
#         # - Col with col_type=ColType.TIME_QUARTER
#         # - Verify returned date is date(2024, 7, 1)  # Q3 starts in July

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_converts_time_year_to_first_day_of_year(self, env: Env) -> None:
#         """Should convert TIME_YEAR format '2024' to first day of that year."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content containing col_id -> "2024"
#         # - Col with col_type=ColType.TIME_YEAR
#         # - Verify returned date is date(2024, 1, 1)

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_returns_none_when_col_id_not_in_case_content(self, env: Env) -> None:
#         """Should return None when provided col_id is missing from case.content."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content: {}  # empty
#         # - Col with valid col_type
#         # - Verify returned date is None

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_returns_none_when_col_value_is_none(self, env: Env) -> None:
#         """Should return None when case.content[col_id] exists but is None."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content: {col_id: None}
#         # - Col with valid col_type
#         # - Verify returned date is None

#         pytest.skip("TODO: Implement fixture creation in TestClient")

#     def test_skips_col_when_col_id_not_found_in_db(self, env: Env) -> None:
#         """Should skip to next col_id when current col_id doesn't exist in database."""
#         user = env.get_root_user()
#         case_service: CaseService = env.services[enum.ServiceType.CASE]

#         # TODO: Create test fixtures:
#         # - Case with content: {missing_col_id: "2024-01-01", valid_col_id: "2024-02-01"}
#         # - Col for valid_col_id only (missing_col_id not in DB)
#         # - Verify returned date is from valid_col_id

#         pytest.skip("TODO: Implement fixture creation in TestClient")
