from collections.abc import Iterable
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
import gen_epix.seqdb.domain.enum as seqdb_enum
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_retrieve_phylogenetic_tree(
    self: BaseCaseService, cmd: command.RetrievePhylogeneticTreeByCasesCommand
) -> model.PhylogeneticTree:
    case_type_id = cmd.case_type_id
    dist_col_id = cmd.genetic_distance_col_id
    tree_algorithm_code = cmd.tree_algorithm
    case_ids = cmd.case_ids
    user: model.User
    user, repository = self._get_user_and_repository(cmd)  # type: ignore[assignment]
    assert isinstance(user, model.User) and user.id is not None
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    with repository.uow() as uow:
        # Get distance column data
        dist_col: model.Col = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            dist_col_id,
            CrudOperation.READ_ONE,
        )
        if dist_col.case_type_id != case_type_id:
            raise exc.InvalidArgumentsError(
                f"Col {dist_col_id} does not belong to CaseType {case_type_id}"
            )
        dist_ref_col: model.RefCol = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.RefCol,
            None,
            dist_col.ref_col_id,
            CrudOperation.READ_ONE,
        )
        if dist_ref_col.col_type != enum.ColType.GENETIC_DISTANCE:
            raise exc.InvalidArgumentsError(
                f"Col {dist_col} is not of type {enum.ColType.GENETIC_DISTANCE.value}"
            )

        # @ABAC
        assert dist_col.tree_algorithm_codes is not None
        if tree_algorithm_code not in dist_col.tree_algorithm_codes:
            raise exc.UnauthorizedAuthError(
                f"User {user.id} has no read access to tree algorithm {tree_algorithm_code}"
            )

        # Get protocol
        protocol: model.GeneticDistanceProtocol = (
            self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                model.GeneticDistanceProtocol,
                None,
                dist_ref_col.genetic_distance_protocol_id,
                CrudOperation.READ_ONE,
            )
        )
        seqdb_seq_distance_protocol_id = protocol.seqdb_seq_distance_protocol_id

        # Special case: zero case_ids
        if not case_ids:
            retval: model.PhylogeneticTree = self.app.handle(
                command.RetrievePhylogeneticTreeBySequencesCommand(
                    user=user,
                    tree_algorithm_code=tree_algorithm_code,
                    seqdb_protocol_id=seqdb_seq_distance_protocol_id,
                    profile_ids=[],
                )
            )
            retval.genetic_distance_protocol_id = protocol.id
            return retval

        # @ABAC: Get cases
        cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            case_type_id,
            case_ids=case_ids,
            filter_content=True,
        )

        # Get profile_ids from dist_col
        case_profile_map = {}
        for case in cases:
            profile_id = case.content.get(dist_col_id)
            if profile_id:
                case_profile_map[case.id] = UUID(profile_id)

        # Retrieve tree
        profile_ids = list(case_profile_map.values())
        profile_case_map = {y: x for x, y in case_profile_map.items()}
        phylogenetic_tree: model.PhylogeneticTree = self.app.handle(
            command.RetrievePhylogeneticTreeBySequencesCommand(
                user=cmd.user,
                tree_algorithm_code=tree_algorithm_code,
                seqdb_protocol_id=seqdb_seq_distance_protocol_id,
                profile_ids=profile_ids,
                props={
                    "leaf_id_mapper": lambda x: profile_case_map[x],
                },
            )
        )
        phylogenetic_tree.genetic_distance_protocol_id = protocol.id

    return phylogenetic_tree


def case_service_retrieve_genetic_sequence_fasta_by_case(
    self: BaseCaseService, cmd: command.RetrieveGeneticSequenceFastaByCaseCommand
) -> Iterable[str]:
    """
    Return a streaming iterable of FASTA formatted lines.
    Path:
    HTTP client
    -> casedb endpoint
    -> casedb service calls casedb seqdb command
    -> seqdb command (inside casedb) calls ext_app with RetrieveSeqFastaCommand
    -> seqdb service calls correct repository (dict or SA implementation) to stream Seq rows
    -> seqdb service converts rows to FASTA lines on the fly
    -> returns an iterator
    -> casedb forwards that iterator
    -> FastAPI wraps it in a StreamingResponse.
    """
    case_type_id = cmd.case_type_id
    seq_col_id = cmd.genetic_sequence_col_id
    case_ids = cmd.case_ids
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    if not case_ids:
        raise exc.InvalidArgumentsError("No case IDs given")

    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    with repository.uow() as uow:

        seq_ids_or_none: list[UUID | None] = _get_seq_ids_from_cases(
            self,
            uow,
            user,
            case_abac,
            case_type_id,
            case_ids,
            seq_col_id,
        )
        if any(x is None for x in seq_ids_or_none):
            raise exc.NoResultsError("Not all cases have a sequence")
        seq_ids: list[UUID] = seq_ids_or_none  # type: ignore[assignment]
        retrieve_cmd = command.RetrieveGeneticSequenceFastaByIdCommand(
            user=cmd.user, seq_ids=seq_ids
        )
        fasta_iterator: Iterable[str] = self.app.handle(retrieve_cmd)
        return fasta_iterator


def case_service_retrieve_protocols(
    self: BaseCaseService, cmd: command.RetrieveProtocolsCommand
) -> list[seqdb_model.Protocol]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    protocols: list[seqdb_model.Protocol] = self.app.handle(
        seqdb_command.ProtocolCrudCommand(
            user=cmd.user, operation=CrudOperation.READ_ALL
        )
    )
    # filter protocols by type ASSEMBLY_PROTOCOL
    protocols = [x for x in protocols if x.protocol_type == cmd.protocol_type]
    return protocols


def _get_seq_ids_from_cases(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    user: model.User,
    case_abac: model.CaseAbac,
    case_type_id: UUID,
    case_ids: list[UUID],
    seq_col_id: UUID,
) -> list[UUID | None]:
    # @ABAC: Get cases and sequence_ids
    cases = self._retrieve_cases_with_content_right(
        uow,
        user.id,  # type: ignore[arg-type]
        case_abac,
        enum.CaseRight.READ_CASE,
        case_type_id,
        case_ids=case_ids,
        filter_content=True,
    )
    retval = [x.content.get(seq_col_id) for x in cases]
    return [UUID(x) for x in retval if x]
