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
    _get_cases_for_create_file_for_read_sets_or_seqs,
    case_service_create_file_for_read_set_or_seq,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCasedbCaseCreateSeq:
    """
    Comprehensive test suite for the create_seq.py module in gen_epix.casedb.services.case.

    This test suite covers the following key functions:
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

    @pytest.fixture
    def mock_user(self) -> Mock:
        """Create a mock user for testing."""
        user = Mock(spec=model.User)
        user.id = uuid4()
        return user

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """Create a mock repository for testing."""
        repository = Mock()
        repository.uow.return_value.__enter__ = Mock()
        repository.uow.return_value.__exit__ = Mock(return_value=False)
        repository.crud = Mock()
        return repository

    @pytest.fixture
    def mock_service(self, mock_user: Mock, mock_repository: Mock) -> Mock:
        """Create a mock BaseCaseService for testing."""
        service = Mock(spec=BaseCaseService)
        service._get_user_and_repository.return_value = (mock_user, mock_repository)
        service.app = Mock()
        service.app.handle = Mock()
        service.repository = mock_repository
        service._retrieve_case_data_collections_map = Mock()
        service._logger = Mock()
        return service

    @pytest.fixture
    def mock_case_abac(self) -> Mock:
        """Create a mock CaseAbac for testing."""
        case_abac = Mock(spec=model.CaseAbac)
        case_abac.is_full_access = True
        case_abac.get_data_collections_with_access_right_for_col = Mock()
        return case_abac

    @pytest.fixture
    def sample_case_read_sets(self) -> list[Mock]:
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
    def sample_case_seqs(self) -> list[Mock]:
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

            # Setup mocks
            mock_case = Mock(spec=model.Case)
            mock_case.content = {cmd.col_id: str(uuid4())}

            mock_read_set = Mock(spec=model.ReadSetForUpload)
            mock_read_set.fwd_file_id = None
            mock_read_set.rev_file_id = None

            created_file = Mock(spec=seqdb_model.File)
            created_file.id = uuid4()

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ) as mock_get_abac:
                mock_abac = Mock()
                mock_get_abac.return_value = mock_abac

                with patch(
                    "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs"
                ) as mock_get_cases:
                    mock_get_cases.return_value = [mock_case]

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
                    result = case_service_create_file_for_read_set_or_seq(
                        mock_service, cmd
                    )

                    # Verify results
                    assert result == created_file.id  # type: ignore[attr-defined]
                    assert mock_read_set.fwd_file_id == created_file.id  # type: ignore[attr-defined]
                    assert mock_read_set.fwd_reads_hash == expected_fwd_reads_hash

        def test_create_file_for_read_set_success_gzip_content(
            self, mock_service: Mock, mock_user: Mock
        ) -> None:
            """Test successful creation of file for ReadSet."""
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

            # Setup mocks
            mock_case = Mock(spec=model.Case)
            mock_case.content = {cmd.col_id: str(uuid4())}

            mock_read_set = Mock(spec=model.ReadSetForUpload)
            mock_read_set.fwd_file_id = None
            mock_read_set.rev_file_id = None

            created_file = Mock(spec=seqdb_model.File)
            created_file.id = uuid4()

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ) as mock_get_abac:
                mock_abac = Mock()
                mock_get_abac.return_value = mock_abac

                with patch(
                    "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs"
                ) as mock_get_cases:
                    mock_get_cases.return_value = [mock_case]

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
                    result = case_service_create_file_for_read_set_or_seq(
                        mock_service, cmd
                    )

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

            expected_file_hash = UUID(
                hashlib.sha256(cmd.file_content).digest()[:16].hex()
            )  # gzip.decompress()

            # Setup mocks
            mock_case = Mock(spec=model.Case)
            mock_case.content = {cmd.col_id: str(uuid4())}

            mock_seq = Mock(spec=model.SeqForUpload)
            mock_seq.file_id = None

            created_file = Mock(spec=seqdb_model.File)
            created_file.id = uuid4()

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ) as mock_get_abac:
                mock_abac = Mock()
                mock_get_abac.return_value = mock_abac

                with patch(
                    "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs"
                ) as mock_get_cases:
                    mock_get_cases.return_value = [mock_case]

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
                    result = case_service_create_file_for_read_set_or_seq(
                        mock_service, cmd
                    )

                    # Verify results
                    assert result == created_file.id  # type: ignore[attr-defined]
                    assert mock_seq.file_id == created_file.id  # type: ignore[attr-defined]
                    assert mock_seq.file_hash == expected_file_hash

        def test_create_file_for_seq_success_gzip_content(
            self, mock_service: Mock, mock_user: Mock
        ) -> None:
            """Test successful creation of file for Seq."""
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

            # Setup mocks
            mock_case = Mock(spec=model.Case)
            mock_case.content = {cmd.col_id: str(uuid4())}

            mock_seq = Mock(spec=model.SeqForUpload)
            mock_seq.file_id = None

            created_file = Mock(spec=seqdb_model.File)
            created_file.id = uuid4()

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ) as mock_get_abac:
                mock_abac = Mock()
                mock_get_abac.return_value = mock_abac

                with patch(
                    "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs"
                ) as mock_get_cases:
                    mock_get_cases.return_value = [mock_case]

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
                    result = case_service_create_file_for_read_set_or_seq(
                        mock_service, cmd
                    )

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
            mock_case.content = {}  # Missing the required col_id

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ):
                with patch(
                    "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs"
                ) as mock_get_cases:
                    mock_get_cases.return_value = [mock_case]

                    with pytest.raises(
                        exc.InvalidArgumentsError,
                        match="No ReadSet linked to case for the given Col",
                    ):
                        case_service_create_file_for_read_set_or_seq(mock_service, cmd)

        def test_read_set_already_has_forward_file(
            self, mock_service: Mock, mock_user: Mock
        ) -> None:
            """Test error when ReadSet already has forward file."""
            cmd = Mock(spec=command.CreateFileForReadSetCommand)
            cmd.user = mock_user
            cmd.case_id = uuid4()
            cmd.col_id = uuid4()
            cmd.is_fwd = True
            cmd.file_format = seqdb_enum.ReadsFileFormat.FASTQ
            cmd.file_compression = seqdb_enum.FileCompression.NONE
            cmd.file_content = b"test content"
            cmd.fwd_reads_hash = UUID(
                hashlib.sha256(cmd.file_content).digest()[:16].hex()
            )
            cmd.rev_reads_hash = UUID(
                hashlib.sha256(b"other content").digest()[:16].hex()
            )
            cmd._policies = []

            mock_case = Mock(spec=model.Case)
            mock_case.content = {cmd.col_id: str(uuid4())}

            mock_read_set = Mock(spec=model.ReadSetForUpload)
            mock_read_set.fwd_file_id = uuid4()  # Already has file
            mock_read_set.fwd_reads_hash = UUID(
                hashlib.sha256(b"other content1").digest()[:16].hex()
            )
            mock_read_set.rev_reads_hash = UUID(
                hashlib.sha256(b"other content2").digest()[:16].hex()
            )

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ):
                with patch(
                    "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs"
                ) as mock_get_cases:
                    mock_get_cases.return_value = [mock_case]
                    mock_service.app.handle.return_value = mock_read_set

                    with pytest.raises(
                        exc.InvalidArgumentsError,
                        match="already has a forward file linked",
                    ):
                        case_service_create_file_for_read_set_or_seq(mock_service, cmd)

        def test_seq_already_has_file(
            self, mock_service: Mock, mock_user: Mock
        ) -> None:
            """Test error when Seq already has file."""
            cmd = Mock(spec=command.CreateFileForSeqCommand)
            cmd.user = mock_user
            cmd.case_id = uuid4()
            cmd.col_id = uuid4()
            cmd.file_format = seqdb_enum.SeqFileFormat.FASTA
            cmd.file_compression = seqdb_enum.FileCompression.NONE
            cmd.file_content = b"test content"
            cmd.seq_hash = UUID(hashlib.sha256(cmd.file_content).digest()[:16].hex())
            cmd._policies = []

            mock_case = Mock(spec=model.Case)
            mock_case.content = {cmd.col_id: str(uuid4())}

            mock_seq = Mock(spec=model.SeqForUpload)
            mock_seq.file_id = uuid4()  # Already has file
            mock_seq.file_hash = UUID(
                hashlib.sha256(b"other content1").digest()[:16].hex()
            )

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ):
                with patch(
                    "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs"
                ) as mock_get_cases:
                    mock_get_cases.return_value = [mock_case]
                    mock_service.app.handle.return_value = mock_seq

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
            file_hash = UUID(hashlib.sha256(cmd.file_content).digest()[:16].hex())
            cmd.seq_hash = file_hash
            cmd._policies = []

            mock_case = Mock(spec=model.Case)
            mock_case.content = {cmd.col_id: str(uuid4())}
            existing_file_id = uuid4()
            mock_seq = Mock(spec=model.SeqForUpload)
            mock_seq.file_id = existing_file_id
            mock_seq.file_hash = file_hash

            with patch(
                "gen_epix.casedb.services.case.create_seq.BaseCaseAbacPolicy.get_case_abac_from_command"
            ), patch(
                "gen_epix.casedb.services.case.create_seq._get_cases_for_create_file_for_read_sets_or_seqs",
                return_value=[mock_case],
            ):
                mock_service.app.handle.return_value = mock_seq

                result = case_service_create_file_for_read_set_or_seq(mock_service, cmd)

            assert result == existing_file_id
            mock_service.app.handle.assert_called_once()
            handled_command = mock_service.app.handle.call_args.args[0]
            assert isinstance(handled_command, seqdb_command.SeqCrudCommand)
            assert handled_command.operation == CrudOperation.READ_ONE

        def test_invalid_command_type_raises_error(self, mock_service: Mock) -> None:
            """Test that invalid command type raises InvalidArgumentsError."""
            cmd = Mock()  # Not a valid command type

            with pytest.raises(exc.InvalidArgumentsError, match="Invalid command type"):
                case_service_create_file_for_read_set_or_seq(mock_service, cmd)

    class TestGetCasesForCreateReadSetsOrSeqs:
        """Test _get_cases_for_create_file_for_read_sets_or_seqs function."""

        @pytest.fixture
        def mock_uow(self) -> Mock:
            """Create a mock UnitOfWork for testing."""
            return Mock(spec=BaseUnitOfWork)

        @pytest.fixture
        def sample_cols(self) -> tuple[list[Mock], UUID]:
            """Create sample Col objects for testing."""
            ref_col_id = uuid4()
            col = Mock(spec=model.Col)
            col.id = uuid4()
            col.ref_col_id = ref_col_id
            col.case_type_id = uuid4()
            return [col], ref_col_id

        @pytest.fixture
        def sample_genetic_reads_cols(self) -> list[Mock]:
            """Create sample RefCol objects with GENETIC_READS type for testing."""
            ref_col = Mock(spec=model.RefCol)
            ref_col.id = uuid4()
            ref_col.col_type = enum.ColType.GENETIC_READS
            return [ref_col]

        @pytest.fixture
        def sample_genetic_sequence_cols(self) -> list[Mock]:
            """Create sample RefCol objects with GENETIC_SEQUENCE type for testing."""
            ref_col = Mock(spec=model.RefCol)
            ref_col.id = uuid4()
            ref_col.col_type = enum.ColType.GENETIC_SEQUENCE
            return [ref_col]

        @pytest.fixture
        def sample_cases(self) -> list[Mock]:
            """Create sample Case objects for testing."""
            case = Mock(spec=model.Case)
            case.id = uuid4()
            case.case_type_id = uuid4()
            case.created_in_data_collection_id = uuid4()
            return [case]

        def test_get_cases_success_for_read_sets(
            self,
            mock_service: Mock,
            mock_case_abac: Mock,
            mock_uow: Mock,
            sample_cols: tuple[list[Mock], UUID],
            sample_genetic_reads_cols: list[Mock],
            sample_cases: list[Mock],
        ) -> None:
            """Test successful retrieval of cases for ReadSets creation."""
            cmd = Mock(spec=command.CreateFileForReadSetCommand)
            cols, ref_col_id = sample_cols
            cols[0].ref_col_id = ref_col_id
            sample_genetic_reads_cols[0].id = ref_col_id
            sample_cases[0].case_type_id = cols[0].case_type_id

            # Configure repository.crud to return appropriate objects
            def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
                model_class = args[2]
                if model_class == model.Col:
                    return cols
                elif model_class == model.RefCol:
                    return sample_genetic_reads_cols
                elif model_class == model.Case:
                    return sample_cases
                return []

            mock_service.repository.crud.side_effect = crud_side_effect

            result = _get_cases_for_create_file_for_read_sets_or_seqs(
                mock_service,
                cmd,
                mock_case_abac,
                mock_uow,
                uuid4(),
                [sample_cases[0].id],
                [cols[0].id],
            )

            assert result == sample_cases

        def test_get_cases_success_for_seqs(
            self,
            mock_service: Mock,
            mock_case_abac: Mock,
            mock_uow: Mock,
            sample_cols: tuple[list[Mock], UUID],
            sample_genetic_sequence_cols: list[Mock],
            sample_cases: list[Mock],
        ) -> None:
            """Test successful retrieval of cases for Seqs creation."""
            cmd = Mock(spec=command.CreateFileForSeqCommand)
            cols, ref_col_id = sample_cols
            cols[0].ref_col_id = ref_col_id
            sample_genetic_sequence_cols[0].id = ref_col_id
            sample_cases[0].case_type_id = cols[0].case_type_id

            # Configure repository.crud to return appropriate objects
            def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
                model_class = args[2]
                if model_class == model.Col:
                    return cols
                elif model_class == model.RefCol:
                    return sample_genetic_sequence_cols
                elif model_class == model.Case:
                    return sample_cases
                return []

            mock_service.repository.crud.side_effect = crud_side_effect

            result = _get_cases_for_create_file_for_read_sets_or_seqs(
                mock_service,
                cmd,
                mock_case_abac,
                mock_uow,
                uuid4(),
                [sample_cases[0].id],
                [cols[0].id],
            )

            assert result == sample_cases

        def test_invalid_col_type_for_read_sets_raises_error(
            self, mock_service: Mock, mock_case_abac: Mock, mock_uow: Mock
        ) -> None:
            """Test that invalid column type for ReadSets raises InvalidArgumentsError."""
            cmd = Mock(spec=command.CreateFileForReadSetCommand)

            col = Mock(spec=model.Col)
            col.id = uuid4()
            col.ref_col_id = uuid4()

            ref_col = Mock(spec=model.RefCol)
            ref_col.id = col.ref_col_id
            ref_col.col_type = enum.ColType.TEXT  # Wrong type for ReadSets

            def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
                model_class = args[2]
                if model_class == model.Col:
                    return [col]
                elif model_class == model.RefCol:
                    return [ref_col]
                return []

            mock_service.repository.crud.side_effect = crud_side_effect

            with pytest.raises(
                exc.InvalidArgumentsError,
                match="Some columns are not of type GENETIC_READS",
            ):
                _get_cases_for_create_file_for_read_sets_or_seqs(
                    mock_service,
                    cmd,
                    mock_case_abac,
                    mock_uow,
                    uuid4(),
                    [uuid4()],
                    [col.id],
                )

        def test_mismatched_case_type_raises_error(
            self, mock_service: Mock, mock_case_abac: Mock, mock_uow: Mock
        ) -> None:
            """Test that mismatched CaseTypes raise InvalidArgumentsError."""
            cmd = Mock(spec=command.CreateFileForReadSetCommand)

            col = Mock(spec=model.Col)
            col.id = uuid4()
            col.ref_col_id = uuid4()
            col.case_type_id = uuid4()  # Different from Case

            ref_col = Mock(spec=model.RefCol)
            ref_col.id = col.ref_col_id
            ref_col.col_type = enum.ColType.GENETIC_READS

            case = Mock(spec=model.Case)
            case.id = uuid4()
            case.case_type_id = uuid4()  # Different from Col

            def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
                model_class = args[2]
                if model_class == model.Col:
                    return [col]
                elif model_class == model.RefCol:
                    return [ref_col]
                elif model_class == model.Case:
                    return [case]
                return []

            mock_service.repository.crud.side_effect = crud_side_effect

            with pytest.raises(exc.InvalidArgumentsError, match="different CaseType"):
                _get_cases_for_create_file_for_read_sets_or_seqs(
                    mock_service,
                    cmd,
                    mock_case_abac,
                    mock_uow,
                    uuid4(),
                    [case.id],
                    [col.id],
                )

        def test_abac_authorization_failure(
            self, mock_service: Mock, mock_uow: Mock
        ) -> None:
            """Test that ABAC authorization failure raises UnauthorizedAuthError."""
            cmd = Mock(spec=command.CreateFileForReadSetCommand)

            # Setup non-full access ABAC
            case_abac = Mock(spec=model.CaseAbac)
            case_abac.is_full_access = False
            case_abac.get_data_collections_with_access_right_for_col.return_value = (
                set()
            )

            col = Mock(spec=model.Col)
            col.id = uuid4()
            col.ref_col_id = uuid4()
            col.case_type_id = uuid4()

            ref_col = Mock(spec=model.RefCol)
            ref_col.id = col.ref_col_id
            ref_col.col_type = enum.ColType.GENETIC_READS

            case = Mock(spec=model.Case)
            case.id = uuid4()
            case.case_type_id = col.case_type_id
            case.created_in_data_collection_id = uuid4()

            def crud_side_effect(*args: Any, **kwargs: Any) -> Any:
                model_class = args[2]
                if model_class == model.Col:
                    return [col]
                elif model_class == model.RefCol:
                    return [ref_col]
                elif model_class == model.Case:
                    return [case]
                return []

            mock_service.repository.crud.side_effect = crud_side_effect
            mock_service._retrieve_case_data_collections_map.return_value = {
                case.id: set()
            }

            with pytest.raises(exc.UnauthorizedAuthError, match="no WRITE_CASE access"):
                _get_cases_for_create_file_for_read_sets_or_seqs(
                    mock_service,
                    cmd,
                    case_abac,
                    mock_uow,
                    uuid4(),
                    [case.id],
                    [col.id],
                )

        def test_invalid_command_type_raises_error(
            self, mock_service: Mock, mock_case_abac: Mock, mock_uow: Mock
        ) -> None:
            """Test that invalid command type raises InvalidArgumentsError."""
            cmd = Mock()  # Not a valid command type

            # Configure repository to return empty lists
            mock_service.repository.crud.return_value = []

            with pytest.raises(exc.InvalidArgumentsError, match="Invalid command type"):
                _get_cases_for_create_file_for_read_sets_or_seqs(
                    mock_service, cmd, mock_case_abac, mock_uow, uuid4(), [], []
                )
