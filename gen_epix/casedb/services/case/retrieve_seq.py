"""Retrieve phylogenetic, FASTA, and protocol data through seqdb commands."""

from collections.abc import Iterable
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_retrieve_phylogenetic_tree(
    self: BaseCaseService, cmd: command.RetrievePhylogeneticTreeByCasesCommand
) -> model.PhylogeneticTree:
    """Build a phylogenetic tree for accessible case-linked profiles.

    The distance column must belong to the requested case type, represent genetic
    distance, and permit the selected tree algorithm. Case access and content are
    filtered before profile IDs are sent to seqdb. Tree leaf profile IDs are mapped
    back to case IDs.

    Args:
        self: Case service handling the retrieval.
        cmd: Command defining cases, distance column, algorithm, and QC restrictions.

    Returns:
        Phylogenetic tree annotated with the case genetic-distance protocol ID.

    Raises:
        InvalidArgumentsError: If the distance column has the wrong case or column
            type.
        UnauthorizedAuthError: If the selected tree algorithm is not allowed.
    """
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
        dist_col: model.Col = repository.crud(
            uow,
            user.id,
            model.Col,
            CrudOperation.READ_ONE,
            obj_ids=dist_col_id,
        )
        if dist_col.case_type_id != case_type_id:
            raise exc.InvalidArgumentsError(
                "b081c000",
                f"Col {dist_col_id} does not belong to CaseType {case_type_id}",
            )
        dist_ref_col: model.RefCol = repository.crud(
            uow,
            user.id,
            model.RefCol,
            CrudOperation.READ_ONE,
            obj_ids=dist_col.ref_col_id,
        )
        if dist_ref_col.col_type != enum.ColType.GENETIC_DISTANCE:
            raise exc.InvalidArgumentsError(
                "b8f2c28c",
                f"Col {dist_col} is not of type {enum.ColType.GENETIC_DISTANCE.value}",
            )

        # @ABAC
        assert dist_col.tree_algorithm_codes is not None
        if tree_algorithm_code not in dist_col.tree_algorithm_codes:
            raise exc.UnauthorizedAuthError(
                "cda692df",
                f"User {user.id} has no read access to tree algorithm {tree_algorithm_code}",
            )

        # Get protocol
        genetic_distance_protocol: model.GeneticDistanceProtocol = self.repository.crud(
            uow,
            user.id,
            model.GeneticDistanceProtocol,
            CrudOperation.READ_ONE,
            obj_ids=dist_ref_col.genetic_distance_protocol_id,
        )
        seqdb_seq_distance_protocol_id = (
            genetic_distance_protocol.seqdb_seq_distance_protocol_id
        )

        # Special case: zero case_ids
        if not case_ids:
            phylogenetic_tree: model.PhylogeneticTree = self.app.handle(
                command.RetrievePhylogeneticTreeByProfilesCommand(
                    user=user,
                    tree_algorithm_code=tree_algorithm_code,
                    seqdb_protocol_id=seqdb_seq_distance_protocol_id,
                    profile_ids=[],
                    allowed_qc_results=cmd.allowed_qc_results,
                )
            )
            phylogenetic_tree.protocol_id = genetic_distance_protocol.id
            return phylogenetic_tree

        # @ABAC: Get cases
        cases, is_max_results_exceeded = self._retrieve_cases_with_content_right(
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
            command.RetrievePhylogeneticTreeByProfilesCommand(
                user=cmd.user,
                tree_algorithm_code=tree_algorithm_code,
                seqdb_protocol_id=seqdb_seq_distance_protocol_id,
                profile_ids=profile_ids,
                allowed_qc_results=cmd.allowed_qc_results,
                props={
                    "leaf_id_mapper": lambda x: profile_case_map[x],
                },
            )
        )
        phylogenetic_tree.protocol_id = genetic_distance_protocol.id

    return phylogenetic_tree


def case_service_retrieve_genetic_sequence_fasta_by_case(
    self: BaseCaseService, cmd: command.RetrieveGeneticSequenceFastaByCaseCommand
) -> Iterable[str]:
    """Return a streaming iterable of FASTA-formatted lines.

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

    Args:
        self: Case service handling the retrieval.
        cmd: Command identifying cases and the genetic-sequence column.

    Returns:
        Lazy FASTA text lines produced by seqdb.

    Raises:
        InvalidArgumentsError: If no case IDs are supplied.
        NoResultsError: If any accessible requested case lacks a sequence value.
    """
    case_type_id = cmd.case_type_id
    seq_col_id = cmd.genetic_sequence_col_id
    case_ids = cmd.case_ids
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    if not case_ids:
        raise exc.InvalidArgumentsError("45b13e30", "No case IDs given")

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
            raise exc.NoResultsError("7c140425", "Not all cases have a sequence")
        seq_ids: list[UUID] = seq_ids_or_none  # type: ignore[assignment]
        retrieve_cmd = command.RetrieveGeneticSequenceFastaByIdCommand(
            user=cmd.user, seq_ids=seq_ids
        )
        fasta_iterator: Iterable[str] = self.app.handle(retrieve_cmd)
        return fasta_iterator


def case_service_retrieve_protocols(
    self: BaseCaseService, cmd: command.RetrieveProtocolsCommand
) -> list[seqdb_model.Protocol]:
    """Retrieve seqdb protocols filtered to the requested protocol type.

    Args:
        self: Case service dispatching the seqdb command.
        cmd: Command containing user context and the requested protocol type.

    Returns:
        Protocols whose type equals the requested type.
    """
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
    """Retrieve accessible cases and extract populated sequence identifiers.

    Args:
        self: Case service used for access-filtered case retrieval.
        uow: Active case repository unit of work.
        user: User whose case access is applied.
        case_abac: Case access metadata for the user.
        case_type_id: Case type shared by requested cases.
        case_ids: Case identifiers to retrieve.
        seq_col_id: Content column containing sequence identifiers.

    Returns:
        UUIDs parsed from populated sequence values in accessible result order.
    """
    # @ABAC: Get cases and sequence_ids
    cases, is_max_results_exceeded = self._retrieve_cases_with_content_right(
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
