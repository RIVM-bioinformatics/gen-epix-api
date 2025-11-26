from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.util import map_paired_elements
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_retrieve_case_type_stats(
    self: BaseCaseService,
    cmd: command.RetrieveCaseTypeStatsCommand,
) -> list[model.CaseTypeStat]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    case_type_ids = cmd.case_type_ids

    # @ABAC: check READ_CASE right on case types
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    read_case_type_ids = case_abac.get_case_types_with_access_right(
        enum.CaseRight.READ_CASE
    )
    if case_type_ids is None:
        # No case types provided -> use all case types with read access
        case_type_ids = read_case_type_ids
    else:
        unauthorized_case_type_ids = case_type_ids - read_case_type_ids
        if unauthorized_case_type_ids:
            unauthorized_case_type_ids_str = ", ".join(
                str(x) for x in unauthorized_case_type_ids
            )
            raise exc.UnauthorizedAuthError(
                f"User {user.id} does not have READ_CASE right for case types: {unauthorized_case_type_ids_str}"
            )

    with repository.uow() as uow:

        # Get all case type settings
        case_type_settings_list: list[model.CaseTypeSettings] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeSettings,
            None,
            None,
            CrudOperation.READ_ALL,
            filter=UuidSetFilter(
                key="case_type_id",
                members=case_type_ids,
            ),
        )
        # Retrieve cases per case type settings and thus case type, and calculate stats
        case_type_stats: list[model.CaseTypeStat] = []
        for case_type_settings in case_type_settings_list:
            if case_type_settings.stats_time_case_type_col_id is None:
                # No time column defined, cannot calculate stats
                continue
            # Retrieve cases for case type
            case_type_id = case_type_settings.case_type_id
            cases: list[model.Case] = (
                self._retrieve_cases_with_content_right(  # type:ignore[attr-defined]
                    uow,
                    user.id,
                    case_abac,
                    # user_case_access,
                    enum.CaseRight.READ_CASE,
                    case_type_settings.case_type_id,
                    case_type_settings=case_type_settings,
                    datetime_range_filter=cmd.datetime_range_filter,
                )
            )
            # Calculate stats
            case_type_stat = model.CaseTypeStat(
                case_type_id=case_type_id,
                n_cases=sum(x.count for x in cases if x.count),
                first_case_date=min(
                    x.case_date for x in cases if x.case_date is not None
                ),
                last_case_date=max(
                    x.case_date for x in cases if x.case_date is not None
                ),
            )
            case_type_stats.append(case_type_stat)

    return case_type_stats


def case_service_retrieve_case_set_stats(
    self: BaseCaseService,
    cmd: command.RetrieveCaseSetStatsCommand,
) -> list[model.CaseSetStat]:
    user, repository = self._get_user_and_repository(cmd)
    case_set_ids = cmd.case_set_ids

    # TODO: adjust analogous to case_service_retrieve_case_type_stats:
    # - Read all case sets while checking access rights. RetrieveCaseSetStatsCommand.case_set_ids should be mandatory.
    # - Get unique case type ids from case sets
    # - Loop over case type ids and retrieve cases for all case sets of that case type
    # - Calculate stats per case set

    # TODO: update the code below as described above

    # Create filter, even if no case_set_ids are provided, to avoid unallowed read
    # all without filter
    query_filter: Filter | None = None
    if case_set_ids:
        query_filter = UuidSetFilter(
            key="case_set_id", members=cmd.case_set_ids  # type: ignore[arg-type]
        )
    with self.repository.uow() as uow:
        curr_cmd = command.CaseSetMemberCrudCommand(
            user=user,  # type: ignore[arg-type]
            operation=CrudOperation.READ_ALL,
            query_filter=query_filter,
        )
        curr_cmd._policies.extend(cmd._policies)
        case_set_members: list[model.CaseSetMember] = self.crud(curr_cmd)  # type: ignore[assignment]
        case_set_case_ids: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
            ((x.case_set_id, x.case_id) for x in case_set_members), as_set=True
        )
        if not case_set_ids:
            case_set_ids = list(case_set_case_ids.keys())
        # Get cases
        # @ABAC: case_set_case_ids is already filtered on cases with access, no
        # need to apply here again
        cases_: list[model.Case] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Case,
            None,
            list(set.union(set(), *list(case_set_case_ids.values()))),
            CrudOperation.READ_SOME,
        )
        cases = {x.id: x for x in cases_}
        # Create case set stats
        case_set_stats = []
        case_dates = {x.id: x.case_date for x in cases.values()}
        all_case_ids = set(cases.keys())
        for case_set_id in case_set_ids:
            case_ids = case_set_case_ids.get(case_set_id, set()).intersection(
                all_case_ids
            )
            # TODO: calculate n_own_cases as the number of cases with a created_in data collection that is associated with the user
            n_own_cases = 0
            first_case_month = (
                min(case_dates[x] for x in case_ids).isoformat()[0:7]
                if case_ids
                else None
            )
            last_case_month = (
                max(case_dates[x] for x in case_ids).isoformat()[0:7]
                if case_ids
                else None
            )
            case_set_stats.append(
                model.CaseSetStat(
                    case_set_id=case_set_id,
                    n_cases=len(case_ids),
                    n_own_cases=n_own_cases,
                    first_case_month=first_case_month,
                    last_case_month=last_case_month,
                )
            )

    return case_set_stats
