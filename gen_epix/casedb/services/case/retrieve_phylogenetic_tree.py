from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation


def case_service_retrieve_phylogenetic_tree(
    self: BaseCaseService, cmd: command.RetrievePhylogeneticTreeByCasesCommand
) -> model.PhylogeneticTree:
    dist_case_type_col_id = cmd.genetic_distance_case_type_col_id
    tree_algorithm_code = cmd.tree_algorithm
    case_ids = cmd.case_ids
    user: model.User
    user, repository = self._get_user_and_repository(cmd)  # type: ignore[assignment]
    assert isinstance(user, model.User) and user.id is not None
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    with repository.uow() as uow:
        # Get distance column data
        dist_case_type_col: model.CaseTypeCol = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeCol,
            None,
            dist_case_type_col_id,
            CrudOperation.READ_ONE,
        )
        case_type_id = dist_case_type_col.case_type_id
        dist_col: model.Col = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            dist_case_type_col.col_id,
            CrudOperation.READ_ONE,
        )
        if dist_col.col_type != enum.ColType.GENETIC_DISTANCE:
            raise exc.InvalidArgumentsError(
                f"Case type column {dist_case_type_col_id} is not of type {enum.ColType.GENETIC_DISTANCE.value}"
            )
        # Get sequence column data
        seq_case_type_col_id = dist_case_type_col.genetic_sequence_case_type_col_id
        if not seq_case_type_col_id:
            raise exc.InvalidArgumentsError(
                f"Case type column {dist_case_type_col_id} has no associated sequence column"
            )

        # @ABAC
        assert dist_case_type_col.tree_algorithm_codes is not None
        if tree_algorithm_code not in dist_case_type_col.tree_algorithm_codes:
            raise exc.UnauthorizedAuthError(
                f"User {user.id} has no read access to tree algorithm {tree_algorithm_code}"
            )

        # Get genetic distance protocol
        genetic_distance_protocol: model.GeneticDistanceProtocol = (
            self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                model.GeneticDistanceProtocol,
                None,
                dist_col.genetic_distance_protocol_id,
                CrudOperation.READ_ONE,
            )
        )
        seqdb_seq_distance_protocol_id = (
            genetic_distance_protocol.seqdb_seq_distance_protocol_id
        )

        # Special case: zero case_ids
        if not case_ids:
            retval: model.PhylogeneticTree = self.app.handle(
                command.RetrievePhylogeneticTreeBySequencesCommand(
                    user=user,
                    tree_algorithm_code=tree_algorithm_code,
                    seqdb_seq_distance_protocol_id=seqdb_seq_distance_protocol_id,
                    sequence_ids=[],
                )
            )
            retval.genetic_distance_protocol_id = genetic_distance_protocol.id
            return retval

        # Create temporary case_abac only for this case type and the
        # seq_case_type_col_id having the same rights as the dist_case_type_col
        temp_case_abac = model.CaseAbac(
            is_full_access=case_abac.is_full_access,
            case_type_access_abacs={},
            case_type_share_abacs={},
        )
        for data_collection_id, x in case_abac.case_type_access_abacs.get(
            case_type_id, {}
        ).items():
            if dist_case_type_col_id not in x.read_case_type_col_ids:
                continue
            if case_type_id not in temp_case_abac.case_type_access_abacs:
                temp_case_abac.case_type_access_abacs[case_type_id] = {}
            temp_case_abac.case_type_access_abacs[case_type_id][data_collection_id] = (
                model.CaseTypeAccessAbac(
                    read_case_type_col_ids={seq_case_type_col_id},
                    **x.model_dump(exclude={"read_case_type_col_ids"}),
                )
            )

        # @ABAC: Get cases
        cases = self._retrieve_cases_with_content_right(  # type: ignore[attr-defined]
            uow,
            user.id,
            temp_case_abac,
            enum.CaseRight.READ_CASE,
            case_ids=case_ids,
            case_type_ids={case_type_id},
            filter_content=True,
        )

        # Get sequence_ids from seq_case_type_col
        case_sequence_map = {}
        for case in cases:
            sequence_id = case.content.get(seq_case_type_col_id)
            if sequence_id:
                case_sequence_map[case.id] = UUID(sequence_id)

        # Retrieve tree and remove sequence_ids to avoid leaking information
        sequence_ids = list(case_sequence_map.values())
        sequence_case_map = {y: x for x, y in case_sequence_map.items()}
        phylogenetic_tree: model.PhylogeneticTree = self.app.handle(
            command.RetrievePhylogeneticTreeBySequencesCommand(
                user=cmd.user,
                tree_algorithm_code=tree_algorithm_code,
                seqdb_seq_distance_protocol_id=seqdb_seq_distance_protocol_id,
                sequence_ids=sequence_ids,
                props={
                    "leaf_id_mapper": lambda x: sequence_case_map[x],
                },
            )
        )
        phylogenetic_tree.genetic_distance_protocol_id = genetic_distance_protocol.id
        phylogenetic_tree.sequence_ids = None

    return phylogenetic_tree
