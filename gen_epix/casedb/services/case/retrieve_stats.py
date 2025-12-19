import datetime
from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.base import Filter
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.util import map_paired_elements


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
        if case_abac.is_full_access:
            with repository.uow() as uow:
                case_type_ids = self.repository.crud(
                    uow,
                    user.id,
                    model.CaseType,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    return_id=True,
                )
        else:
            case_type_ids = read_case_type_ids
    elif not case_abac.is_full_access:
        unauthorized_case_type_ids = case_type_ids - read_case_type_ids
        if unauthorized_case_type_ids:
            unauthorized_case_type_ids_str = ", ".join(
                str(x) for x in unauthorized_case_type_ids
            )
            raise exc.UnauthorizedAuthError(
                f"User {user.id} does not have READ_CASE right for case types: {unauthorized_case_type_ids_str}"
            )

    with repository.uow() as uow:

        # Retrieve cases per case type settings and thus case type, and calculate stats
        case_type_stats: list[model.CaseTypeStat] = []
        for case_type_id in case_type_ids:
            cases: list[model.Case] = self._retrieve_cases_with_content_right(
                uow,
                user.id,
                case_abac,
                enum.CaseRight.READ_CASE,
                case_type_id,
                datetime_range_filter=cmd.datetime_range_filter,
                calculate_case_date=True,
                apply_max_n_cases=False,
            )
            # Calculate stats
            case_dates = [x.case_date for x in cases if x.case_date is not None]
            case_type_stat = model.CaseTypeStat(
                case_type_id=case_type_id,
                n_cases=(
                    sum(1 if x.count is None else x.count for x in cases)
                    if cases
                    else 0
                ),
                first_case_date=min(case_dates) if case_dates else None,
                last_case_date=max(case_dates) if case_dates else None,
            )
            case_type_stats.append(case_type_stat)

    return case_type_stats


def case_service_retrieve_case_set_stats(
    self: BaseCaseService,
    cmd: command.RetrieveCaseSetStatsCommand,
) -> list[model.CaseSetStat]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    # Handle transaction
    case_set_stats = []
    with repository.uow() as uow:
        curr_cmd: command.Command

        # @ABAC: retrieve case sets: this applies ABAC filtering on case sets and,
        # in case case_set_ids are provided, raises an error on unauthorized case
        # sets. In addition it retrieves the list of case set IDs in case not
        # explicitly provided.
        case_set_query_filter: Filter | None = None
        if cmd.case_set_ids:
            case_set_query_filter = UuidSetFilter(
                key="id", members=cmd.case_set_ids  # type: ignore[arg-type]
            )
        curr_cmd = command.CaseSetCrudCommand(
            user=user,
            operation=CrudOperation.READ_ALL,
            query_filter=case_set_query_filter,
        )
        curr_cmd._policies.extend(cmd._policies)
        case_sets: list[model.CaseSet] = self.crud(curr_cmd)  # type: ignore[assignment]
        case_set_ids: set[UUID] = {x.id for x in case_sets}  # type: ignore[misc]

        # Retrieve case set members
        # @ABAC: cases retrieved here are filtered on cases with access
        case_set_member_query_filter = UuidSetFilter(
            key="case_set_id", members=case_set_ids  # type: ignore[arg-type]
        )
        curr_cmd = command.CaseSetMemberCrudCommand(
            user=user,
            operation=CrudOperation.READ_ALL,
            query_filter=case_set_member_query_filter,
        )
        curr_cmd._policies.extend(cmd._policies)
        case_set_members: list[model.CaseSetMember] = self.crud(curr_cmd)  # type: ignore[assignment]
        case_set_case_ids: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
            ((x.case_set_id, x.case_id) for x in case_set_members), as_set=True
        )
        if not case_set_ids:
            case_set_ids = set(case_set_case_ids.keys())

        # Retrieve private data collections for the user's organization for own case calculation
        curr_cmd = command.OrganizationAccessCasePolicyCrudCommand(
            user=user,
            operation=CrudOperation.READ_ALL,
            query_filter=EqualsUuidFilter(
                key="organization_id", value=user.organization_id
            ),
        )
        curr_cmd._policies.extend(cmd._policies)
        policies: list[model.OrganizationAccessCasePolicy] = self.app.handle(curr_cmd)
        private_data_collection_ids: set[UUID] = {x.id for x in policies if x.is_private}  # type: ignore[misc]

        # Retrieve case dates and whether the case is an own case
        # @ABAC: case_set_case_ids is already filtered on cases with access, no
        # need to apply here again, but case_date calculation requires ABAC as well
        case_type_ids: set[UUID] = {x.case_type_id for x in case_sets}
        case_props_map: dict[UUID, tuple[datetime.datetime, bool]] = {}
        for case_type_id in case_type_ids:
            curr_case_set_ids: set[UUID] = {x.id for x in case_sets if x.case_type_id == case_type_id}  # type: ignore[misc]
            curr_case_ids = set.union(
                *[case_set_case_ids[x] for x in curr_case_set_ids]
            )
            curr_cmd = command.RetrieveCasesByIdCommand(
                user=user, case_type_id=case_type_id, case_ids=list(curr_case_ids)
            )
            curr_cmd._policies.extend(cmd._policies)
            curr_cases: list[model.Case] = self.app.handle(curr_cmd)
            curr_case_props_map: dict[UUID, tuple[datetime.datetime, bool]] = {
                x.id: (  # type: ignore[arg-type]
                    x.case_date,
                    x.created_in_data_collection_id in private_data_collection_ids,
                )
                for x in curr_cases
            }
            case_props_map.update(curr_case_props_map)

        # Create case set stats
        for case_set in case_sets:
            case_set_id: UUID = case_set.id  # type: ignore[assignment]
            case_ids = case_set_case_ids.get(case_set_id, set())

            # Special case: no cases in case set
            if not case_ids:
                case_set_stats.append(
                    model.CaseSetStat(
                        case_set_id=case_set_id,
                        n_cases=0,
                        n_own_cases=0,
                        first_case_date=None,
                        last_case_date=None,
                    )
                )
                continue

            # Calculate stats
            n_own_cases = sum(case_props_map[x][1] for x in case_ids)
            first_case_date = min(case_props_map[x][0] for x in case_ids)
            last_case_date = max(case_props_map[x][0] for x in case_ids)
            case_set_stats.append(
                model.CaseSetStat(
                    case_set_id=case_set_id,
                    n_cases=len(case_ids),
                    n_own_cases=n_own_cases,
                    first_case_date=first_case_date,
                    last_case_date=last_case_date,
                )
            )

    return case_set_stats
