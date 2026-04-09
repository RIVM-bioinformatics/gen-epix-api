import datetime
from collections.abc import Callable, Iterable
from decimal import Decimal
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_retrieve_cases_by_query(
    self: BaseCaseService, cmd: command.RetrieveCasesByQueryCommand
) -> model.CaseQueryResult:
    # TODO: This is an inefficient call first loading all cases, then filtering them and then keeping only the ids. To be replaced by optimized query.
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    case_query = cmd.case_query
    case_set_ids = case_query.case_set_ids
    case_type_id = case_query.case_type_id
    datetime_range_filter = case_query.datetime_range_filter

    # Special case: zero case_set_ids or zero case_type_ids (None equals all)
    # TODO: return empty CaseQueryResult instead of empty list
    if case_set_ids is not None and len(case_set_ids) == 0:
        raise NotImplementedError("To be implemented")

    # @ABAC: get case abac
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    is_full_access = case_abac.is_full_access
    has_case_read = case_abac.get_combinations_with_access_right(
        enum.CaseRight.READ_CASE
    )
    if case_type_id not in has_case_read and not is_full_access:
        raise exc.UnauthorizedAuthError(f"Unauthorized CaseType: {case_type_id}")

    with repository.uow() as uow:
        if case_set_ids:
            # @ABAC: Verify any access to all given case sets if applicable
            _verify_case_set_access(
                self, user, case_set_ids, case_type_id, case_abac, uow
            )
        if case_query.filter:
            # @ABAC: Verify validity of filter
            cols = _verify_filter_validity(self, user, case_query, uow)

        # @ABAC: Retrieve all cases with read access, and content filtered on Col read access
        cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            # user_case_access,
            enum.CaseRight.READ_CASE,
            case_type_id,
            case_ids=None,
            datetime_range_filter=datetime_range_filter,
            filter_content=True,
            # Disable the helper's early max results limit, since we need to apply it after filtering by case sets and filters, which happens after retrieving the cases
            apply_max_n_cases=not case_set_ids and not case_query.filter,
        )
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

        # retrieve CaseType to apply max results limit
        cases, is_max_results_exceeded = _apply_max_results_limit(
            self, user, case_type_id, uow, cases
        )

    return model.CaseQueryResult(
        case_query=case_query,
        case_ids=[x.id for x in cases],  # type: ignore[misc]
        is_max_results_exceeded=is_max_results_exceeded,
    )


def _apply_max_results_limit(
    self: BaseCaseService,
    user: model.User,
    case_type_id: UUID,
    uow: BaseUnitOfWork,
    cases: list[model.Case],
) -> tuple[list[model.Case], bool]:
    case_types: list[model.CaseType] = self.repository.crud(  # type: ignore
        uow,
        user.id,
        model.CaseType,
        None,
        [case_type_id],
        CrudOperation.READ_SOME,
    )
    if not case_types:
        raise exc.InvalidArgumentsError(f"Invalid CaseType ID: {case_type_id}")
    case_type = case_types[0]
    # Apply max results limit
    is_max_results_exceeded = False
    _raw = case_type.props.read_max_n_cases
    max_n_cases = _raw if _raw > 0 else self._default_props.read_max_n_cases
    if len(cases) > max_n_cases:
        is_max_results_exceeded = True
        cases = cases[:max_n_cases]
    return cases, is_max_results_exceeded


def _verify_filter_validity(
    self: BaseCaseService,
    user: model.User,
    case_query: model.CaseQuery,
    uow: BaseUnitOfWork,
) -> list[model.RefCol]:
    case_query.filter.set_keys(lambda x: UUID(x) if isinstance(x, str) else x)
    cols = _verify_case_filter(self, uow, user, case_query.filter)
    return cols


def _verify_case_set_access(
    self: BaseCaseService,
    user: model.User,
    case_set_ids: set[UUID],
    case_type_id: UUID,
    case_abac: model.CaseAbac,
    uow: BaseUnitOfWork,
) -> None:
    case_sets = self._retrieve_case_sets_with_content_right(
        uow,
        user.id,  # type: ignore[arg-type]
        case_abac,
        # user_case_access
        enum.CaseRight.READ_CASE_SET,
        case_type_id=case_type_id,
    ) + self._retrieve_case_sets_with_content_right(
        uow,
        user.id,  # type: ignore[arg-type]
        case_abac,
        # user_case_access
        enum.CaseRight.WRITE_CASE_SET,
        case_type_id=case_type_id,
    )
    unauthorized_case_set_ids = case_set_ids - {x.id for x in case_sets}
    if unauthorized_case_set_ids:
        unauthorized_case_set_ids_str = ", ".join(
            [str(x) for x in unauthorized_case_set_ids]
        )
        raise exc.UnauthorizedAuthError(
            f"Unauthorized case sets: {unauthorized_case_set_ids_str}"
        )


def case_service_retrieve_cases_by_id(
    self: BaseCaseService,
    cmd: command.RetrieveCasesByIdCommand,
    on_invalid_case_id: str = "raise",
) -> list[model.Case]:
    case_type_id = cmd.case_type_id
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
            case_type_id,
            case_ids=case_ids,
            filter_content=True,
            on_invalid_case_id=on_invalid_case_id,
        )
        if not cases:
            return []

        case_types: list[model.CaseType] = self.repository.crud(  # type: ignore
            uow,
            user.id,
            model.CaseType,
            None,
            [case_type_id],
            CrudOperation.READ_SOME,
        )
        if not case_types:
            raise exc.InvalidArgumentsError(f"Invalid CaseType ID: {case_type_id}")
        case_type = case_types[0]

        # Apply max results limit
        _raw = case_type.props.read_max_n_cases
        max_n_cases = _raw if _raw > 0 else self._default_props.read_max_n_cases
        if max_n_cases > 0 and len(cases) > max_n_cases:
            cases = cases[:max_n_cases]

    return cases


# TEMPORARY: kept for reference while refactoring, remove afterwards

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

#     # @ABAC: Verify read access to all given CaseTypes if applicable
#     if case_type_ids and not is_full_access:
#         if not case_type_ids.issubset(set(has_case_read.keys())):
#             raise exc.UnauthorizedAuthError(f"Unauthorized CaseTypes: {case_type_ids}")

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
#         ref_cols: list[model.RefCol] = []
#         if case_query.filter:
#             # Make sure filter keys are UUIDs
#             case_query.filter.set_keys(lambda x: UUID(x) if isinstance(x, str) else x)
#             ref_cols = _verify_case_filter(self, uow, user, case_query.filter)

#         # @ABAC: Retrieve all cases with read access, and content filtered on Col
#         # read access
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

#         # Filter cases by CaseTypes
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


# TEMPORARY: kept for reference while refactoring, remove afterwards

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


def _verify_case_filter(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    user: model.User,
    composite_filter: CompositeFilter,
) -> list[model.RefCol]:
    # Retrieve Cols corresponding to filter keys
    filter_col_ids = composite_filter.get_keys()
    filter_cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user.id,
        model.Col,
        None,
        filter_col_ids,
        CrudOperation.READ_SOME,
    )
    # Retrieve cols for Cols
    ref_cols: list[model.RefCol] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user.id,
        model.RefCol,
        None,
        list(
            {x.ref_col_id for x in filter_cols}
        ),  # TODO: consider READ_SOME allowing duplicate ids
        CrudOperation.READ_SOME,
    )
    ref_cols_map = {x.id: x for x in ref_cols}
    ref_cols = [ref_cols_map[x.ref_col_id] for x in filter_cols]
    # Verify filter validity
    concept_valid_values: dict[UUID, set[str]] = {}
    region_valid_values: dict[UUID, set[str]] = {}
    for col, ref_col, composite_filter in zip(  # type: ignore[assignment]
        filter_cols, ref_cols, composite_filter.filters
    ):
        if ref_col.concept_set_id or ref_col.region_set_id:
            if isinstance(composite_filter, StringSetFilter):
                validate_concept_or_region(
                    self,
                    user,
                    composite_filter,
                    concept_valid_values,
                    region_valid_values,
                    col,
                    ref_col,
                )
            else:
                raise exc.InvalidArgumentsError(
                    f"Column {col.id}: invalid filter type: {composite_filter.__class__.__name__}"
                )

    return ref_cols


def validate_concept_or_region(
    self: BaseCaseService,
    user: model.User,
    stringset_filter: StringSetFilter,
    concept_valid_values: dict[UUID, set[str]],
    region_valid_values: dict[UUID, set[str]],
    col: model.Col,
    ref_col: model.RefCol,
) -> None:
    valid_values = None
    if ref_col.concept_set_id is not None:
        # Get valid region set values
        valid_values = _get_valid_concepts(self, user, concept_valid_values, ref_col)
    elif ref_col.region_set_id is not None:
        # Get valid region set values
        valid_values = _get_valid_region_values(
            self, user, region_valid_values, ref_col
        )
        # Handle invalid values
    if valid_values is not None:
        _validate_filter_members(stringset_filter, col, valid_values)


def _validate_filter_members(
    stringset_filter: StringSetFilter,
    col: model.Col,
    valid_values: set[str],
) -> None:
    invalid_values = [
        str(x) for x in stringset_filter.members if str(x).lower() not in valid_values
    ]
    if len(invalid_values):
        invalid_values_str = ", ".join(invalid_values)
        raise exc.InvalidArgumentsError(
            f"Column {col.id}: invalid {stringset_filter.__class__.__name__} filter members: {invalid_values_str}"
        )


def _get_valid_region_values(
    self: BaseCaseService,
    user: model.User,
    region_valid_values: dict[UUID, set[str]],
    ref_col: model.RefCol,
) -> set[str]:
    if ref_col.region_set_id not in region_valid_values:
        regions: list[model.Region] = self.app.handle(
            command.RegionCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=UuidSetFilter(
                    key="region_set_id",
                    members=frozenset({ref_col.region_set_id}),  # type: ignore[arg-type]
                ),
            )
        )
        assert isinstance(regions, list)
        region_valid_values[ref_col.region_set_id] = {str(x.id).lower() for x in regions}  # type: ignore[index]
    valid_values = region_valid_values[ref_col.region_set_id]  # type: ignore[index]
    return valid_values


def _get_valid_concepts(
    self: BaseCaseService,
    user: model.User,
    concept_valid_values: dict[UUID, set[str]],
    ref_col: model.RefCol,
) -> set[str]:
    if ref_col.concept_set_id not in concept_valid_values:
        concepts: list[model.Concept] = self.app.handle(
            command.ConceptCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=UuidSetFilter(
                    key="concept_set_id",
                    members=frozenset({ref_col.concept_set_id}),  # type: ignore[arg-type]
                ),
            )
        )
        concept_valid_values[ref_col.concept_set_id] = {str(x.id).lower() for x in concepts}  # type: ignore[index]
    return concept_valid_values[ref_col.concept_set_id]  # type: ignore[index]


def _get_map_functions_for_filters(
    ref_cols: Iterable[model.RefCol],
) -> list[Callable[[Any], Any]]:

    # Check validity of filter and generate map_fns
    map_fns: list[Callable[[Any], Any]] = []
    for ref_col in ref_cols:
        _get_map_function_for_col(map_fns, ref_col)
    return map_fns


def _get_map_function_for_col(
    map_fns: list[Callable[[Any], Any]],
    ref_col: model.RefCol,
) -> None:
    mapping: dict[enum.ColType, Callable[[Any], Any]] = {
        enum.ColType.TIME_DAY: lambda x: (
            datetime.date.fromisoformat(x) if isinstance(x, str) else x
        ),
        enum.ColType.DECIMAL_0: lambda x: int(x) if isinstance(x, str) else x,
        enum.ColType.GEO_LATLON: lambda x: (
            (float(x.split(",")[0]), float(x.split(",")[1]))
            if isinstance(x, str)
            else x
        ),
    }
    if ref_col.col_type in mapping:
        map_fns.append(mapping[ref_col.col_type])
    elif ref_col.col_type in enum.ColTypeSet.COL_TYPES_STR_LIKE.value:
        map_fns.append(lambda x: x if isinstance(x, str) else str(x))
    elif ref_col.col_type in enum.ColTypeSet.NUMBER.value - {enum.ColType.DECIMAL_0}:
        map_fns.append(lambda x: Decimal(x) if isinstance(x, str) else x)
    else:
        raise exc.InvalidArgumentsError(f"Unsupported column type: {ref_col.col_type}")
