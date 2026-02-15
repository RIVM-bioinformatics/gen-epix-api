from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_retrieve_case_stats(
    self: BaseCaseService,
    cmd: command.RetrieveCaseStatsCommand,
) -> list[model.CaseStats]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    case_type_ids = cmd.case_type_ids

    with repository.uow() as uow:
        # @ABAC: check READ_CASE right on case types
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        read_case_type_ids = case_abac.get_case_types_with_access_right(
            enum.CaseRight.READ_CASE
        )
        if case_type_ids is None:
            # No case types provided -> use all case types with read access
            if case_abac.is_full_access:
                # All case types
                case_type_ids = set(
                    self.repository.crud(  # type: ignore[arg-type]
                        uow,
                        user.id,
                        model.CaseType,
                        None,
                        None,
                        CrudOperation.READ_ALL,
                        return_id=True,
                    )
                )
            else:
                case_type_ids = read_case_type_ids
        assert case_type_ids is not None
        if not case_abac.is_full_access:
            unauthorized_case_type_ids = case_type_ids - read_case_type_ids
            if unauthorized_case_type_ids:
                unauthorized_case_type_ids_str = ", ".join(
                    str(x) for x in unauthorized_case_type_ids
                )
                raise exc.UnauthorizedAuthError(
                    f"User {user.id} does not have READ_CASE right for case types: {unauthorized_case_type_ids_str}"
                )

        # Retrieve case sets if applicable
        case_type_case_set_ids_map: dict[UUID, set[UUID]] | None = None
        if cmd.case_set_ids is not None:
            # Get (case_set_id, case_type_id) tuples
            case_set_case_type_tuples: list[tuple[UUID, UUID]] = list(
                self.repository.read_fields(
                    uow,
                    user.id,
                    model.CaseSet,
                    ["id", "case_type_id"],
                    filter=UuidSetFilter(key="id", members=frozenset(cmd.case_set_ids)),
                )
            )
            # Check if all case sets are for allowed case types
            if any(x[1] not in case_type_ids for x in case_set_case_type_tuples):
                raise exc.UnauthorizedAuthError(
                    f"User {user.id} does not have READ_CASE right for all case sets provided"
                )
            # Map case type IDs to case set IDs
            case_type_case_set_ids_map = {}
            for case_set_id, case_type_id in case_set_case_type_tuples:
                case_type_case_set_ids_map.setdefault(case_type_id, set()).add(
                    case_set_id
                )
            # Restrict case types to those in the case sets
            case_type_ids = set(case_type_case_set_ids_map.keys())
        is_by_case_set = case_type_case_set_ids_map is not None
        if case_type_case_set_ids_map is None:
            case_type_case_set_ids_map = {}

        # Calculate case stats per case type or case set
        case_stats: list[model.CaseStats] = []
        for case_type_id in case_type_ids or []:
            # @ABAC: Get complete case type, which contains all necessary ABAC info
            sub_cmd = command.RetrieveCompleteCaseTypeCommand(
                user=user,
                case_type_id=case_type_id,
            )
            sub_cmd._policies.extend(cmd._policies)
            complete_case_type: model.CompleteCaseType = (
                self.retrieve_complete_case_type(sub_cmd)
            )

            # Special case: no user -> no access
            if cmd.user is None:
                case_stats.append(model.CaseStats(case_type_id=case_type_id))
                continue

            # Get private data collections for the user's organization for own case calculation
            private_data_collection_ids: set[UUID] = {
                x.data_collection_id
                for x in complete_case_type.case_type_access_abacs.values()
                if x.is_private
            }

            # Get readable data collections by highest resolution time unit
            data_collections_by_time_unit: dict[enum.ColType, set[UUID]] = {}
            is_handled_case_type_col_ids: set[UUID] = set()
            for col_type in enum.ColTypeOrder.TIME_RESOLUTION_DESC.value:
                case_type_col_id = complete_case_type.case_date_col_type_map.get(
                    col_type
                )
                if case_type_col_id is None:
                    # No case date column for this time unit
                    continue
                for (
                    data_collection_id,
                    case_type_access_abac,
                ) in complete_case_type.case_type_access_abacs.items():
                    read_case_type_col_ids = (
                        case_type_access_abac.read_case_type_col_ids
                    )
                    if read_case_type_col_ids & is_handled_case_type_col_ids:
                        # Case type column already handled at a higher resolution time unit
                        continue
                    data_collections_by_time_unit.setdefault(col_type, set()).add(
                        data_collection_id
                    )
                    is_handled_case_type_col_ids.add(case_type_col_id)

            # Retrieve case stats by case set if applicable
            if is_by_case_set:
                case_set_ids = case_type_case_set_ids_map.get(case_type_id, set())
                for case_set_id in case_set_ids:
                    # Get all cases in case set
                    case_ids: set[UUID] = {
                        x[0]
                        for x in self.repository.read_fields(
                            uow,
                            user.id,
                            model.CaseSetMember,
                            ["case_id"],
                            filter=EqualsUuidFilter(
                                key="case_set_id", value=case_set_id
                            ),
                        )
                    }
                    case_type_stat = self.repository.retrieve_case_stats(
                        uow,
                        case_type_id=case_type_id,
                        data_collections_by_time_unit=data_collections_by_time_unit,
                        private_data_collection_ids=private_data_collection_ids,
                        case_ids=case_ids,
                        datetime_range_filter=cmd.datetime_range_filter,
                    )
                    case_type_stat.case_set_id = case_set_id
                    case_stats.append(case_type_stat)
                continue

            # Retrieve case stats for entire case type
            case_type_stat = self.repository.retrieve_case_stats(
                uow,
                case_type_id=case_type_id,
                data_collections_by_time_unit=data_collections_by_time_unit,
                private_data_collection_ids=private_data_collection_ids,
                datetime_range_filter=cmd.datetime_range_filter,
            )
            case_stats.append(case_type_stat)

        return case_stats
