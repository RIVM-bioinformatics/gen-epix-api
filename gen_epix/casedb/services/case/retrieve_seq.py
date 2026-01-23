from collections.abc import Iterable
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


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
        cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            temp_case_abac,
            enum.CaseRight.READ_CASE,
            case_ids=case_ids,
            case_type_id=case_type_id,
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


def case_service_retrieve_genetic_sequence_by_case(
    self: BaseCaseService,
    cmd: command.RetrieveGeneticSequenceByCaseCommand,
) -> list[model.GeneticSequence]:
    seq_case_type_col_id = cmd.genetic_sequence_case_type_col_id
    case_ids = cmd.case_ids
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    if not case_ids:
        return []

    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    with repository.uow() as uow:
        seq_ids_or_none: list[UUID | None] = _get_seq_ids_from_cases(
            self,
            uow,
            user,
            case_abac,
            case_ids,
            seq_case_type_col_id,
        )
        if any(x is None for x in seq_ids_or_none):
            raise exc.NoResultsError("Not all cases have a sequence")
        seq_ids: list[UUID] = seq_ids_or_none  # type: ignore[assignment]

        # Retrieve sequences
        genetic_sequences: list[model.GeneticSequence] = self.app.handle(
            command.RetrieveGeneticSequenceByIdCommand(
                user=user,
                seq_ids=seq_ids,
            )
        )

    return genetic_sequences


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
    seq_case_type_col_id = cmd.genetic_sequence_case_type_col_id
    case_ids = cmd.case_ids
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    if not case_ids:
        raise exc.InvalidArgumentsError("No case ids given")

    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    with repository.uow() as uow:

        seq_ids_or_none: list[UUID | None] = _get_seq_ids_from_cases(
            self,
            uow,
            user,
            case_abac,
            case_ids,
            seq_case_type_col_id,
        )
        if any(x is None for x in seq_ids_or_none):
            raise exc.NoResultsError("Not all cases have a sequence")
        seq_ids: list[UUID] = seq_ids_or_none  # type: ignore[assignment]
        retrieve_cmd = command.RetrieveGeneticSequenceFastaByIdCommand(
            user=cmd.user, seq_ids=seq_ids
        )
        fasta_iterator: Iterable[str] = self.app.handle(retrieve_cmd)
        return fasta_iterator


def case_service_retrieve_sequencing_protocols(
    self: BaseCaseService,
    cmd: command.RetrieveSequencingProtocolsCommand,
) -> list[seqdb_model.SequencingProtocol]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    sequencing_protocols: list[seqdb_model.SequencingProtocol] = self.app.handle(
        seqdb_command.SequencingProtocolCrudCommand(
            user=cmd.user,
            operation=CrudOperation.READ_ALL,
        )
    )
    return sequencing_protocols


def case_service_retrieve_assembly_protocols(
    self: BaseCaseService, cmd: command.RetrieveAssemblyProtocolsCommand
) -> list[seqdb_model.AssemblyProtocol]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    assembly_protocols: list[seqdb_model.AssemblyProtocol] = self.app.handle(
        seqdb_command.AssemblyProtocolCrudCommand(
            user=cmd.user,
            operation=CrudOperation.READ_ALL,
        )
    )
    return assembly_protocols


def _get_seq_ids_from_cases(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    user: model.User,
    case_abac: model.CaseAbac,
    case_ids: list[UUID],
    seq_case_type_col_id: UUID,
) -> list[UUID | None]:
    # @ABAC: Get cases and sequence_ids
    cases = self._retrieve_cases_with_content_right(
        uow,
        user.id,  # type: ignore[arg-type]
        case_abac,
        enum.CaseRight.READ_CASE,
        NULL_ID,
        case_ids=case_ids,
        filter_content=True,
    )
    retval = [x.content.get(seq_case_type_col_id) for x in cases]
    return [UUID(x) for x in retval if x]
