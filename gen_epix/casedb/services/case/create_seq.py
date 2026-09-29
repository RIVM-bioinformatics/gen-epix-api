"""Create seqdb files linked through genetic case-content columns.

The module validates case and column access in the case repository, creates files
through seqdb commands, and updates the linked read set or sequence.
"""

import gzip
import hashlib
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import enum as seqdb_enum


def case_service_create_file_for_read_set_or_seq(
    self: BaseCaseService,
    cmd: command.CreateFileForReadSetCommand | command.CreateFileForSeqCommand,
) -> UUID:
    """Create or reuse a file for a case-linked read set or sequence.

    The handler verifies WRITE_CASE access to the selected genetic column. Uploading
    identical uncompressed content is idempotent and returns the existing file ID.
    Case reads occur in one case-repository unit of work, while file creation and
    read-set or sequence updates are separate seqdb commands; the overall operation
    is not one cross-domain transaction.

    Args:
        self: Case service handling the command.
        cmd: Read-set or sequence file creation command.

    Returns:
        Identifier of the existing or newly created file.

    Raises:
        InvalidArgumentsError: If the command type, linked content, column type,
            case type, or an existing file's content is invalid.
        UnauthorizedAuthError: If the user lacks column-level write access through
            every collection associated with the case.
        ValueError: If command dispatch reaches an unsupported command type.
    """
    user, repository = self._get_user_and_repository(cmd)
    user_id: UUID = user.id  # type: ignore[assignment]

    # Parse input
    if isinstance(cmd, command.CreateFileForReadSetCommand):
        is_read_set = True
    elif isinstance(cmd, command.CreateFileForSeqCommand):
        is_read_set = False
    else:
        raise exc.InvalidArgumentsError("8b764853", "Invalid command type")

    # Retrieve case ABAC
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    # Handle transaction for reading case
    with repository.uow() as uow:
        cases = _get_cases_for_create_file_for_read_sets_or_seqs(
            self, cmd, case_abac, uow, user_id, [cmd.case_id], [cmd.col_id]
        )
        case = cases[0]

        # Retrieve ReadSet or Seq ID from case content
        if cmd.col_id not in case.content:
            raise exc.InvalidArgumentsError(
                "b5acc6e9", "No ReadSet linked to case for the given Col"
            )
        read_set_or_seq_id = UUID(case.content[cmd.col_id])

    if is_read_set:
        assert isinstance(cmd, command.CreateFileForReadSetCommand)
        # Verify no file linked yet
        read_set: seqdb_model.ReadSet = self.app.handle(
            seqdb_command.ReadSetCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ONE,
                obj_ids=read_set_or_seq_id,
            )
        )
        # Compute file hash before checking existing links to enable
        # idempotent re-uploads (same content → return existing file_id).
        file_hash = _get_hash_uuid(cmd.file_content, cmd.file_compression)
        if cmd.is_fwd and read_set.fwd_file_id is not None:
            if read_set.fwd_reads_hash == file_hash:
                return read_set.fwd_file_id
            raise exc.InvalidArgumentsError(
                "d0a23cd0",
                "The ReadSet already has a forward file linked with different content",
            )
        if not cmd.is_fwd and read_set.rev_file_id is not None:
            if read_set.rev_reads_hash == file_hash:
                return read_set.rev_file_id
            raise exc.InvalidArgumentsError(
                "30150932",
                "The ReadSet already has a reverse file linked with different content",
            )
        file_id = _create_file(self, cmd)
        # Update ReadSet with file ID and hash
        if cmd.is_fwd:
            read_set.fwd_file_id = file_id
            read_set.fwd_reads_hash = file_hash
        else:
            read_set.rev_file_id = file_id
            read_set.rev_reads_hash = file_hash
        read_set.file_format = cmd.file_format
        self.app.handle(
            seqdb_command.ReadSetCrudCommand(
                user=cmd.user,
                operation=CrudOperation.UPDATE_ONE,
                objs=read_set,
            )
        )

    elif isinstance(cmd, command.CreateFileForSeqCommand):
        # Verify no file linked yet
        seq: seqdb_model.Seq = self.app.handle(
            seqdb_command.SeqCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ONE,
                obj_ids=read_set_or_seq_id,
            )
        )
        # Compute file hash before checking existing link to enable
        # idempotent re-uploads (same content → return existing file_id).
        file_hash = _get_hash_uuid(cmd.file_content, cmd.file_compression)
        if seq.file_id is not None:
            if seq.file_hash == file_hash:
                return seq.file_id
            raise exc.InvalidArgumentsError(
                "dd752d19",
                "The Seq already has a file linked with different content",
            )
        file_id = _create_file(self, cmd)
        # Update Seq with file ID and hash
        seq.file_id = file_id
        seq.file_hash = file_hash
        seq.file_format = cmd.file_format
        self.app.handle(
            seqdb_command.SeqCrudCommand(
                user=cmd.user,
                operation=CrudOperation.UPDATE_ONE,
                objs=seq,
            )
        )

    else:
        raise ValueError("Invalid command type")

    assert file_id is not None
    return file_id


def _get_cases_for_create_file_for_read_sets_or_seqs(
    self: BaseCaseService,
    cmd: command.CreateFileForReadSetCommand | command.CreateFileForSeqCommand,
    case_abac: model.CaseAbac,
    uow: BaseUnitOfWork,
    user_id: UUID,
    case_ids: list[UUID],
    col_ids: list[UUID],
) -> list[model.Case]:
    """Load cases and validate genetic column compatibility and write access.

    Args:
        self: Case service used for repository and association access.
        cmd: Read-set or sequence file creation command.
        case_abac: Case access policy data used for column authorization.
        uow: Active case repository unit of work.
        user_id: Identifier used for repository reads.
        case_ids: Case identifiers to retrieve.
        col_ids: Corresponding genetic column identifiers.

    Returns:
        Retrieved cases in repository result order.

    Raises:
        InvalidArgumentsError: If the command type is unsupported, a column has the
            wrong genetic type, or a column and case have different case types.
        UnauthorizedAuthError: If a case has no associated collection granting write
            access to its corresponding column.
    """
    # Get Col and RefCol data
    cols: list[model.Col] = self.repository.crud(
        uow,
        user_id,
        model.Col,
        CrudOperation.READ_SOME,
        obj_ids=list(set(col_ids)),
    )
    col_map: dict[UUID, model.Col] = {x.id: x for x in cols if x.id is not None}

    # Get RefCol data
    ref_col_ids: set[UUID] = {x.ref_col_id for x in cols}
    ref_cols: list[model.RefCol] = self.repository.crud(
        uow,
        user_id,
        model.RefCol,
        CrudOperation.READ_SOME,
        obj_ids=list(ref_col_ids),
    )
    ref_col_by_id: dict[UUID, model.RefCol] = {
        x.id: x for x in ref_cols if x.id is not None
    }

    # TODO: Verify all Cols are for the given CaseType

    # Verify all Cols are of type GENETIC_READS
    if isinstance(cmd, command.CreateFileForReadSetCommand):
        expected_col_type = enum.ColType.GENETIC_READS
    elif isinstance(cmd, command.CreateFileForSeqCommand):
        expected_col_type = enum.ColType.GENETIC_SEQUENCE
    else:
        raise exc.InvalidArgumentsError("1c4b839d", "Invalid command type")
    invalid_col_ids = [
        x.ref_col_id
        for x in cols
        if ref_col_by_id[x.ref_col_id].col_type != expected_col_type
    ]
    if invalid_col_ids:
        invalid_col_ids_str = ", ".join(str(x) for x in invalid_col_ids)
        raise exc.InvalidArgumentsError(
            "4f1a5c97",
            f"Some columns are not of type {expected_col_type.name}: {invalid_col_ids_str}",
        )

    # Get Case data
    cases: list[model.Case] = self.repository.crud(
        uow,
        user_id,
        model.Case,
        CrudOperation.READ_SOME,
        obj_ids=list(case_ids),
    )

    # Verify if all Cols are for the same CaseType as the cases
    # TODO: remove once the command is adjusted to be for only one CaseType
    invalid_col_ids = [
        y for x, y in zip(cases, col_ids) if col_map[y].case_type_id != x.case_type_id
    ]
    if invalid_col_ids:
        invalid_col_ids_str = ", ".join(str(x) for x in invalid_col_ids)
        raise exc.InvalidArgumentsError(
            "d258a460",
            f"Some Col IDs are for a different CaseType than the given cases: {invalid_col_ids_str}",
        )

    # @ABAC: Verify write rights to Col for each case
    if not case_abac.is_full_access:
        # Get some write rights to Col
        writable_data_collections_by_col: dict[UUID, set[UUID]] = {
            x: case_abac.get_data_collections_with_access_right_for_col(
                x, enum.CaseRight.WRITE_CASE
            )
            for x in col_ids
        }
        # Retrieve data collections by Case ID for ABAC column-level write checks
        case_data_collections_map: dict[UUID, set[UUID]] = (
            self._retrieve_case_data_collections_map(uow, user_id, case_ids=case_ids)
        )
        # For each requested (Case, Col), ensure the user has write access
        # to that column in at least one data collection the case belongs to
        for case, col_id in zip(cases, col_ids):
            # Membership includes created_in_data_collection_id
            assert case.id is not None
            case_data_collections = set(case_data_collections_map.get(case.id, set()))
            case_data_collections.add(case.created_in_data_collection_id)
            if case_data_collections.isdisjoint(
                writable_data_collections_by_col[col_id]
            ):
                raise exc.UnauthorizedAuthError(
                    "7c74259b",
                    "User has no WRITE_CASE access to the specified column in any data collection of the case",
                )
    return cases


def _create_file(
    self: BaseCaseService,
    cmd: command.CreateFileForReadSetCommand | command.CreateFileForSeqCommand,
) -> UUID:
    """Dispatch a seqdb command to create a file.

    Args:
        self: Case service whose application dispatches the command.
        cmd: Command supplying file bytes, format, compression, and user.

    Returns:
        Identifier returned by the seqdb file creation command.
    """
    created_file_id: UUID = self.app.handle(
        seqdb_command.CreateFileCommand(
            user=cmd.user,
            file=seqdb_model.File(content=cmd.file_content),
            format=seqdb_enum.FileFormat(cmd.file_format.value),
            compression=cmd.file_compression,
        )
    )
    return created_file_id


def _get_hash_uuid(content: bytes, compression: seqdb_enum.FileCompression) -> UUID:
    """Derive a stable UUID from the uncompressed file content.

    Args:
        content: Raw file bytes in the declared compression format.
        compression: Compression applied to ``content``.

    Returns:
        UUID formed from the first 16 bytes of the SHA-256 digest.

    Raises:
        ValueError: If the compression mode is unsupported.
    """
    if compression == seqdb_enum.FileCompression.NONE:
        uncompressed_content = content
    elif compression == seqdb_enum.FileCompression.GZIP:
        uncompressed_content = gzip.decompress(content)
    else:
        raise ValueError(f"Unsupported compression: {compression}")
    return UUID(hashlib.sha256(uncompressed_content).digest()[:16].hex())
