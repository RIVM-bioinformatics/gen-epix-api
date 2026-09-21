"""Create seqdb files linked through genetic case-content columns.

The module validates case and column access in the case repository, creates files
through seqdb commands, and updates the linked read set or sequence.
"""

import gzip
import hashlib
from typing import cast
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BasePolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp import CrudOperation
from gen_epix.filter.equals_uuid import EqualsUuidFilter
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

    # Parse input
    if isinstance(cmd, command.CreateFileForReadSetCommand):
        is_read_set = True
    elif isinstance(cmd, command.CreateFileForSeqCommand):
        is_read_set = False
    else:
        raise exc.InvalidArgumentsError("8b764853", "Invalid command type")

    # Handle transaction for reading case
    with repository.uow() as uow:
        # Retrieve case
        case: model.Case = repository.crud(
            uow, user.id, model.Case, CrudOperation.READ_ONE, obj_ids=cmd.case_id
        )

        # Retrieve data collection IDs associated with the case
        data_collection_id_tuples = self.repository.read_fields(
            uow,
            user.id,
            model.CaseDataCollectionLink,
            ["data_collection_id"],
            filter=EqualsUuidFilter(key="case_id", value=cast(UUID, case.id)),
        )
        data_collection_ids = frozenset(x[0] for x in data_collection_id_tuples)

        # ABAC PEP: Check if column is readable
        complete_case_type = self.retrieve_complete_case_type(
            command.RetrieveCompleteCaseTypeCommand(
                user=cmd.user, case_type_id=case.case_type_id
            )
        )
        pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if not pdp.is_readable_columns_for_data_collections(
            complete_case_type, data_collection_ids, frozenset([cmd.col_id])
        ):
            raise exc.UnauthorizedAuthError(
                "c06dfc2e", "Column is not readable for the specified data collections"
            )

        # Verify column type
        ref_col_id = complete_case_type.cols[cmd.col_id].ref_col_id
        col_type = complete_case_type.ref_cols[ref_col_id].col_type
        if is_read_set:
            expected_col_type = enum.ColType.GENETIC_READS
        else:
            expected_col_type = enum.ColType.GENETIC_SEQUENCE
        if col_type != expected_col_type:
            raise exc.InvalidArgumentsError(
                "4f1a5c97",
                f"Column type mismatch: expected {expected_col_type}, got {col_type}",
            )

        # Get the ReadSet or Seq ID for the given case and column
        read_set_or_seq_id_str_or_none = case.content.get(cmd.col_id)
        if read_set_or_seq_id_str_or_none is None:
            model_str = "ReadSet" if is_read_set else "Seq"
            raise exc.InvalidArgumentsError(
                "b5acc6e9", f"No {model_str} linked to case for Col {cmd.col_id}"
            )
        read_set_or_seq_id = UUID(read_set_or_seq_id_str_or_none)

    if is_read_set:
        assert isinstance(cmd, command.CreateFileForReadSetCommand)
        file_id = _update_read_set_with_file(self, cmd, read_set_or_seq_id)
    elif isinstance(cmd, command.CreateFileForSeqCommand):
        assert isinstance(cmd, command.CreateFileForSeqCommand)
        file_id = _update_seq_with_file(self, cmd, read_set_or_seq_id)
    else:
        raise AssertionError("Invalid command type")

    return file_id


def _update_read_set_with_file(
    self: BaseCaseService,
    cmd: command.CreateFileForReadSetCommand,
    read_set_or_seq_id: UUID,
) -> UUID:
    """Update a ReadSet with the given file ID and hash."""
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
    return file_id


def _update_seq_with_file(
    self: BaseCaseService,
    cmd: command.CreateFileForSeqCommand,
    read_set_or_seq_id: UUID,
) -> UUID:
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
    return file_id


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
