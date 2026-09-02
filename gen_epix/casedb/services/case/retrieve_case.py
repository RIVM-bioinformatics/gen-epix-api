"""Retrieve cases and validate case-content query filters under ABAC constraints.

The handlers return only cases and content visible to the acting user before applying
case-set, content, date, and configured result-limit restrictions.
"""

import datetime
from collections.abc import Callable, Iterable
from decimal import Decimal
from typing import Any, cast
from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_retrieve_cases_by_query(
    self: BaseCaseService, cmd: command.RetrieveCasesByQueryCommand
) -> model.CaseQueryResult:
    """Retrieve case IDs for a query after ABAC, set, and content filtering.

    The command currently targets one case type and may include case-set and
    column-content filters. Access checks and content filtering are applied before
    query matching, then case IDs are limited by the configured maximum. Filter keys
    are normalized from strings to UUIDs in place.

    Args:
        self: Case service handling the query.
        cmd: Query command containing case-type, set, date, and content restrictions.

    Returns:
        Matching accessible case IDs and a result-limit indicator.

    Raises:
        NotImplementedError: If an explicitly empty case-set selection is supplied.
        UnauthorizedAuthError: If the user cannot read the case type or a requested
            case set.
        InvalidArgumentsError: If filter columns, members, or types are invalid.
    """
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
    has_case_read = case_abac.get_combinations_with_access_right(
        enum.CaseRight.READ_CASE
    )
    if case_type_id not in has_case_read and not case_abac.is_full_access:
        raise exc.UnauthorizedAuthError(
            "e9a598d2", f"Unauthorized CaseType: {case_type_id}"
        )

    with repository.uow() as uow:
        case_type: model.CaseType = self.repository.crud(
            uow,
            user.id,
            model.CaseType,
            CrudOperation.READ_ONE,
            obj_ids=case_type_id,
        )
        max_n_cases = (
            case_type.props.read_max_n_cases
            if case_type.props.read_max_n_cases > 0
            else self._default_props.read_max_n_cases
        )
        if case_set_ids:
            # @ABAC: Verify any access to all given case sets if applicable
            _verify_case_set_access(
                self, user, case_set_ids, case_type_id, case_abac, uow
            )
        if case_query.filter:
            # @ABAC: Verify validity of filter
            ref_cols = _verify_filter_validity(self, user, case_query, uow)
        else:
            ref_cols = []

        # @ABAC: Retrieve all cases with read access, and content filtered on Col read access
        cases, is_max_results_exceeded = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            # user_case_access,
            enum.CaseRight.READ_CASE,
            cast(UUID, case_type.id),
            case_ids=None,
            datetime_range_filter=datetime_range_filter,
            filter_content=True,
            # Disable the helper's early max results limit if case_set_ids and filters are applied, since we need to apply it after filtering by case sets and filters, which happens after retrieving the cases
            apply_max_n_cases=False,
        )

        # Filter cases by case sets
        if case_set_ids:
            case_case_sets = self._retrieve_case_case_sets_map(uow, user.id)
            cases = [
                x
                for x in cases
                if x.id in case_case_sets
                and case_case_sets[x.id].intersection(case_set_ids)  # type: ignore[arg-type]
            ]

        # Filter cases by filters
        if case_query.filter:
            filter_mapping_functions = _get_map_functions_for_filters(ref_cols)
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

        # Apply max results limit
        is_max_results_exceeded = len(cases) > max_n_cases if max_n_cases > 0 else False
        if is_max_results_exceeded:
            cases = cases[:max_n_cases]

    return model.CaseQueryResult(
        case_query=case_query,
        case_ids=[x.id for x in cases],  # type: ignore[misc]
        is_max_results_exceeded=is_max_results_exceeded,
    )


def case_service_retrieve_case_cohort_links_by_case_type(
    self: BaseCaseService,
    cmd: command.RetrieveCaseCohortLinksByCaseTypeCommand,
) -> list[model.CaseCohortLink]:
    """Return case-to-cohort links for all cases of one case type.

    When include_missing is true, cases without cohort metadata are mapped to
    the NULL_ID placeholder pair.
    """
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    case_type_filter = UuidSetFilter(
        key="case_type_id", members=frozenset({cmd.case_type_id})
    )
    case_cohort_links: list[model.CaseCohortLink] = []
    with repository.uow() as uow:
        row_iter = list(
            self.repository.read_fields(
                uow=uow,
                user_id=user.id,
                model_class=model.Case,
                field_names=["id", "cohort"],
                filter=case_type_filter,
            )
        )
        for row in row_iter:
            cohort_dict = row[1]
            if not cohort_dict:
                if cmd.include_missing:
                    cohort_dict = {NULL_ID: NULL_ID}
                else:
                    continue
            case_cohort_links.extend(
                [
                    model.CaseCohortLink(
                        case_id=row[0], cohort_id=x, cohort_definition_id=y
                    )
                    for x, y in cohort_dict.items()
                ]
            )

    return case_cohort_links


def _verify_filter_validity(
    self: BaseCaseService,
    user: model.User,
    case_query: model.CaseQuery,
    uow: BaseUnitOfWork,
) -> list[model.RefCol]:
    """Normalize and validate content-filter keys and members.

    Args:
        self: Case service used for metadata retrieval.
        user: User whose command context is used for retrieval.
        case_query: Query whose filter keys are converted to UUIDs in place.
        uow: Active unit of work for metadata reads.

    Returns:
        Reference columns corresponding to filter order.
    """
    assert case_query.filter is not None
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
    """Ensure the user can read or write every requested case set.

    Args:
        self: Case service used for access-filtered retrieval.
        user: User whose case-set rights are checked.
        case_set_ids: Requested case-set identifiers.
        case_type_id: Required case type of the requested sets.
        case_abac: Case access metadata used for retrieval.
        uow: Active unit of work for access checks.

    Raises:
        UnauthorizedAuthError: If any requested case set is inaccessible.
    """
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
            "cd11372a", f"Unauthorized case sets: {unauthorized_case_set_ids_str}"
        )


def case_service_retrieve_cases_by_id(
    self: BaseCaseService,
    cmd: command.RetrieveCasesByIdCommand,
    on_invalid_case_id: str = "raise",
) -> list[model.Case]:
    """Retrieve access-filtered cases by ID subject to case-type result limits.

    Inaccessible content columns are removed from returned cases. Invalid or
    unauthorized case IDs either raise or are ignored according to
    ``on_invalid_case_id``.

    Args:
        self: Case service handling the retrieval.
        cmd: Command containing case type and requested identifiers.
        on_invalid_case_id: Whether invalid requested IDs raise or are ignored.

    Returns:
        Accessible cases, truncated to the configured case-type limit.

    Raises:
        InvalidArgumentsError: If the case type is invalid or invalid-ID handling is
            unsupported.
        UnauthorizedAuthError: If requested cases are inaccessible and raising is
            configured.
    """
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

        cases, is_max_results_exceeded = self._retrieve_cases_with_content_right(
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

        case_types: list[model.CaseType] = self.repository.crud(
            uow,
            user.id,
            model.CaseType,
            CrudOperation.READ_SOME,
            obj_ids=[case_type_id],
        )
        if not case_types:
            raise exc.InvalidArgumentsError(
                "06f5019f", f"Invalid CaseType ID: {case_type_id}"
            )
        case_type = case_types[0]

        # Apply max results limit
        _raw = case_type.props.read_max_n_cases
        max_n_cases = _raw if _raw > 0 else self._default_props.read_max_n_cases
        if max_n_cases > 0 and len(cases) > max_n_cases:
            cases = cases[:max_n_cases]

    return cases


def _verify_case_filter(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    user: model.User,
    composite_filter: CompositeFilter,
) -> list[model.RefCol]:
    """Resolve filter metadata and validate concept and region members.

    Args:
        self: Case service used for metadata retrieval.
        uow: Active unit of work for column reads.
        user: User associated with reference-data commands.
        composite_filter: Content filter to validate.

    Returns:
        Reference columns in the same order as filter columns.

    Raises:
        InvalidArgumentsError: If a set-backed column uses a non-string-set filter or
            contains a member outside its configured domain.
    """
    # Retrieve Cols corresponding to filter keys
    filter_col_ids = composite_filter.get_keys()
    filter_cols: list[model.Col] = self.repository.crud(
        uow,
        user.id,
        model.Col,
        CrudOperation.READ_SOME,
        obj_ids=filter_col_ids,
    )
    # Retrieve cols for Cols
    ref_cols: list[model.RefCol] = self.repository.crud(
        uow,
        user.id,
        model.RefCol,
        CrudOperation.READ_SOME,
        obj_ids=list(
            {x.ref_col_id for x in filter_cols}
        ),  # TODO: consider READ_SOME allowing duplicate ids
    )
    ref_cols_map = {x.id: x for x in ref_cols}
    ref_cols = [ref_cols_map[x.ref_col_id] for x in filter_cols]
    # Verify filter validity
    concept_valid_values: dict[UUID, set[str]] = {}
    region_valid_values: dict[UUID, set[str]] = {}
    for col, ref_col, filter in zip(  # type: ignore[assignment]
        filter_cols, ref_cols, composite_filter.filters
    ):
        if ref_col.concept_set_id or ref_col.region_set_id:
            if isinstance(filter, StringSetFilter):
                validate_concept_or_region(
                    self,
                    user,
                    filter,
                    concept_valid_values,
                    region_valid_values,
                    col,
                    ref_col,
                )
            else:
                raise exc.InvalidArgumentsError(
                    "290ab290",
                    f"Column {col.id}: invalid filter type: {filter.__class__.__name__}",
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
    """Validate a StringSet filter against the ref column's concept or region set."""
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
    """Require every string-set filter member to belong to a valid domain.

    Args:
        stringset_filter: Filter whose members are validated case-insensitively.
        col: Column used to identify an invalid filter in the error.
        valid_values: Lowercase valid values for the column domain.

    Raises:
        InvalidArgumentsError: If any filter member is outside the valid domain.
    """
    invalid_values = [
        str(x) for x in stringset_filter.members if str(x).lower() not in valid_values
    ]
    if len(invalid_values):
        invalid_values_str = ", ".join(invalid_values)
        raise exc.InvalidArgumentsError(
            "b8527ecb",
            f"Column {col.id}: invalid {stringset_filter.__class__.__name__} filter members: {invalid_values_str}",
        )


def _get_valid_region_values(
    self: BaseCaseService,
    user: model.User,
    region_valid_values: dict[UUID, set[str]],
    ref_col: model.RefCol,
) -> set[str]:
    """Load and cache valid region IDs for a ref column's region set."""
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
    """Load and cache valid concept IDs for a ref column's concept set."""
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
    """Build value-normalization functions in the same order as filter columns."""
    # Check validity of filter and generate map_fns
    map_fns: list[Callable[[Any], Any]] = []
    for ref_col in ref_cols:
        _get_map_function_for_col(map_fns, ref_col)
    return map_fns


def _get_map_function_for_col(
    map_fns: list[Callable[[Any], Any]],
    ref_col: model.RefCol,
) -> None:
    """Append a value converter for one filter column type.

    Args:
        map_fns: Converter list to mutate in place.
        ref_col: Reference column determining conversion behavior.

    Raises:
        InvalidArgumentsError: If the column type has no supported converter.
    """
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
        raise exc.InvalidArgumentsError(
            "ab68605a", f"Unsupported column type: {ref_col.col_type}"
        )
