from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_date import (
    case_service_get_case_date_case_type_col_mappers,
)
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter import UuidSetFilter


def case_service_retrieve_complete_case_type(
    self: BaseCaseService,
    cmd: command.RetrieveCompleteCaseTypeCommand,
) -> model.CompleteCaseType:
    # TODO: many calls are inefficient,
    # retrieving first all objs and then filtering.
    # To be improved with e.g. CQS.
    user, repository = self._get_user_and_repository(cmd)
    assert user.id is not None

    with repository.uow() as uow:
        # Get case type
        case_type_id = cmd.case_type_id
        case_type: model.CaseType = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseType,
            None,
            case_type_id,
            CrudOperation.READ_ONE,
        )

        # @ABAC
        # Get allowed case type columns with any CRUD permission
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        case_type_access_abacs: dict[UUID, model.CaseTypeAccessAbac] = (
            case_abac.case_type_access_abacs.get(case_type_id, {})
        )
        case_type_share_abacs: dict[UUID, model.CaseTypeShareAbac] = (
            case_abac.case_type_share_abacs.get(case_type_id, {})
        )

        abac_case_type_col_ids: set[UUID]
        if case_abac.is_full_access:
            # Special case: full access -> all rights for all data collections for
            # this case type
            # TODO: consider if it should be limited to the union of all the
            # organization rights instead. A root user e.g. may then still have
            # full access by using the CRUD methods
            abac_case_type_col_ids = repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                model.CaseTypeCol,
                None,
                None,
                CrudOperation.READ_ALL,
                filter=UuidSetFilter(
                    key="case_type_id",
                    members=frozenset({case_type_id}),
                ),
                return_id=True,
            )
            abac_read_case_type_col_ids = abac_case_type_col_ids
            data_collection_ids: list[UUID] = self.app.handle(
                command.DataCollectionCrudCommand(
                    user=user,  # type: ignore[arg-type]
                    operation=CrudOperation.READ_ALL,
                    props={"return_id": True},
                )
            )
            case_type_access_abacs = {
                x: model.CaseTypeAccessAbac(
                    case_type_id=case_type_id,
                    data_collection_id=x,
                    is_private=True,
                    add_case=True,
                    remove_case=True,
                    read_case_type_col_ids=abac_case_type_col_ids,
                    write_case_type_col_ids=abac_case_type_col_ids,
                    add_case_set=True,
                    remove_case_set=True,
                    read_case_set=True,
                    write_case_set=True,
                )
                for x in data_collection_ids
            }
            # case_type_share_abacs can be empty since all rights are already in
            # case_type_access_abacs
            case_type_share_abacs = {}
        else:
            abac_case_type_col_ids = set()
            abac_read_case_type_col_ids = set()
            for x in case_type_access_abacs.values():
                abac_read_case_type_col_ids.update(x.read_case_type_col_ids)
                abac_case_type_col_ids.update(x.write_case_type_col_ids)
            abac_case_type_col_ids.update(abac_read_case_type_col_ids)

        # Get etiologies
        if case_type.disease_id:
            etiologies = self.app.handle(
                command.EtiologyCrudCommand(
                    user=user,  # type: ignore[arg-type]
                    operation=CrudOperation.READ_ALL,
                )
            )
            etiologies = {
                x.id: x for x in etiologies if x.disease_id == case_type.disease_id
            }
        else:
            etiologies = {}

        # Get etiological agents
        if etiologies:
            etiological_agent_ids = list(
                x.etiological_agent_id for x in etiologies.values()
            )
            etiological_agents = self.app.handle(
                command.EtiologicalAgentCrudCommand(
                    user=user,  # type: ignore[arg-type]
                    operation=CrudOperation.READ_SOME,
                    obj_ids=etiological_agent_ids,
                )
            )
            etiological_agents = {x.id: x for x in etiological_agents}
        else:
            etiological_agents = {}

        # Get allowed case_type_cols
        case_type_col_ids = list(abac_case_type_col_ids)
        case_type_cols_: list[model.CaseTypeCol] = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeCol,
            None,
            case_type_col_ids,
            CrudOperation.READ_SOME,
        )
        case_type_cols: dict[UUID, model.CaseTypeCol] = {
            x.id: x for x in case_type_cols_  # type: ignore[misc]
        }

        # Get cols
        col_ids = list({x.col_id for x in case_type_cols.values()})
        cols_: list[model.Col] = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            col_ids,
            CrudOperation.READ_SOME,
        )
        cols: dict[UUID, model.Col] = {x.id: x for x in cols_}  # type: ignore[misc]

        # Get dims
        dim_ids = list({x.dim_id for x in cols.values()})
        dims_: list[model.Dim] = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Dim,
            None,
            dim_ids,
            CrudOperation.READ_SOME,
        )
        dims: dict[UUID, model.Dim] = {x.id: x for x in dims_}  # type: ignore[misc]

        # Get case_type_col_order
        # TODO: to be tested
        max_dim_rank = max([0] + [x.rank for x in dims.values() if x.rank])
        max_col_rank = max([0] + [x.rank for x in cols.values() if x.rank])
        max_case_type_col_rank = max(
            [0] + [x.rank for x in case_type_cols.values() if x.rank]
        )
        max_case_type_col_occurrence = max(
            [0] + [x.occurrence for x in case_type_cols.values() if x.occurrence]
        )
        case_type_col_keys: dict[UUID, tuple[int, int, int]] = {
            x.id: (  # type: ignore[misc]
                x.rank if x.rank else max_case_type_col_rank,
                (
                    dims[cols[x.col_id].dim_id].rank
                    if dims[cols[x.col_id].dim_id].rank
                    else max_dim_rank
                ),
                (cols[x.col_id].rank if cols[x.col_id].rank else max_col_rank),
                x.occurrence if x.occurrence else max_case_type_col_occurrence,
            )
            for x in case_type_cols.values()
        }
        case_type_col_order = list(case_type_col_keys.keys())
        case_type_col_order.sort(key=lambda x: case_type_col_keys[x])

        # Get case_type_dims as the list ordered by the (dim, occurrence)
        # that occurs first in case_type_col_order
        dict_: dict[tuple[UUID, int | None], list] = {}
        # dict[tuple[dim_id, occurrence], list[rank, [tuple[case_type_col_id, col.rank]]]]
        for case_type_col_id in case_type_col_order:
            # Add to dict_
            case_type_col = case_type_cols[case_type_col_id]
            col = cols[case_type_col.col_id]
            tuple_ = (col.dim_id, case_type_col.occurrence)
            if tuple_ in dict_:
                dict_[tuple_][1].append((case_type_col_id, col.rank))
                continue
            dict_[tuple_] = [len(dict_), [(case_type_col_id, col.rank)]]
        case_type_dim_order = list(dict_.keys())
        case_type_dim_order.sort(key=lambda x: dict_[x][0])
        case_type_dims = [
            model.CaseTypeDim(
                id=x[0],
                dim_id=x[0],
                occurrence=x[1],
                rank=i + 1,
                case_type_col_order=[],
            )
            for i, x in enumerate(case_type_dim_order)
        ]
        for case_type_dim in case_type_dims:
            # Fill in id and case_type_col_order
            tuples = dict_[(case_type_dim.dim_id, case_type_dim.occurrence)][1]
            tuples.sort(key=lambda x: 1 if x[1] is None else x[1])
            case_type_dim.case_type_col_order = [x[0] for x in tuples]
            case_type_dim.id = case_type_dim.case_type_col_order[0]

        # Get genetic distance protocols
        genetic_distance_protocols = self.app.handle(
            command.GeneticDistanceProtocolCrudCommand(
                user=user,  # type: ignore[arg-type]
                operation=CrudOperation.READ_SOME,
                obj_ids=list(
                    {
                        x.genetic_distance_protocol_id
                        for x in cols.values()
                        if x.genetic_distance_protocol_id
                    }
                ),
            )
        )
        genetic_distance_protocols = {x.id: x for x in genetic_distance_protocols}

        # Get tree algorithms
        tree_algorithm_codes = set.union(
            set(),
            *[
                x.tree_algorithm_codes
                for x in case_type_cols.values()
                if x.tree_algorithm_codes
            ],
        )
        tree_algorithms = self.app.handle(
            command.TreeAlgorithmCrudCommand(
                user=user,  # type: ignore[arg-type]
                operation=CrudOperation.READ_ALL,
            )
        )
        tree_algorithms = {
            x.code: x for x in tree_algorithms if x.code in tree_algorithm_codes
        }

        # Get case type settings if it exists
        has_case_type_settings: bool = self.app.handle(
            command.CaseTypeSettingsCrudCommand(
                user=user,  # type: ignore[arg-type]
                operation=CrudOperation.EXISTS_ONE,
                obj_ids=case_type_id,
            )
        )
        if has_case_type_settings:
            case_type_settings: model.CaseTypeSettings = self.app.handle(
                command.CaseTypeSettingsCrudCommand(
                    user=user,  # type: ignore[arg-type]
                    operation=CrudOperation.READ_ONE,
                    obj_ids=case_type_id,
                )
            )
        else:
            # Create default case type settings
            case_type_settings = model.CaseTypeSettings(
                case_type_id=case_type_id,
                stats_time_case_type_col_id=None,
                stats_geo_case_type_col_id=None,
                create_max_n_cases=self._default_create_max_n_cases,
                read_max_n_cases=self._default_read_max_n_cases,
                read_max_tree_size=self._default_read_max_tree_size,
                update_max_n_cases=self._default_update_max_n_cases,
                delete_max_n_cases=self._default_delete_max_n_cases,
            )

        # Get stats_time_case_type_col_ids
        if not case_type_settings.stats_time_case_type_col_id:
            stats_time_case_type_col_ids = None
            stats_time_case_type_col_id = None
        else:
            case_date_case_type_col_mappers = case_service_get_case_date_case_type_col_mappers(
                self=self,
                uow=uow,
                user_id=user.id,
                case_type_id=case_type_id,
                stats_time_case_type_col_id=case_type_settings.stats_time_case_type_col_id,
            )
            stats_time_case_type_col_ids = [
                x
                for x in case_date_case_type_col_mappers.keys()
                if x in abac_read_case_type_col_ids
            ]
            stats_time_case_type_col_id = (
                case_type_settings.stats_time_case_type_col_id
                if case_type_settings.stats_time_case_type_col_id
                in abac_read_case_type_col_ids
                else (
                    stats_time_case_type_col_ids[0]
                    if stats_time_case_type_col_ids
                    else None
                )
            )

        # Get stats_geo_case_type_col_ids
        stats_geo_case_type_col_ids: list[UUID] | None
        if case_type_settings.stats_geo_case_type_col_id is None:
            stats_geo_case_type_col_ids = None
            stats_geo_case_type_col_id = None
        else:
            # Get all case type cols in the same (dim, occurrence) as stats_geo_case_type_col_id
            stats_geo_case_type_col = case_type_cols[
                case_type_settings.stats_geo_case_type_col_id
            ]
            stats_geo_col = cols[stats_geo_case_type_col.col_id]
            dim_id = stats_geo_col.dim_id
            occurrence = stats_geo_case_type_col.occurrence
            case_type_cols_same_dim_occurrence = [
                x
                for x in case_type_cols.values()
                if cols[x.col_id].dim_id == dim_id
                and x.occurrence == occurrence
                and cols[x.col_id].col_type in model.enum.ColTypeSet.GEO.value
            ]
            stats_geo_case_type_col_ids = [  # type: ignore[assignment]
                x.id
                for x in case_type_cols_same_dim_occurrence
                if x.id in abac_read_case_type_col_ids
            ]
            stats_geo_case_type_col_id = (
                case_type_settings.stats_geo_case_type_col_id
                if case_type_settings.stats_geo_case_type_col_id
                in abac_read_case_type_col_ids
                else (
                    stats_geo_case_type_col_ids[0]
                    if stats_geo_case_type_col_ids
                    else None
                )
            )

    # Compose complete case type and return
    return model.CompleteCaseType(
        **case_type.model_dump(),
        etiologies=etiologies,
        etiological_agents=etiological_agents,
        dims=dims,
        cols=cols,
        case_type_dims=case_type_dims,
        case_type_cols=case_type_cols,
        case_type_col_order=case_type_col_order,
        genetic_distance_protocols=genetic_distance_protocols,
        tree_algorithms=tree_algorithms,
        case_type_access_abacs=case_type_access_abacs,
        case_type_share_abacs=case_type_share_abacs,
        stats_time_case_type_col_id=stats_time_case_type_col_id,
        stats_geo_case_type_col_id=stats_geo_case_type_col_id,
        stats_time_case_type_col_ids=stats_time_case_type_col_ids,
        stats_geo_case_type_col_ids=stats_geo_case_type_col_ids,
        create_max_n_cases=case_type_settings.create_max_n_cases,
        read_max_n_cases=case_type_settings.read_max_n_cases,
        read_max_tree_size=case_type_settings.read_max_tree_size,
        update_max_n_cases=case_type_settings.update_max_n_cases,
        delete_max_n_cases=case_type_settings.delete_max_n_cases,
    )
