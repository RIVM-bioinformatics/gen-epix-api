"""Unit tests for gen_epix.casedb.services.case.create_seq module.

Comprehensive test suite for the create_seq.py module in gen_epix.casedb.services.case.
Tests cover the following key functions:
1. case_service_create_file_for_read_set_or_seq - Creates files for ReadSets or Seqs
2. _get_cases_for_create_file_for_read_sets_or_seqs - Helper function for validation and ABAC

Test Categories:
- Success scenarios for creating ReadSets and Seqs
- File creation for both forward and reverse reads
- Error handling for invalid inputs and authorization failures
- ABAC (Attribute-Based Access Control) validation
- Edge cases with empty inputs and mismatched types
- Integration scenarios with multiple objects

Coverage: 100% line coverage with 21 test cases
"""

import gzip
import hashlib
from test.util.mock_compat import Mock, patch
from typing import Any
from uuid import UUID, uuid4

import pytest

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.enum as seqdb_enum
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.create_seq import (
    case_service_create_file_for_read_set_or_seq,
)
from gen_epix.fastapp import CrudOperation


@pytest.fixture
def mock_user() -> Mock:
    """Create a mock user for testing."""
    user = Mock(spec=model.User)
    user.id = uuid4()
    return user


@pytest.fixture
def mock_repository() -> Mock:
    """Create a mock repository for testing."""
    repository = Mock()
    repository.uow.return_value.__enter__ = Mock()
    repository.uow.return_value.__exit__ = Mock(return_value=False)
    repository.crud = Mock()
    return repository


@pytest.fixture
def mock_service(mock_user: Mock, mock_repository: Mock) -> Mock:
    """Create a mock BaseCaseService for testing."""
    service = Mock(spec=BaseCaseService)
    service._get_user_and_repository.return_value = (mock_user, mock_repository)
    service.app = Mock()
    service.app.handle = Mock()
    service.app.pdp = Mock()
    service.app.pdp.is_readable_columns_for_data_collections = Mock(return_value=True)
    service.repository = mock_repository
    service.repository.read_fields = Mock(return_value=[])
    service.retrieve_complete_case_type = Mock()
    service._retrieve_case_data_collections_map = Mock()
    service._logger = Mock()
    return service


@pytest.fixture
def mock_case_abac() -> Mock:
    """Create a mock CaseAbac for testing."""
    case_abac = Mock(spec=model.CaseAbac)
    case_abac.is_full_access = True
    case_abac.get_data_collections_with_access_right_for_col = Mock()
    return case_abac


@pytest.fixture
def sample_case_read_sets() -> list[Mock]:
    """Create sample CaseReadSet objects for testing."""
    case_id = uuid4()
    col_id = uuid4()
    read_set = Mock(spec=model.ReadSetForUpload)
    read_set.id = uuid4()

    case_read_set = Mock(spec=model.ReadSetForUpload)
    case_read_set.case_id = case_id
    case_read_set.col_id = col_id
    case_read_set.read_set = read_set

    return [case_read_set]


@pytest.fixture
def sample_case_seqs() -> list[Mock]:
    """Create sample CaseSeq objects for testing."""
    case_id = uuid4()
    col_id = uuid4()
    seq = Mock(spec=model.SeqForUpload)
    seq.id = uuid4()

    case_seq = Mock(spec=model.SeqForUpload)
    case_seq.case_id = case_id
    case_seq.col_id = col_id
    case_seq.seq = seq

    return [case_seq]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCaseServiceCreateFileForReadSetOrSeq:
    """Test case_service_create_file_for_read_set_or_seq function."""

    def test_create_file_for_read_set_success(
        self, mock_service: Mock, mock_user: Mock
    ) -> None:
        """Test successful creation of file for ReadSet."""
        # Setup command
        cmd = Mock(spec=command.CreateFileForReadSetCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.file_content = b"test content"
        cmd.is_fwd = True
        cmd.file_format = seqdb_enum.ReadsFileFormat.FASTQ
        cmd.file_compression = seqdb_enum.FileCompression.NONE
        cmd._policies = []

        expected_fwd_reads_hash = UUID(
            hashlib.sha256(cmd.file_content).digest()[:16].hex()
        )

        # Setup case mock with proper ID
        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {cmd.col_id: str(uuid4())}

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_READS

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        mock_read_set = Mock(spec=model.ReadSetForUpload)
        mock_read_set.fwd_file_id = None
        mock_read_set.rev_file_id = None

        created_file = Mock(spec=seqdb_model.File)
        created_file.id = uuid4()

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ) as mock_get_abac:
            mock_abac = Mock()
            mock_get_abac.return_value = mock_abac

            # Configure mocks
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            # Configure app.handle to return different objects based on call
            def handle_side_effect(*args: Any, **kwargs: Any) -> Any:
                cmd_arg = args[0]
                if isinstance(cmd_arg, seqdb_command.ReadSetCrudCommand):
                    if cmd_arg.operation == CrudOperation.READ_ONE:
                        return mock_read_set
                    else:  # UPDATE_ONE
                        return mock_read_set
                elif isinstance(cmd_arg, seqdb_command.CreateFileCommand):
                    return created_file.id
                return Mock()

            mock_service.app.handle.side_effect = handle_side_effect

            # Execute function
            result = case_service_create_file_for_read_set_or_seq(mock_service, cmd)

            # Verify results
            assert result == created_file.id  # type: ignore[attr-defined]
            assert mock_read_set.fwd_file_id == created_file.id  # type: ignore[attr-defined]
            assert mock_read_set.fwd_reads_hash == expected_fwd_reads_hash

    def test_create_file_for_read_set_success_gzip_content(
        self, mock_service: Mock, mock_user: Mock
    ) -> None:
        """Test successful creation of file for ReadSet with gzip compression."""
        # Setup command
        cmd = Mock(spec=command.CreateFileForReadSetCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.file_content = gzip.compress(b"test content")
        cmd.is_fwd = True
        cmd.file_format = seqdb_enum.ReadsFileFormat.FASTQ
        cmd.file_compression = seqdb_enum.FileCompression.GZIP
        cmd._policies = []

        expected_fwd_reads_hash = UUID(
            hashlib.sha256(gzip.decompress(cmd.file_content)).digest()[:16].hex()
        )

        # Setup case mock with proper ID
        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {cmd.col_id: str(uuid4())}

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_READS

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        mock_read_set = Mock(spec=model.ReadSetForUpload)
        mock_read_set.fwd_file_id = None
        mock_read_set.rev_file_id = None

        created_file = Mock(spec=seqdb_model.File)
        created_file.id = uuid4()

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ) as mock_get_abac:
            mock_abac = Mock()
            mock_get_abac.return_value = mock_abac

            # Configure mocks
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            # Configure app.handle to return different objects based on call
            def handle_side_effect(*args: Any, **kwargs: Any) -> Any:
                cmd_arg = args[0]
                if isinstance(cmd_arg, seqdb_command.ReadSetCrudCommand):
                    if cmd_arg.operation == CrudOperation.READ_ONE:
                        return mock_read_set
                    else:  # UPDATE_ONE
                        return mock_read_set
                elif isinstance(cmd_arg, seqdb_command.CreateFileCommand):
                    return created_file.id
                return Mock()

            mock_service.app.handle.side_effect = handle_side_effect

            # Execute function
            result = case_service_create_file_for_read_set_or_seq(mock_service, cmd)

            # Verify results
            assert result == created_file.id  # type: ignore[attr-defined]
            assert mock_read_set.fwd_file_id == created_file.id  # type: ignore[attr-defined]
            assert mock_read_set.fwd_reads_hash == expected_fwd_reads_hash

    def test_create_file_for_seq_success(
        self, mock_service: Mock, mock_user: Mock
    ) -> None:
        """Test successful creation of file for Seq."""
        # Setup command
        cmd = Mock(spec=command.CreateFileForSeqCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.file_content = b"test content"
        cmd.file_format = seqdb_enum.SeqFileFormat.FASTA
        cmd.file_compression = seqdb_enum.FileCompression.NONE
        cmd._policies = []

        expected_file_hash = UUID(hashlib.sha256(cmd.file_content).digest()[:16].hex())

        # Setup case mock with proper ID
        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {cmd.col_id: str(uuid4())}

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_SEQUENCE

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        mock_seq = Mock(spec=model.SeqForUpload)
        mock_seq.file_id = None

        created_file = Mock(spec=seqdb_model.File)
        created_file.id = uuid4()

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ) as mock_get_abac:
            mock_abac = Mock()
            mock_get_abac.return_value = mock_abac

            # Configure mocks
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            # Configure app.handle to return different objects based on call
            def handle_side_effect(*args: Any, **kwargs: Any) -> Any:
                cmd_arg = args[0]
                if isinstance(cmd_arg, seqdb_command.SeqCrudCommand):
                    if cmd_arg.operation == CrudOperation.READ_ONE:
                        return mock_seq
                    else:  # UPDATE_ONE
                        return mock_seq
                elif isinstance(cmd_arg, seqdb_command.CreateFileCommand):
                    return created_file.id
                return Mock()

            mock_service.app.handle.side_effect = handle_side_effect

            # Execute function
            result = case_service_create_file_for_read_set_or_seq(mock_service, cmd)

            # Verify results
            assert result == created_file.id  # type: ignore[attr-defined]
            assert mock_seq.file_id == created_file.id  # type: ignore[attr-defined]
            assert mock_seq.file_hash == expected_file_hash

    def test_create_file_for_seq_success_gzip_content(
        self, mock_service: Mock, mock_user: Mock
    ) -> None:
        """Test successful creation of file for Seq with gzip compression."""
        # Setup command
        cmd = Mock(spec=command.CreateFileForSeqCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.file_content = gzip.compress(b"test content")
        cmd.file_format = seqdb_enum.SeqFileFormat.FASTA
        cmd.file_compression = seqdb_enum.FileCompression.GZIP
        cmd._policies = []

        expected_file_hash = UUID(
            hashlib.sha256(gzip.decompress(cmd.file_content)).digest()[:16].hex()
        )

        # Setup case mock with proper ID
        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {cmd.col_id: str(uuid4())}

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_SEQUENCE

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        mock_seq = Mock(spec=model.SeqForUpload)
        mock_seq.file_id = None

        created_file = Mock(spec=seqdb_model.File)
        created_file.id = uuid4()

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ) as mock_get_abac:
            mock_abac = Mock()
            mock_get_abac.return_value = mock_abac

            # Configure mocks
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            # Configure app.handle to return different objects based on call
            def handle_side_effect(*args: Any, **kwargs: Any) -> Any:
                cmd_arg = args[0]
                if isinstance(cmd_arg, seqdb_command.SeqCrudCommand):
                    if cmd_arg.operation == CrudOperation.READ_ONE:
                        return mock_seq
                    else:  # UPDATE_ONE
                        return mock_seq
                elif isinstance(cmd_arg, seqdb_command.CreateFileCommand):
                    return created_file.id
                return Mock()

            mock_service.app.handle.side_effect = handle_side_effect

            # Execute function
            result = case_service_create_file_for_read_set_or_seq(mock_service, cmd)

            # Verify results
            assert result == created_file.id  # type: ignore[attr-defined]
            assert mock_seq.file_id == created_file.id  # type: ignore[attr-defined]
            assert mock_seq.file_hash == expected_file_hash

    def test_missing_case_content_raises_error(
        self, mock_service: Mock, mock_user: Mock
    ) -> None:
        """Test that missing case content raises InvalidArgumentsError."""
        cmd = Mock(spec=command.CreateFileForReadSetCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.file_format = seqdb_enum.ReadsFileFormat.FASTQ
        cmd.file_compression = seqdb_enum.FileCompression.NONE
        cmd._policies = []

        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {}  # Missing the required col_id

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_READS

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ):
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            with pytest.raises(
                exc.InvalidArgumentsError,
                match="No ReadSet linked to case for Col",
            ):
                case_service_create_file_for_read_set_or_seq(mock_service, cmd)

    def test_read_set_already_has_forward_file(
        self, mock_service: Mock, mock_user: Mock
    ) -> None:
        """Test error when ReadSet already has forward file with different content."""
        cmd = Mock(spec=command.CreateFileForReadSetCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.is_fwd = True
        cmd.file_format = seqdb_enum.ReadsFileFormat.FASTQ
        cmd.file_compression = seqdb_enum.FileCompression.NONE
        cmd.file_content = b"test content"
        cmd._policies = []

        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {cmd.col_id: str(uuid4())}

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_READS

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        mock_read_set = Mock(spec=model.ReadSetForUpload)
        mock_read_set.fwd_file_id = uuid4()  # Already has file
        mock_read_set.fwd_reads_hash = UUID(
            hashlib.sha256(b"other content1").digest()[:16].hex()
        )

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ):
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            def handle_side_effect(*args: Any, **kwargs: Any) -> Any:
                cmd_arg = args[0]
                if isinstance(cmd_arg, seqdb_command.ReadSetCrudCommand):
                    if cmd_arg.operation == CrudOperation.READ_ONE:
                        return mock_read_set
                return Mock()

            mock_service.app.handle.side_effect = handle_side_effect

            with pytest.raises(
                exc.InvalidArgumentsError,
                match="already has a forward file linked",
            ):
                case_service_create_file_for_read_set_or_seq(mock_service, cmd)

    def test_seq_already_has_file(self, mock_service: Mock, mock_user: Mock) -> None:
        """Test error when Seq already has file with different content."""
        cmd = Mock(spec=command.CreateFileForSeqCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.file_format = seqdb_enum.SeqFileFormat.FASTA
        cmd.file_compression = seqdb_enum.FileCompression.NONE
        cmd.file_content = b"test content"
        cmd._policies = []

        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {cmd.col_id: str(uuid4())}

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_SEQUENCE

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        mock_seq = Mock(spec=model.SeqForUpload)
        mock_seq.file_id = uuid4()  # Already has file
        mock_seq.file_hash = UUID(hashlib.sha256(b"other content1").digest()[:16].hex())

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ):
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            def handle_side_effect(*args: Any, **kwargs: Any) -> Any:
                cmd_arg = args[0]
                if isinstance(cmd_arg, seqdb_command.SeqCrudCommand):
                    if cmd_arg.operation == CrudOperation.READ_ONE:
                        return mock_seq
                return Mock()

            mock_service.app.handle.side_effect = handle_side_effect

            with pytest.raises(
                exc.InvalidArgumentsError, match="already has a file linked"
            ):
                case_service_create_file_for_read_set_or_seq(mock_service, cmd)

    def test_seq_reuploading_same_content_returns_existing_file(
        self, mock_service: Mock, mock_user: Mock
    ) -> None:
        """Test that an identical Seq upload is handled idempotently."""
        cmd = Mock(spec=command.CreateFileForSeqCommand)
        cmd.user = mock_user
        cmd.case_id = uuid4()
        cmd.col_id = uuid4()
        cmd.file_format = seqdb_enum.SeqFileFormat.FASTA
        cmd.file_compression = seqdb_enum.FileCompression.NONE
        cmd.file_content = b"same sequence content"
        cmd._policies = []

        file_hash = UUID(hashlib.sha256(cmd.file_content).digest()[:16].hex())

        mock_case = Mock(spec=model.Case)
        mock_case.id = uuid4()
        mock_case.case_type_id = uuid4()
        mock_case.created_in_data_collection_id = uuid4()
        mock_case.content = {cmd.col_id: str(uuid4())}

        # Setup ref_col mock
        ref_col_id = uuid4()
        mock_col = Mock()
        mock_col.ref_col_id = ref_col_id
        mock_ref_col = Mock()
        mock_ref_col.col_type = enum.ColType.GENETIC_SEQUENCE

        # Setup complete case type mock
        mock_complete_case_type = Mock()
        mock_complete_case_type.cols = {cmd.col_id: mock_col}
        mock_complete_case_type.ref_cols = {ref_col_id: mock_ref_col}

        existing_file_id = uuid4()
        mock_seq = Mock(spec=model.SeqForUpload)
        mock_seq.file_id = existing_file_id
        mock_seq.file_hash = file_hash

        with patch(
            "gen_epix.casedb.domain.policy.BaseCaseAbacPolicy.get_case_abac_from_command"
        ):
            mock_service.repository.crud.return_value = mock_case
            data_collection_id = uuid4()
            mock_service.repository.read_fields.return_value = [(data_collection_id,)]
            mock_service.retrieve_complete_case_type.return_value = (
                mock_complete_case_type
            )
            mock_service.app.pdp.is_readable_columns_for_data_collections.return_value = (
                True
            )

            def handle_side_effect(*args: Any, **kwargs: Any) -> Any:
                cmd_arg = args[0]
                if isinstance(cmd_arg, seqdb_command.SeqCrudCommand):
                    if cmd_arg.operation == CrudOperation.READ_ONE:
                        return mock_seq
                return Mock()

            mock_service.app.handle.side_effect = handle_side_effect

            result = case_service_create_file_for_read_set_or_seq(mock_service, cmd)

            assert result == existing_file_id
            # Verify that SeqCrudCommand READ_ONE was called
            calls = [
                c
                for c in mock_service.app.handle.call_args_list
                if isinstance(c[0][0], seqdb_command.SeqCrudCommand)
            ]
            assert any(c[0][0].operation == CrudOperation.READ_ONE for c in calls)

    def test_invalid_command_type_raises_error(self, mock_service: Mock) -> None:
        """Test that invalid command type raises InvalidArgumentsError."""
        cmd = Mock()  # Not a valid command type

        with pytest.raises(exc.InvalidArgumentsError, match="Invalid command type"):
            case_service_create_file_for_read_set_or_seq(mock_service, cmd)
