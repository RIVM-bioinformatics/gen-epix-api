"""Calculate access-aware case statistics by case type or case set."""

from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_retrieve_case_stats(
    self: BaseCaseService,
    cmd: command.RetrieveCaseTypeStatsCommand | command.RetrieveCaseSetStatsCommand,
) -> list[model.CaseStats]:
    """Calculate case statistics restricted by case and date-column access.

    Case types are limited to those with READ_CASE access. For each case type, date
    resolution is selected per data collection from the highest-resolution readable
    case-date column. Case-set requests additionally restrict cases to requested sets.

    Args:
        self: Case service handling the statistics request.
        cmd: Case-type or case-set statistics command.

    Returns:
        Statistics for each accessible requested case type or case set.

    Raises:
        UnauthorizedAuthError: If the user lacks READ_CASE access to any requested
            case type or to the case type of any requested case set.
    """
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    with repository.uow() as uow:
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        read_case_type_ids = case_abac.get_case_types_with_access_right(
            enum.CaseRight.READ_CASE
        )
        case_type_ids = _get_accessible_case_type_ids(
            self, uow, user.id, cmd, case_abac.is_full_access, read_case_type_ids
        )
        case_type_case_set_ids_map = _get_case_set_ids_by_case_type(
            self, uow, user.id, cmd, case_type_ids
        )
        case_stats: list[model.CaseStats] = []
        for case_type_id in case_type_ids:
            case_stats.extend(
                _retrieve_case_type_stats(
                    self,
                    uow,
                    user,
                    cmd,
                    case_type_id,
                    case_type_case_set_ids_map,
                )
            )

        return case_stats


def _get_accessible_case_type_ids(
    service: BaseCaseService,
    uow: object,
    user_id: UUID,
    cmd: command.RetrieveCaseTypeStatsCommand | command.RetrieveCaseSetStatsCommand,
    is_full_access: bool,
    read_case_type_ids: set[UUID],
) -> set[UUID]:
    """Resolve requested case types and enforce READ_CASE access."""
    if (
        isinstance(cmd, command.RetrieveCaseTypeStatsCommand)
        and cmd.case_type_ids is not None
    ):
        case_type_ids = cmd.case_type_ids
    elif is_full_access:
        case_type_ids = set(
            service.repository.crud(
                uow,
                user_id,
                model.CaseType,
                CrudOperation.READ_ALL,
                return_id=True,
            )
        )
    else:
        case_type_ids = read_case_type_ids
    if not is_full_access:
        unauthorized_ids = case_type_ids - read_case_type_ids
        if unauthorized_ids:
            unauthorized_ids_str = ", ".join(str(item) for item in unauthorized_ids)
            raise exc.UnauthorizedAuthError(
                "e70d1344",
                f"User {user_id} does not have READ_CASE right for CaseTypes: {unauthorized_ids_str}",
            )
    return case_type_ids


def _get_case_set_ids_by_case_type(
    service: BaseCaseService,
    uow: object,
    user_id: UUID,
    cmd: command.RetrieveCaseTypeStatsCommand | command.RetrieveCaseSetStatsCommand,
    case_type_ids: set[UUID],
) -> dict[UUID, set[UUID]] | None:
    """Read requested case sets, enforce access, and group IDs by case type."""
    if (
        not isinstance(cmd, command.RetrieveCaseSetStatsCommand)
        or cmd.case_set_ids is None
    ):
        return None
    case_set_case_type_tuples: list[tuple[UUID, UUID]] = list(
        service.repository.read_fields(
            uow,
            user_id,
            model.CaseSet,
            ["id", "case_type_id"],
            filter=UuidSetFilter(key="id", members=frozenset(cmd.case_set_ids)),
        )
    )
    if any(
        case_type_id not in case_type_ids
        for _, case_type_id in case_set_case_type_tuples
    ):
        raise exc.UnauthorizedAuthError(
            "67dc2ef5",
            f"User {user_id} does not have READ_CASE right for all case sets provided",
        )
    case_type_case_set_ids_map: dict[UUID, set[UUID]] = {}
    for case_set_id, case_type_id in case_set_case_type_tuples:
        case_type_case_set_ids_map.setdefault(case_type_id, set()).add(case_set_id)
    return case_type_case_set_ids_map


def _get_data_collections_by_time_unit(
    complete_case_type: model.CompleteCaseType,
) -> dict[enum.ColType, set[UUID]]:
    """Select each data collection's highest-resolution readable date column."""
    data_collections_by_time_unit: dict[enum.ColType, set[UUID]] = {}
    handled_data_collection_ids: set[UUID] = set()
    for col_type in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value:
        col_id = complete_case_type.case_date_col_type_map.get(col_type)
        if col_id is None:
            continue
        for (
            data_collection_id,
            access_abac,
        ) in complete_case_type.case_type_access_abacs.items():
            if data_collection_id in handled_data_collection_ids:
                continue
            if col_id not in access_abac.read_col_ids:
                continue
            data_collections_by_time_unit.setdefault(col_type, set()).add(
                data_collection_id
            )
            handled_data_collection_ids.add(data_collection_id)
    return data_collections_by_time_unit


def _retrieve_case_type_stats(
    service: BaseCaseService,
    uow: object,
    user: model.User,
    cmd: command.RetrieveCaseTypeStatsCommand | command.RetrieveCaseSetStatsCommand,
    case_type_id: UUID,
    case_type_case_set_ids_map: dict[UUID, set[UUID]] | None,
) -> list[model.CaseStats]:
    """Retrieve statistics for one case type or its requested case sets."""
    sub_cmd = command.RetrieveCompleteCaseTypeCommand(
        user=user,
        case_type_id=case_type_id,
    )
    sub_cmd._policies.extend(cmd._policies)
    complete_case_type: model.CompleteCaseType = service.retrieve_complete_case_type(
        sub_cmd
    )
    if cmd.user is None:
        return [model.CaseStats(case_type_id=case_type_id)]

    private_data_collection_ids = {
        access_abac.data_collection_id
        for access_abac in complete_case_type.case_type_access_abacs.values()
        if access_abac.is_private
    }
    data_collections_by_time_unit = _get_data_collections_by_time_unit(
        complete_case_type
    )
    if case_type_case_set_ids_map is not None:
        return _retrieve_case_set_stats(
            service,
            uow,
            user,
            cmd,
            case_type_id,
            case_type_case_set_ids_map.get(case_type_id, set()),
            data_collections_by_time_unit,
            private_data_collection_ids,
        )
    return [
        service.repository.retrieve_case_stats(
            uow,
            case_type_id=case_type_id,
            data_collections_by_time_unit=data_collections_by_time_unit,
            private_data_collection_ids=private_data_collection_ids,
            datetime_range_filter=cmd.datetime_range_filter,
        )
    ]


def _retrieve_case_set_stats(
    service: BaseCaseService,
    uow: object,
    user: model.User,
    cmd: command.RetrieveCaseTypeStatsCommand | command.RetrieveCaseSetStatsCommand,
    case_type_id: UUID,
    case_set_ids: set[UUID],
    data_collections_by_time_unit: dict[enum.ColType, set[UUID]],
    private_data_collection_ids: set[UUID],
) -> list[model.CaseStats]:
    """Retrieve statistics for each case set of a case type."""
    case_stats = []
    for case_set_id in case_set_ids:
        case_ids: set[UUID] = {
            row[0]
            for row in service.repository.read_fields(
                uow,
                user.id,
                model.CaseSetMember,
                ["case_id"],
                filter=EqualsUuidFilter(key="case_set_id", value=case_set_id),
            )
        }
        case_type_stat = service.repository.retrieve_case_stats(
            uow,
            case_type_id=case_type_id,
            data_collections_by_time_unit=data_collections_by_time_unit,
            private_data_collection_ids=private_data_collection_ids,
            case_ids=case_ids,
            datetime_range_filter=cmd.datetime_range_filter,
        )
        case_type_stat.case_set_id = case_set_id
        case_stats.append(case_type_stat)
    return case_stats
