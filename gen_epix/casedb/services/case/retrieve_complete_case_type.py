from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
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
            abac_read_case_type_col_ids: set[UUID] = set()
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
        case_type_cols: list[model.CaseTypeCol] = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeCol,
            None,
            case_type_col_ids,
            CrudOperation.READ_SOME,
        )
        case_type_dim_ids: list[UUID] = [x.case_type_dim_id for x in case_type_cols]
        case_type_col_map: dict[UUID, model.CaseTypeCol] = {
            x.id: x for x in case_type_cols  # type: ignore[misc]
        }

        case_type_dims: list[model.CaseTypeDim] = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeDim,
            None,
            case_type_dim_ids,
            CrudOperation.READ_SOME,
        )
        case_type_dim_map: dict[UUID, model.CaseTypeDim] = {
            x.id: x for x in case_type_dims  # type: ignore[misc]
        }

        # Get cols
        col_ids = list({x.col_id for x in case_type_cols})
        cols: list[model.Col] = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            col_ids,
            CrudOperation.READ_SOME,
        )
        col_map: dict[UUID, model.Col] = {x.id: x for x in cols}  # type: ignore[misc]

        # Get dims
        dim_ids = list({x.dim_id for x in cols})
        dims: list[model.Dim] = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Dim,
            None,
            dim_ids,
            CrudOperation.READ_SOME,
        )
        dim_map: dict[UUID, model.Dim] = {x.id: x for x in dims}  # type: ignore[misc]

        # Get case_type_col_order

        # TODO: to be tested
        case_type_col_sort_keys: dict[UUID, tuple[int, int]] = {
            x.id: (  # type: ignore[misc]
                case_type_dim_map[x.case_type_dim_id].rank,
                x.rank,
            )
            for x in case_type_cols
        }
        ordered_case_type_col_ids = list(case_type_col_sort_keys.keys())
        ordered_case_type_col_ids.sort(key=lambda x: case_type_col_sort_keys[x])

        # Get genetic distance protocols
        genetic_distance_protocols = self.app.handle(
            command.GeneticDistanceProtocolCrudCommand(
                user=user,  # type: ignore[arg-type]
                operation=CrudOperation.READ_SOME,
                obj_ids=list(
                    {
                        x.genetic_distance_protocol_id
                        for x in cols
                        if x.genetic_distance_protocol_id
                    }
                ),
            )
        )
        genetic_distance_protocols = {x.id: x for x in genetic_distance_protocols}

        # Get tree algorithms
        tree_algorithm_codes: set[enum.TreeAlgorithmType] = set.union(
            set(),
            *[x.tree_algorithm_codes for x in case_type_cols if x.tree_algorithm_codes],
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

        # derrive stats_time_case_type_dim_id from CaseTypeDim.is_time
        stats_time_case_type_dim_id: UUID | None = None
        stats_geo_case_type_dim_id: UUID | None = None
        for case_type_dim in case_type_dims:
            if case_type_dim.is_case_date_dim:
                stats_time_case_type_dim_id = case_type_dim.id
                break
            # TODO: add geo case type dim flag if needed

    # Compose complete case type and return
    return model.CompleteCaseType(
        **case_type.model_dump(),
        etiologies=etiologies,
        etiological_agents=etiological_agents,
        dims=dim_map,
        cols=col_map,
        case_type_dims=case_type_dim_map,
        case_type_cols=case_type_col_map,
        ordered_case_type_col_ids=ordered_case_type_col_ids,
        genetic_distance_protocols=genetic_distance_protocols,
        tree_algorithms=tree_algorithms,
        case_type_access_abacs=case_type_access_abacs,
        case_type_share_abacs=case_type_share_abacs,
        create_max_n_cases=case_type.create_max_n_cases,
        read_max_n_cases=case_type.read_max_n_cases,
        read_max_tree_size=case_type.read_max_tree_size,
        update_max_n_cases=case_type.update_max_n_cases,
        delete_max_n_cases=case_type.delete_max_n_cases,
        stats_time_case_type_dim_id=stats_time_case_type_dim_id,
        stats_geo_case_type_dim_id=stats_geo_case_type_dim_id,
    )
