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
    user, repository = self._get_user_and_repository(cmd)
    user_id: UUID = user.id  # type: ignore[assignment]

    # Parse input
    if isinstance(cmd, command.CreateFileForReadSetCommand):
        is_read_set = True
    elif isinstance(cmd, command.CreateFileForSeqCommand):
        is_read_set = False
    else:
        raise exc.InvalidArgumentsError("Invalid command type")

    # Retrieve case ABAC
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    # Handle transaction for reading case
    with repository.uow() as uow:
        cases = _get_cases_for_create_file_for_read_sets_or_seqs(
            self, cmd, case_abac, uow, user_id, [cmd.case_id], [cmd.case_type_col_id]
        )
        case = cases[0]

        # Retrieve ReadSet or Seq ID from case content
        if cmd.case_type_col_id not in case.content:
            raise exc.InvalidArgumentsError(
                "No ReadSet linked to case for the given case type column"
            )
        read_set_or_seq_id = UUID(case.content[cmd.case_type_col_id])

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
        if cmd.is_fwd and read_set.fwd_file_id is not None:
            raise exc.InvalidArgumentsError(
                "The ReadSet already has a forward file linked"
            )
        if not cmd.is_fwd and read_set.rev_file_id is not None:
            raise exc.InvalidArgumentsError(
                "The ReadSet already has a reverse file linked"
            )
        # Compute file hash then create file
        file_hash = _get_hash_uuid(cmd.file_content, cmd.file_compression)
        file_id = _create_file(self, cmd)
        # Update ReadSet with file ID and hash
        if cmd.is_fwd:
            read_set.fwd_file_id = file_id
            read_set.fwd_reads_hash = file_hash
        else:
            read_set.rev_file_id = file_id
            read_set.rev_reads_hash = file_hash
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
        if seq.file_id is not None:
            raise exc.InvalidArgumentsError("The Seq already has a file linked")
        # Compute file hash then create file
        file_hash = _get_hash_uuid(cmd.file_content, cmd.file_compression)
        file_id = _create_file(self, cmd)
        # Update Seq with file ID and hash
        seq.file_id = file_id
        seq.file_hash = file_hash
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
    case_type_col_ids: list[UUID],
) -> list[model.Case]:
    # Get CaseTypeCol and RefCol data
    case_type_cols: list[model.CaseTypeCol] = (
        self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.CaseTypeCol,
            None,
            list(set(case_type_col_ids)),
            CrudOperation.READ_SOME,
        )
    )
    case_type_col_by_id: dict[UUID, model.CaseTypeCol] = {
        x.id: x for x in case_type_cols if x.id is not None
    }

    # Get RefCol data
    ref_col_ids: set[UUID] = {
        case_type_col.ref_col_id for case_type_col in case_type_cols
    }
    ref_cols: list[model.RefCol] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.RefCol,
        None,
        list(ref_col_ids),
        CrudOperation.READ_SOME,
    )
    ref_col_by_id: dict[UUID, model.RefCol] = {
        x.id: x for x in ref_cols if x.id is not None
    }

    # TODO: Verify all case type cols are for the given case type

    # Verify all case type cols are of type GENETIC_READS
    if isinstance(cmd, command.CreateFileForReadSetCommand):
        expected_col_type = enum.ColType.GENETIC_READS
    elif isinstance(cmd, command.CreateFileForSeqCommand):
        expected_col_type = enum.ColType.GENETIC_SEQUENCE
    else:
        raise exc.InvalidArgumentsError("Invalid command type")
    invalid_case_type_col_ids = [
        x.ref_col_id
        for x in case_type_cols
        if ref_col_by_id[x.ref_col_id].col_type != expected_col_type
    ]
    if invalid_case_type_col_ids:
        invalid_case_type_col_ids_str = ", ".join(
            str(x) for x in invalid_case_type_col_ids
        )
        raise exc.InvalidArgumentsError(
            f"Some columns are not of type {expected_col_type.name}: {invalid_case_type_col_ids_str}"
        )

    # Get Case data
    cases: list[model.Case] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.Case,
        None,
        list(case_ids),
        CrudOperation.READ_SOME,
    )

    # Verify if all case type cols are for the same case type as the cases
    # TODO: remove once the command is adjusted to be for only one case type
    invalid_case_type_col_ids = [
        y
        for x, y in zip(cases, case_type_col_ids)
        if case_type_col_by_id[y].case_type_id != x.case_type_id
    ]
    if invalid_case_type_col_ids:
        invalid_case_type_col_ids_str = ", ".join(
            str(x) for x in invalid_case_type_col_ids
        )
        raise exc.InvalidArgumentsError(
            f"Some case type column ids are for a different case type than the given cases: {invalid_case_type_col_ids_str}"
        )

    # @ABAC: Verify write rights to case_type_col for each case
    if not case_abac.is_full_access:
        # Get some write rights to case_type_col
        writable_data_collections_by_case_type_col: dict[UUID, set[UUID]] = {
            x: case_abac.get_data_collections_with_access_right_for_case_type_col(
                x, enum.CaseRight.WRITE_CASE
            )
            for x in case_type_col_ids
        }
        # Retrieve data collections by case id for ABAC column-level write checks
        case_data_collections_map: dict[UUID, set[UUID]] = (
            self._retrieve_case_data_collections_map(uow, user_id, case_ids=case_ids)
        )
        # For each requested (case, case_type_col), ensure the user has write access
        # to that column in at least one data collection the case belongs to
        for case, case_type_col_id in zip(cases, case_type_col_ids):
            # Membership includes created_in_data_collection_id
            assert case.id is not None
            case_data_collections = set(case_data_collections_map.get(case.id, set()))
            case_data_collections.add(case.created_in_data_collection_id)
            if case_data_collections.isdisjoint(
                writable_data_collections_by_case_type_col[case_type_col_id]
            ):
                raise exc.UnauthorizedAuthError(
                    "User has no WRITE_CASE access to the specified column in any data collection of the case"
                )
    return cases


def _create_file(
    self: BaseCaseService,
    cmd: command.CreateFileForReadSetCommand | command.CreateFileForSeqCommand,
) -> UUID:
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
    if compression == seqdb_enum.FileCompression.NONE:
        uncompressed_content = content
    elif compression == seqdb_enum.FileCompression.GZIP:
        uncompressed_content = gzip.decompress(content)
    else:
        raise ValueError(f"Unsupported compression: {compression}")
    return UUID(hashlib.sha256(uncompressed_content).digest()[:16].hex())
