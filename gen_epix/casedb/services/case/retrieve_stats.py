from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.util import map_paired_elements
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.base import Filter
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_retrieve_case_type_stats(
    self: BaseCaseService,
    cmd: command.RetrieveCaseTypeStatsCommand,
) -> list[model.CaseTypeStat]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    case_type_ids = cmd.case_type_ids
    with repository.uow() as uow:
        cases: list[model.Case] = (
            self._retrieve_cases_with_content_right(  # type:ignore[attr-defined]
                uow,
                user.id,
                case_abac,
                # user_case_access,
                enum.CaseRight.READ_CASE,
                datetime_range_filter=cmd.datetime_range_filter,
                filter_content=False,
            )
        )
        if case_type_ids is not None:
            cases = [x for x in cases if x.case_type_id in case_type_ids]
        else:
            case_type_ids = {x.case_type_id for x in cases}
        # Derive stats
        empty_stat = {
            "n_cases": 0,
            "first_case_month": None,
            "last_case_month": None,
        }
        stats = {x: dict(empty_stat) for x in case_type_ids}
        for case in cases:
            case_type_id = case.case_type_id
            date_ = case.case_date
            stat = stats[case_type_id]
            if stat["n_cases"] == 0:
                stat["n_cases"] = 1
                stat["first_case_month"] = date_  # type: ignore[assignment]
                stat["last_case_month"] = date_  # type: ignore[assignment]
            else:
                stat["n_cases"] += 1  # type:ignore[operator]
                stat["first_case_month"] = min(stat["first_case_month"], date_)  # type: ignore[type-var,assignment]
                stat["last_case_month"] = max(stat["last_case_month"], date_)  # type: ignore[type-var,assignment]
        # Convert first/last date to month only
        for stat in stats.values():
            for key in ("first_case_month", "last_case_month"):
                stat[key] = stat[key].isoformat()[0:7]  # type: ignore[union-attr]
        # Get case type stats
        case_type_stats = [
            model.CaseTypeStat(case_type_id=x, **stats[x]) for x in case_type_ids  # type: ignore[arg-type]
        ]
    return case_type_stats


def case_service_retrieve_case_set_stats(
    self: BaseCaseService,
    cmd: command.RetrieveCaseSetStatsCommand,
) -> list[model.CaseSetStat]:
    user, repository = self._get_user_and_repository(cmd)
    case_set_ids = cmd.case_set_ids
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
