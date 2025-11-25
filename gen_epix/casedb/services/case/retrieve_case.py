import datetime
from collections.abc import Callable, Iterable
from decimal import Decimal
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_date import (
    case_service_get_case_date,
    case_service_get_case_date_case_type_col_ids,
)
from gen_epix.fastapp.enum import CrudOperation


def case_service_retrieve_cases_by_query(
    self: BaseCaseService, cmd: command.RetrieveCasesByQueryCommand
) -> model.CaseQueryResult:
    # TODO: This is an inefficient call first loading all cases, then filtering them and then keeping only the ids. To be replaced by optimized query.
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    case_query = cmd.case_query
    case_set_ids = case_query.case_set_ids
    case_type_ids = case_query.case_type_ids
    datetime_range_filter = case_query.datetime_range_filter

    # Special case: zero case_set_ids or zero case_type_ids (None equals all)
    # TODO: return empty CaseQueryResult instead of empty list
    if case_set_ids is not None and len(case_set_ids) == 0:
        return []
    if case_type_ids is not None and len(case_type_ids) == 0:
        return []

    # @ABAC: get case abac
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    is_full_access = case_abac.is_full_access
    has_case_read = case_abac.get_combinations_with_access_right(
        enum.CaseRight.READ_CASE
    )

    # @ABAC: Verify read access to all given case types if applicable
    if case_type_ids and not is_full_access:
        if not case_type_ids.issubset(set(has_case_read.keys())):
            raise exc.UnauthorizedAuthError(f"Unauthorized case types: {case_type_ids}")

    with repository.uow() as uow:

        # @ABAC: Verify any access to all given case sets if applicable
        if case_set_ids:
            case_sets = self._retrieve_case_sets_with_content_right(
                uow,
                user.id,
                case_abac,
                # user_case_access
                enum.CaseRight.READ_CASE_SET,
            ) + self._retrieve_case_sets_with_content_right(
                uow,
                user.id,
                case_abac,
                # user_case_access
                enum.CaseRight.WRITE_CASE_SET,
            )
            invalid_case_set_ids = case_set_ids - {x.id for x in case_sets}
            if invalid_case_set_ids:
                invalid_case_set_ids_str = ", ".join(
                    [str(x) for x in invalid_case_set_ids]
                )
                raise exc.UnauthorizedAuthError(
                    f"Unauthorized case sets: {invalid_case_set_ids_str}"
                )

        # @ABAC: Verify validity of filter
        if case_query.filter:
            # Make sure filter keys are UUIDs
            case_query.filter.set_keys(lambda x: UUID(x) if isinstance(x, str) else x)
            cols = self._verify_case_filter(uow, user, case_query.filter)

        # @ABAC: Retrieve all cases with read access, and content filtered on case type
        # col read access
        cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            # user_case_access,
            enum.CaseRight.READ_CASE,
            case_ids=None,
            datetime_range_filter=datetime_range_filter,
            filter_content=True,
        )

        # Filter cases by case types
        if case_type_ids:
            cases = [x for x in cases if x.case_type_id in case_type_ids]

        target_case_type_ids: set[UUID] = (
            set(case_type_ids)
            if case_type_ids is not None
            else {x.case_type_id for x in cases}
        )

        case_type_to_case_type_col_ids: dict[UUID, list[UUID]] = (
            case_service_get_case_date_case_type_col_ids(
                self, uow, user, target_case_type_ids
            )
        )
        case_dates: dict[UUID, datetime.date | None] = {}
        for case in cases:

            case_type_col_ids = case_type_to_case_type_col_ids.get(
                case.case_type_id, []
            )
            calculated_case_date = (
                case_service_get_case_date(self, uow, user, [case.id], col_ids)
                if case.id is not None
                else None
            )
            case_dates[case.id] = calculated_case_date or case.case_date  # type: ignore[index]

        cases.sort(
            key=lambda case: case_dates.get(case.id) or datetime.date.min,  # type: ignore[arg-type]
            reverse=True,
        )

        case_type_settings: list[model.CaseTypeSettings] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeSettings,
            None,
            list(target_case_type_ids),
            CrudOperation.READ_SOME,
        )
        max_by_case_type: dict[UUID, int] = {
            case_type_setting.case_type_id: (case_type_setting.read_max_n_cases or 0)
            for case_type_setting in case_type_settings
        }
        case_type_limits: dict[UUID, int] = {}
        limited_cases: list[model.Case] = []
        is_max_results_exceeded: bool = False
        for case in cases:
            case_type_id = case.case_type_id
            limit = max_by_case_type.get(case_type_id, 0)
            # 0 or missing => no limit
            if limit and case_type_limits.get(case_type_id, 0) >= limit:
                is_max_results_exceeded = True
                continue
            limited_cases.append(case)
            case_type_limits[case_type_id] = case_type_limits.get(case_type_id, 0) + 1
        cases = limited_cases

        # Filter cases by case sets
        if case_set_ids:
            case_case_sets = self._retrieve_case_case_sets_map(uow, user.id)
            cases = [
                x
                for x in cases
                if x.id in case_case_sets
                and case_case_sets[x.id].intersection(case_set_ids)
            ]

        # Filter cases by filters
        if case_query.filter:
            filter_mapping_functions = _get_map_functions_for_filters(cols)
            cases = [
                x
                for x, y in zip(
                    cases,
                    case_query.filter.match_rows(
                        (x.content for x in cases), map_fn=filter_mapping_functions  # type: ignore[misc]
                    ),
                )
                if y
            ]

    # TODO: consider putting these cases, with their data already filtered, in a
    # cache, so that the expected subsequent call to retrieve them can be sped up

    return model.CaseQueryResult(
        case_type_id=case_type_id,
        filter=case_query.filter,
        cases=[x.id for x in cases if x.id is not None],
        is_max_results_exceeded=is_max_results_exceeded,
    )


def case_service_retrieve_cases_by_id(
    self: BaseCaseService, cmd: command.RetrieveCasesByIdCommand
) -> list[model.Case]:
    case_ids = cmd.case_ids
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    if not case_ids:
        return []
    # @ABAC: get case abac
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    with repository.uow() as uow:
        cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            case_ids=case_ids,
            filter_content=True,
        )
        if not cases:
            return []
        if len({x.case_type_id for x in cases}) > 1:
            raise exc.InvalidArgumentsError("All cases must have the same case type")
            # TODO: To be adjusted to check that all case types are equal to the given case type

        case_type_id = cases[0].case_type_id
        case_type_settings: model.CaseTypeSettings = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeSettings,
            None,
            case_type_id,
            CrudOperation.READ_ONE,
        )
        if len(cases) > case_type_settings.read_max_n_cases:
            raise exc.RequestLimitExceededAuthError(
                f"Number of cases retrieved for case type {case_type_id} exceeds the maximum allowed"
            )
        time_case_type_col_ids, date_mappers = (
            case_service_get_case_date_case_type_col_ids(
                self,
                uow,
                user,
                case_type_id,
                case_type_settings.stats_time_case_type_col_id,
            )
        )

        # TODO: filter time case type col ids and date mappers to only readable case type cols
        # use abac to see with case type cols are readable and take intersection of those
        # loop over each case and determine case date based on accessible time columns

        # For cases without calculatable case_date:
        # fill in a fixed date (default date) -> CaseService.DEFAULT_CASE_DATE

    return cases


# def case_service_retrieve_cases_by_query(
#     self: BaseCaseService, cmd: command.RetrieveCasesByQueryCommand
# ) -> model.CaseQueryResult:
#     # TODO: This is an inefficient call first loading all cases, then filtering them and then keeping only the ids. To be replaced by optimized query.
#     user, repository = self._get_user_and_repository(cmd)
#     assert isinstance(user, model.User) and user.id is not None
#     case_query = cmd.case_query
#     case_set_ids = case_query.case_set_ids
#     case_type_ids = case_query.case_type_ids
#     datetime_range_filter = case_query.datetime_range_filter

#     # Special case: zero case_set_ids or zero case_type_ids (None equals all)
#     if case_set_ids is not None and len(case_set_ids) == 0:
#         return []
#     if case_type_ids is not None and len(case_type_ids) == 0:
#         return []

#     # @ABAC: get case abac
#     case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
#     assert case_abac is not None
#     is_full_access = case_abac.is_full_access
#     has_case_read = case_abac.get_combinations_with_access_right(
#         enum.CaseRight.READ_CASE
#     )

#     # @ABAC: Verify read access to all given case types if applicable
#     if case_type_ids and not is_full_access:
#         if not case_type_ids.issubset(set(has_case_read.keys())):
#             raise exc.UnauthorizedAuthError(f"Unauthorized case types: {case_type_ids}")

#     case_ids: list[UUID] = []
#     with repository.uow() as uow:

#         # @ABAC: Verify any access to all given case sets if applicable
#         if case_set_ids:
#             case_sets = self._retrieve_case_sets_with_content_right(
#                 uow,
#                 user.id,
#                 case_abac,
#                 # user_case_access
#                 enum.CaseRight.READ_CASE_SET,
#             ) + self._retrieve_case_sets_with_content_right(
#                 uow,
#                 user.id,
#                 case_abac,
#                 # user_case_access
#                 enum.CaseRight.WRITE_CASE_SET,
#             )
#             invalid_case_set_ids = case_set_ids - {x.id for x in case_sets}
#             if invalid_case_set_ids:
#                 invalid_case_set_ids_str = ", ".join(
#                     [str(x) for x in invalid_case_set_ids]
#                 )
#                 raise exc.UnauthorizedAuthError(
#                     f"Unauthorized case sets: {invalid_case_set_ids_str}"
#                 )

#         # @ABAC: Verify validity of filter
#         cols: list[model.Col] = []
#         if case_query.filter:
#             # Make sure filter keys are UUIDs
#             case_query.filter.set_keys(lambda x: UUID(x) if isinstance(x, str) else x)
#             cols = _verify_case_filter(self, uow, user, case_query.filter)

#         # @ABAC: Retrieve all cases with read access, and content filtered on case type
#         # col read access
#         cases = self._retrieve_cases_with_content_right(
#             uow,
#             user.id,
#             case_abac,
#             # user_case_access,
#             enum.CaseRight.READ_CASE,
#             case_ids=None,
#             datetime_range_filter=datetime_range_filter,
#             filter_content=True,
#         )

#         # Filter cases by case types
#         if case_type_ids:
#             cases = [x for x in cases if x.case_type_id in case_type_ids]

#         # Filter cases by case sets
#         if case_set_ids:
#             case_ids: list[UUID] = [x.id for x in cases]  # type: ignore
#             case_case_sets = self._retrieve_case_case_sets_map(uow, user.id)
#             cases = [
#                 x
#                 for x, y in zip(cases, case_ids)
#                 if y in case_case_sets and case_case_sets[y].intersection(case_set_ids)
#             ]

#         # Filter cases by filters
#         if case_query.filter:
#             map_fns = _get_map_functions_for_filters(cols)
#             cases = [
#                 x
#                 for x, y in zip(
#                     cases,
#                     case_query.filter.match_rows(
#                         (x.content for x in cases), map_fn=map_fns  # type: ignore[misc]
#                     ),
#                 )
#                 if y
#             ]

#     # TODO: consider putting these cases, with their data already filtered, in a
#     # cache, so that the expected subsequent call to retrieve them can be sped up

#     # Return case ids
#     case_ids: list[UUID] = [x.id for x in cases]  # type: ignore
#     return case_ids


# def case_service_retrieve_cases_by_id(
#     self: BaseCaseService, cmd: command.RetrieveCasesByIdCommand
# ) -> list[model.Case]:
#     case_ids = cmd.case_ids
#     user, repository = self._get_user_and_repository(cmd)
#     assert isinstance(user, model.User) and user.id is not None
#     if not case_ids:
#         return []
#     # @ABAC: get case abac
#     case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
#     assert case_abac is not None

#     with repository.uow() as uow:
#         cases = self._retrieve_cases_with_content_right(
#             uow,
#             user.id,
#             case_abac,
#             enum.CaseRight.READ_CASE,
#             case_ids=case_ids,
#             filter_content=True,
#         )
#     return cases


# def _verify_case_filter(
#     self: BaseCaseService,
#     uow: BaseUnitOfWork,
#     user: model.User,
#     filter: CompositeFilter,
# ) -> list[model.Col]:
#     # Retrieve case type cols corresponding to filter keys
#     filter_case_type_col_ids = filter.get_keys()
#     filter_case_type_cols: list[model.CaseTypeCol] = (
#         self.repository.crud(  # type:ignore[assignment]
#             uow,
#             user.id,
#             model.CaseTypeCol,
#             None,
#             filter_case_type_col_ids,
#             CrudOperation.READ_SOME,
#         )
#     )
#     # Retrieve cols for case type cols
#     cols: list[model.Col] = self.repository.crud(  # type:ignore[assignment]
#         uow,
#         user.id,
#         model.Col,
#         None,
#         list(
#             set(x.col_id for x in filter_case_type_cols)
#         ),  # TODO: consider READ_SOME allowing duplicate ids
#         CrudOperation.READ_SOME,
#     )
#     cols_ = {x.id: x for x in cols}
#     cols = [cols_[x.col_id] for x in filter_case_type_cols]
#     # Verify filter validity
#     concept_valid_values: dict[UUID, set[str]] = {}
#     region_valid_values: dict[UUID, set[str]] = {}
#     for case_type_col, col, filter in zip(  # type:ignore[assignment]
#         filter_case_type_cols, cols, filter.filters
#     ):
#         if col.concept_set_id or col.region_set_id:
#             if isinstance(filter, StringSetFilter):
#                 valid_values = None
#                 if col.concept_set_id is not None:
#                     # Get valid region set values
#                     if col.concept_set_id not in concept_valid_values:
#                         concepts: list[model.Concept] = self.app.handle(
#                             command.ConceptCrudCommand(
#                                 user=user,
#                                 operation=CrudOperation.READ_ALL,
#                                 query_filter=UuidSetFilter(
#                                     key="concept_set_id",
#                                     members=frozenset({col.concept_set_id}),
#                                 ),
#                             )
#                         )
#                         concept_valid_values[col.concept_set_id] = {
#                             str(x.id).lower() for x in concepts
#                         }
#                     valid_values = concept_valid_values[col.concept_set_id]
#                 elif col.region_set_id is not None:
#                     # Get valid region set values
#                     if col.region_set_id not in region_valid_values:
#                         regions: list[model.Region] = self.app.handle(
#                             command.RegionCrudCommand(
#                                 user=user,
#                                 operation=CrudOperation.READ_ALL,
#                                 query_filter=UuidSetFilter(
#                                     key="region_set_id",
#                                     members=frozenset({col.region_set_id}),
#                                 ),
#                             )
#                         )
#                         region_valid_values[col.region_set_id] = set(
#                             [str(x.id).lower() for x in regions]
#                         )
#                     valid_values = region_valid_values[col.region_set_id]
#                 # Handle invalid values
#                 if valid_values is not None:
#                     invalid_values = [
#                         str(x)
#                         for x in filter.members
#                         if str(x).lower() not in valid_values
#                     ]
#                     if len(invalid_values):
#                         invalid_values_str = ", ".join(invalid_values)
#                         raise exc.InvalidArgumentsError(
#                             f"Column {case_type_col.id}: invalid {filter.__class__.__name__} filter members: {invalid_values_str}"
#                         )
#             else:
#                 raise exc.InvalidArgumentsError(
#                     f"Column {case_type_col.id}: invalid filter type: {filter.__class__.__name__}"
#                 )

#     return cols


def _get_map_functions_for_filters(
    cols: Iterable[model.Col],
) -> list[Callable[[Any], Any]]:

    # Check validity of filter and generate map_fns
    map_fns = []
    for col in cols:
        if col.col_type == enum.ColType.TIME_DAY:
            map_fns.append(
                lambda x: (datetime.date.fromisoformat(x) if isinstance(x, str) else x)
            )
        elif col.col_type in {
            enum.ColType.TIME_WEEK,
            enum.ColType.TIME_MONTH,
            enum.ColType.TIME_QUARTER,
            enum.ColType.TIME_YEAR,
            enum.ColType.GEO_REGION,
            enum.ColType.NOMINAL,
            enum.ColType.ORDINAL,
            enum.ColType.INTERVAL,
            enum.ColType.TEXT,
            enum.ColType.ID_DIRECT,
            enum.ColType.ID_PSEUDONYMISED,
            enum.ColType.ORGANIZATION,
            enum.ColType.OTHER,
        }:
            map_fns.append(lambda x: x if isinstance(x, str) else str(x))
        elif col.col_type == enum.ColType.DECIMAL_0:
            map_fns.append(lambda x: int(x) if isinstance(x, str) else x)
        elif col.col_type in {
            enum.ColType.DECIMAL_1,
            enum.ColType.DECIMAL_2,
            enum.ColType.DECIMAL_3,
            enum.ColType.DECIMAL_4,
            enum.ColType.DECIMAL_5,
            enum.ColType.DECIMAL_6,
        }:
            map_fns.append(lambda x: Decimal(x) if isinstance(x, str) else x)
        elif col.col_type == enum.ColType.GEO_LATLON:
            map_fns.append(
                lambda x: (
                    (float(x.split(",")[0]), float(x.split(",")[1]))
                    if isinstance(x, str)
                    else x
                )
            )
        else:
            raise exc.InvalidArgumentsError(f"Unsupported column type: {col.col_type}")
    return map_fns
