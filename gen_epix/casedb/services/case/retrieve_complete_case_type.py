from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.domain.repository.case import BaseCaseRepository
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
    repository: BaseCaseRepository = self.repository
    user = cmd.user
    user_id: UUID | None = None if user is None else user.id

    with repository.uow() as uow:
        # Get case type
        case_type_id = cmd.case_type_id
        case_type: model.CaseType = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.CaseType,
            None,
            case_type_id,
            CrudOperation.READ_ONE,
        )

        # @ABAC
        # Get allowed case type columns with any CRUD permission
        case_abac: model.CaseAbac | None
        case_type_access_abacs: dict[UUID, model.CaseTypeAccessAbac]
        case_type_share_abacs: dict[UUID, model.CaseTypeShareAbac]
        abac_case_type_col_ids: set[UUID]
        abac_read_case_type_col_ids: set[UUID]
        if cmd.user is None:
            # Special case: no user -> treated as full access (actual ABAC still applies, which will require a valid user later)
            case_abac = model.CaseAbac(
                case_type_access_abacs={},
                case_type_share_abacs={},
                is_full_access=True,
            )
        else:
            case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
            assert case_abac is not None
        if case_abac.is_full_access:
            # Special case: full access -> all rights for all data collections for
            # this case type
            # TODO: consider if it should be limited to the union of all the
            # organization rights instead. A root user e.g. may then still have
            # full access by using the CRUD methods
            abac_case_type_col_ids = repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
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
                    user=user,
                    operation=CrudOperation.READ_ALL,
                    props={"return_id": True},
                )
            )
            case_type_access_abacs = {
                x: model.CaseTypeAccessAbac(
                    case_type_id=case_type_id,
                    data_collection_id=x,
                    # TODO: is_private should be determined properly
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
            case_type_access_abacs = case_abac.case_type_access_abacs.get(
                case_type_id, {}
            )
            case_type_share_abacs = case_abac.case_type_share_abacs.get(
                case_type_id, {}
            )
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
                    user=user,
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
                    user=user,
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
            user_id,
            model.CaseTypeCol,
            None,
            case_type_col_ids,
            CrudOperation.READ_SOME,
        )
        case_type_col_map: dict[UUID, model.CaseTypeCol] = {
            x.id: x for x in case_type_cols  # type: ignore[misc]
        }

        # Get allowed case_type_dims as the case_type_dims used by the allowed
        # case_type_cols
        case_type_dim_ids: list[UUID] = list(
            {x.case_type_dim_id for x in case_type_cols}
        )
        case_type_dims: list[model.CaseTypeDim] = repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.CaseTypeDim,
            None,
            case_type_dim_ids,
            CrudOperation.READ_SOME,
        )
        case_type_dim_map: dict[UUID, model.CaseTypeDim] = {
            x.id: x for x in case_type_dims  # type: ignore[misc]
        }

        # Get cols
        ref_col_ids = list({x.ref_col_id for x in case_type_cols})
        ref_cols: list[model.RefCol] = repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.RefCol,
            None,
            ref_col_ids,
            CrudOperation.READ_SOME,
        )
        ref_col_map: dict[UUID, model.RefCol] = {x.id: x for x in ref_cols}  # type: ignore[misc]

        # Get dims
        ref_dim_ids = list({x.ref_dim_id for x in ref_cols})
        ref_dims: list[model.RefDim] = repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.RefDim,
            None,
            ref_dim_ids,
            CrudOperation.READ_SOME,
        )
        ref_dim_map: dict[UUID, model.RefDim] = {x.id: x for x in ref_dims}  # type: ignore[misc]

        # Get genetic distance protocols
        genetic_distance_protocols = self.app.handle(
            command.GeneticDistanceProtocolCrudCommand(
                user=user,
                operation=CrudOperation.READ_SOME,
                obj_ids=list(
                    {
                        x.genetic_distance_protocol_id
                        for x in ref_cols
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
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        tree_algorithms = {
            x.code: x for x in tree_algorithms if x.code in tree_algorithm_codes
        }

        # Derive stats_time_case_type_dim_id from CaseTypeDim.is_time
        case_date_case_type_dim_id: UUID | None = None
        for case_type_dim in case_type_dims:
            if case_type_dim.is_case_date_dim:
                case_date_case_type_dim_id = case_type_dim.id
                break
            # TODO: add geo_case_type_dim flag if needed

        # Compose complete case type and return
        return model.CompleteCaseType(
            **case_type.model_dump(),
            user_id=cmd.user.id if cmd.user else None,
            etiologies=etiologies,
            etiological_agents=etiological_agents,
            ref_dims=ref_dim_map,
            ref_cols=ref_col_map,
            case_type_dims=case_type_dim_map,
            case_type_cols=case_type_col_map,
            genetic_distance_protocols=genetic_distance_protocols,
            tree_algorithms=tree_algorithms,
            case_type_access_abacs=case_type_access_abacs,
            case_type_share_abacs=case_type_share_abacs,
            case_date_case_type_dim_id=case_date_case_type_dim_id,
        )
