import gzip
import hashlib
from contextlib import nullcontext
from test.util.mock_compat import Mock
from uuid import UUID, uuid4

import pytest

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.enum as seqdb_enum
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case import create_seq
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp import CrudOperation

_FILE_CONTENT = b"test file content"


def _make_command(
    command_type: type,
    user: Mock,
    content: bytes = _FILE_CONTENT,
    compression: seqdb_enum.FileCompression = seqdb_enum.FileCompression.NONE,
    is_fwd: bool = True,
) -> Mock:
    cmd = Mock(spec=command_type)
    cmd.user = user
    cmd.case_id = uuid4()
    cmd.col_id = uuid4()
    cmd.file_content = content
    cmd.file_compression = compression
    cmd.file_format = (
        seqdb_enum.ReadsFileFormat.FASTQ
        if command_type is command.CreateFileForReadSetCommand
        else seqdb_enum.SeqFileFormat.FASTA
    )
    if command_type is command.CreateFileForReadSetCommand:
        cmd.is_fwd = is_fwd
    return cmd


@pytest.fixture
def user() -> Mock:
    result = Mock(spec=model.User)
    result.id = uuid4()
    return result


@pytest.fixture
def service_context(user: Mock) -> tuple[Mock, Mock, Mock, Mock, UUID]:
    service = Mock(spec=BaseCaseService)
    repository = Mock()
    service._get_user_and_repository.return_value = (user, repository)
    service.repository = repository
    service.app = Mock()
    unit_of_work = object()
    repository.uow.return_value = nullcontext(unit_of_work)

    data_collection_id = uuid4()
    case = Mock(spec=model.Case)
    case.id = uuid4()
    case.case_type_id = uuid4()
    case.created_in_data_collection_id = data_collection_id
    case.content = {}
    repository.crud.return_value = case
    repository.read_fields.return_value = []

    service.app.pdp.is_writable_columns_for_data_collections.return_value = True
    service.app.pdp.get_case_abac.return_value.is_full_access = False

    complete_case_type = Mock(spec=model.CompleteCaseType)
    service.retrieve_complete_case_type.return_value = complete_case_type
    return service, repository, case, complete_case_type, data_collection_id


def _configure_column_type(
    complete_case_type: Mock, col_id: UUID, col_type: enum.ColType
) -> None:
    ref_col_id = uuid4()
    col = Mock(spec=model.Col)
    col.ref_col_id = ref_col_id
    ref_col = Mock(spec=model.RefCol)
    ref_col.col_type = col_type
    complete_case_type.cols = {col_id: col}
    complete_case_type.ref_cols = {ref_col_id: ref_col}


@pytest.mark.parametrize(
    ("command_type", "expected_col_type", "crud_command_type"),
    [
        (
            command.CreateFileForReadSetCommand,
            enum.ColType.GENETIC_READS,
            seqdb_command.ReadSetCrudCommand,
        ),
        (
            command.CreateFileForSeqCommand,
            enum.ColType.GENETIC_SEQUENCE,
            seqdb_command.SeqCrudCommand,
        ),
    ],
    ids=["read-set", "sequence"],
)
@pytest.mark.parametrize("is_full_access", [False, True])
def test_service_creates_file_for_authorized_genetic_column(
    service_context: tuple[Mock, Mock, Mock, Mock, UUID],
    user: Mock,
    command_type: type,
    expected_col_type: enum.ColType,
    crud_command_type: type,
    is_full_access: bool,
) -> None:
    service, repository, case, complete_case_type, data_collection_id = service_context
    service.app.pdp.get_case_abac.return_value.is_full_access = is_full_access
    cmd = _make_command(command_type, user)
    linked_entity_id = uuid4()
    case.content = {cmd.col_id: str(linked_entity_id)}
    _configure_column_type(complete_case_type, cmd.col_id, expected_col_type)
    linked_entity = (
        Mock(spec=seqdb_model.ReadSet)
        if command_type is command.CreateFileForReadSetCommand
        else Mock(spec=seqdb_model.Seq)
    )
    if command_type is command.CreateFileForReadSetCommand:
        linked_entity.fwd_file_id = None
        linked_entity.fwd_reads_hash = None
        linked_entity.rev_file_id = None
        linked_entity.rev_reads_hash = None
    else:
        linked_entity.file_id = None
        linked_entity.file_hash = None
    created_file_id = uuid4()

    def handle_side_effect(seqdb_cmd: object) -> UUID | Mock:
        if isinstance(seqdb_cmd, seqdb_command.CreateFileCommand):
            return created_file_id
        if isinstance(seqdb_cmd, crud_command_type):
            return linked_entity
        raise AssertionError(f"Unexpected command: {seqdb_cmd}")

    service.app.handle.side_effect = handle_side_effect

    result = create_seq.case_service_create_file_for_read_set_or_seq(service, cmd)

    assert result == created_file_id
    crud_call = repository.crud.call_args
    assert crud_call.args[1:] == (user.id, model.Case, CrudOperation.READ_ONE)
    assert crud_call.kwargs == {"obj_ids": cmd.case_id}
    if is_full_access:
        service.app.pdp.is_writable_columns_for_data_collections.assert_not_called()
    else:
        service.app.pdp.is_writable_columns_for_data_collections.assert_called_once_with(
            complete_case_type,
            frozenset({data_collection_id}),
            frozenset({cmd.col_id}),
        )
    assert service.app.handle.call_count == 3


def test_service_rejects_upload_without_write_access(
    service_context: tuple[Mock, Mock, Mock, Mock, UUID], user: Mock
) -> None:
    service, _, case, complete_case_type, _ = service_context
    cmd = _make_command(command.CreateFileForSeqCommand, user)
    case.content = {cmd.col_id: str(uuid4())}
    _configure_column_type(
        complete_case_type, cmd.col_id, enum.ColType.GENETIC_SEQUENCE
    )
    # Deny the column-level WRITE_CASE check for this non-full-access user.
    service.app.pdp.is_writable_columns_for_data_collections.return_value = False

    with pytest.raises(exc.UnauthorizedAuthError, match="no WRITE_CASE access"):
        create_seq.case_service_create_file_for_read_set_or_seq(service, cmd)

    service.app.handle.assert_not_called()


def test_service_rejects_wrong_genetic_column_type(
    service_context: tuple[Mock, Mock, Mock, Mock, UUID], user: Mock
) -> None:
    service, _, _, complete_case_type, _ = service_context
    cmd = _make_command(command.CreateFileForReadSetCommand, user)
    # Wrong type for ReadSets.
    _configure_column_type(complete_case_type, cmd.col_id, enum.ColType.TEXT)

    with pytest.raises(exc.InvalidArgumentsError, match="Column type mismatch"):
        create_seq.case_service_create_file_for_read_set_or_seq(service, cmd)


def test_service_rejects_missing_case_content(
    service_context: tuple[Mock, Mock, Mock, Mock, UUID], user: Mock
) -> None:
    service, _, _, complete_case_type, _ = service_context
    cmd = _make_command(command.CreateFileForReadSetCommand, user)
    # Missing the required col_id from case content.
    _configure_column_type(complete_case_type, cmd.col_id, enum.ColType.GENETIC_READS)

    with pytest.raises(exc.InvalidArgumentsError, match="No ReadSet linked"):
        create_seq.case_service_create_file_for_read_set_or_seq(service, cmd)


def test_read_set_file_creation_updates_selected_direction(user: Mock) -> None:
    service = Mock(spec=BaseCaseService)
    service.app = Mock()
    cmd = _make_command(command.CreateFileForReadSetCommand, user, is_fwd=False)
    read_set = Mock(spec=seqdb_model.ReadSet)
    read_set.rev_file_id = None
    read_set.rev_reads_hash = None
    read_set.fwd_file_id = None
    read_set.fwd_reads_hash = None
    created_file_id = uuid4()
    service.app.handle.side_effect = [read_set, created_file_id, read_set]

    result = create_seq._update_read_set_with_file(service, cmd, uuid4())

    expected_hash = UUID(hashlib.sha256(_FILE_CONTENT).digest()[:16].hex())
    assert result == created_file_id
    assert read_set.rev_file_id == created_file_id
    assert read_set.rev_reads_hash == expected_hash
    assert read_set.fwd_file_id is None
    assert read_set.file_format == cmd.file_format


def test_read_set_identical_reupload_is_idempotent(user: Mock) -> None:
    service = Mock(spec=BaseCaseService)
    service.app = Mock()
    cmd = _make_command(command.CreateFileForReadSetCommand, user)
    existing_file_id = uuid4()
    read_set = Mock(spec=seqdb_model.ReadSet)
    # Already has a forward file with the uploaded content's hash.
    read_set.fwd_file_id = existing_file_id
    read_set.fwd_reads_hash = UUID(hashlib.sha256(_FILE_CONTENT).digest()[:16].hex())
    service.app.handle.return_value = read_set

    assert (
        create_seq._update_read_set_with_file(service, cmd, uuid4()) == existing_file_id
    )
    service.app.handle.assert_called_once()


def test_seq_rejects_different_content_for_existing_file(user: Mock) -> None:
    service = Mock(spec=BaseCaseService)
    service.app = Mock()
    cmd = _make_command(command.CreateFileForSeqCommand, user)
    seq = Mock(spec=seqdb_model.Seq)
    # Already has a file with a different content hash.
    seq.file_id = uuid4()
    seq.file_hash = UUID(hashlib.sha256(b"different content").digest()[:16].hex())
    service.app.handle.return_value = seq

    with pytest.raises(exc.InvalidArgumentsError, match="different content"):
        create_seq._update_seq_with_file(service, cmd, uuid4())

    service.app.handle.assert_called_once()


@pytest.mark.parametrize(
    ("content", "compression", "uncompressed"),
    [
        (_FILE_CONTENT, seqdb_enum.FileCompression.NONE, _FILE_CONTENT),
        (
            gzip.compress(_FILE_CONTENT),
            seqdb_enum.FileCompression.GZIP,
            _FILE_CONTENT,
        ),
    ],
    ids=["uncompressed", "gzip"],
)
def test_hash_uses_uncompressed_content(
    content: bytes,
    compression: seqdb_enum.FileCompression,
    uncompressed: bytes,
) -> None:
    # Gzip input is decompressed before calculating the hash.
    result = create_seq._get_hash_uuid(content, compression)

    assert result == UUID(hashlib.sha256(uncompressed).digest()[:16].hex())


def test_hash_rejects_unsupported_compression() -> None:
    with pytest.raises(ValueError, match="Unsupported compression"):
        create_seq._get_hash_uuid(_FILE_CONTENT, None)  # type: ignore[arg-type]
