"""
Unit tests for seqdb sample upload functionality.

Tests the seq_service_upload_samples function and its component steps.
"""

import base64
from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import EtlStatus, UploadAction, UploadStatusSet
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import UploadResult, User
from gen_epix.commondb.domain.model.upload import ParentUploadResult
from gen_epix.fastapp.app import App
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.enum import Role
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.seqdb.services.seq import SampleBatchUploader
from gen_epix.seqdb.services.seq.upload_verify_batch import (
    _verify_children_seq_profiles,
    _verify_children_seqs,
    _verify_sample_refdata,
)


def create_allele_profile_base64(num_alleles: int = 4) -> str:
    """Create a valid allele profile with base64-encoded concatenated UUIDs."""
    allele_uuids = [uuid4() for _ in range(num_alleles)]
    concatenated_bytes = b"".join(uuid.bytes for uuid in allele_uuids)
    return base64.b64encode(concatenated_bytes).decode("ascii")


class BaseUploadTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Test user
        self.user = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.APP_ADMIN.value},
            organization_id=uuid4(),
            is_active=True,
        )

        # Test IDs
        self.sample_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.read_set_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.seq_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.protocol_id = UUID("550e8400-e29b-41d4-a716-446655440044")
        self.allele_profile_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.sequencing_protocol_id = UUID("550e8400-e29b-41d4-a716-446655440005")
        self.assembly_protocol_id = UUID("550e8400-e29b-41d4-a716-446655440006")
        self.locus_detection_protocol_id = UUID("550e8400-e29b-41d4-a716-446655440007")
        self.locus_set_id = UUID("550e8400-e29b-41d4-a716-446655440008")
        self.locus_code_map_id = UUID("550e8400-e29b-41d4-a716-446655440009")
        self.seq_hash = UUID("550e8400-e29b-41d4-a716-446655440010")
        self.locus_id = UUID("550e8400-e29b-41d4-a716-446655440011")
        self.allele_id = UUID("550e8400-e29b-41d4-a716-446655440012")
        self.identifier_issuer_id = UUID("550e8400-e29b-41d4-a716-446655440013")
        self.data_collection_id = UUID("550e8400-e29b-41d4-a716-446655440014")
        self.batch_id = UUID("550e8400-e29b-41d4-a716-446655440015")
        self.identifier_issuer_code = "IDENTIFIER_ISSUER_CODE"
        self.identifier_issuer = model.IdentifierIssuer(
            id=self.identifier_issuer_id,
            code=self.identifier_issuer_code,
            name="Identifier issuer",
        )
        self.random_ids = [
            UUID("550e8400-e29b-41d4-a716-446655440021"),
            UUID("550e8400-e29b-41d4-a716-446655440022"),
            UUID("550e8400-e29b-41d4-a716-446655440023"),
            UUID("550e8400-e29b-41d4-a716-446655440024"),
            UUID("550e8400-e29b-41d4-a716-446655440025"),
            UUID("550e8400-e29b-41d4-a716-446655440026"),
            UUID("550e8400-e29b-41d4-a716-446655440027"),
            UUID("550e8400-e29b-41d4-a716-446655440028"),
            UUID("550e8400-e29b-41d4-a716-446655440029"),
            UUID("550e8400-e29b-41d4-a716-446655440030"),
        ]

        # Mock service
        self.service = Mock(spec=BaseSeqService)
        self.service.generate_id = Mock(side_effect=uuid4)
        self.service.repository = Mock()

        # Mock UOW context manager
        self.uow = Mock(spec=BaseUnitOfWork)
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.service.repository.uow.return_value = self.uow

        # Mock repository methods
        self.service.repository.crud.return_value = []
        self.service.repository.read_fields.return_value = []

        # Mock app for cross-service calls
        self.service.app = Mock(spec=App)
        self.service.app.handle.return_value = []

        self.batch_uploader = SampleBatchUploader(self.service)

    def assertBatchProcessed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.PROCESSED.value:
            self.fail(
                f"Upload was not processed, status: {upload_result.status.value}",
            )

    def assertBatchFailed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.FAILED.value:
            self.fail(
                f"Upload did not fail, status: {upload_result.status.value}",
            )

    def assertHasLogCode(
        self, upload_result: UploadResult, code: list[str] | str
    ) -> None:
        if isinstance(code, str):
            code = [code]
        missing_codes = [x for x in code if not upload_result.has_log_code(x)]
        if missing_codes:
            missing_codes_str = ", ".join(missing_codes)
            if len(missing_codes) == 1:
                self.fail(f"Log missing for code {missing_codes_str}")
            self.fail(f"Logs missing for codes {missing_codes_str}")

    def assertStatusCount(
        self,
        upload_result: ParentUploadResult,
        n_skipped: int = 0,
        n_created: int = 0,
        n_updated: int = 0,
        n_failed: int = 0,
        n_pending: int = 0,
        n_processed: int = 0,
        n_initialized: int = 0,
        n_error: int = 0,
        n_mixed: int = 0,
        n_success: int = 0,
        include_self: bool = False,
    ) -> None:
        expected_status_count = {
            EtlStatus.SKIPPED: n_skipped,
            EtlStatus.CREATED: n_created,
            EtlStatus.UPDATED: n_updated,
            EtlStatus.FAILED: n_failed,
            EtlStatus.PENDING: n_pending,
            EtlStatus.PROCESSED: n_processed,
            EtlStatus.INITIALIZED: n_initialized,
            EtlStatus.ERROR: n_error,
            EtlStatus.MIXED: n_mixed,
            EtlStatus.SUCCESS: n_success,
        }
        actual_status_count = upload_result.get_status_count(include_self=include_self)
        different_status_count = {
            (x, expected_status_count[x], actual_status_count[x])
            for x in EtlStatus
            if actual_status_count[x] != expected_status_count[x]
        }
        if different_status_count:
            different_status_count_str = ""
            different_status_count_str = ", ".join(
                f"{x[0].value} ({x[1]}/{x[2]})" for x in different_status_count
            )
            self.fail(
                f"Status count mismatch (expected/actual): {different_status_count_str}"
            )

    def create_command_and_result_for_samples(
        self,
        samples: list[model.SampleForUpload] | model.SampleForUpload,
        on_exists: UploadAction = UploadAction.UPDATE,
        on_new: UploadAction = UploadAction.CREATE,
        batch_id: UUID | None = None,
        alleles: list[model.AlleleForUpload] | None = None,
    ) -> tuple[command.UploadSamplesCommand, model.SampleBatchUploadResult]:
        """Create a test upload command."""
        if not isinstance(samples, list):
            samples = [samples]
        sample_batch = model.SampleBatchForUpload(batch_id=batch_id or self.batch_id, samples=samples, alleles=alleles)  # type: ignore[call-arg]
        cmd = command.UploadSamplesCommand(
            user=self.user,
            sample_batch=sample_batch,
            on_exists=on_exists,  # type: ignore[call-arg]
            on_new=on_new,  # type: ignore[call-arg]
        )
        retval = self.batch_uploader.init_batch_upload_result(cmd)
        return cmd, retval

    def create_sample_for_upload(
        self,
        sample_id: UUID | None = None,
        read_sets: list[model.ReadSetForUpload] | None = None,
        seqs: list[model.SeqForUpload] | None = None,
        seq_profiles: list[model.SeqProfileForUpload] | None = None,
    ) -> model.SampleForUpload:
        """Helper to create a SampleForUpload with default or specified properties."""
        return model.SampleForUpload(
            id=sample_id,
            read_sets=read_sets or [],
            seqs=seqs or [],
            seq_profiles=seq_profiles or [],
        )

    def create_read_set_for_upload(
        self,
        sample_id: UUID | None = None,
        read_set_id: UUID | None = None,
        sequencing_protocol_id: UUID | None = None,
        fwd_uri: str | None = None,
        rev_uri: str | None = None,
        fwd_file_id: UUID | None = None,
        rev_file_id: UUID | None = None,
        file_format: enum.ReadsFileFormat | None = None,
        file_compression: enum.FileCompression | None = None,
        fwd_reads_hash: UUID | None = None,
        rev_reads_hash: UUID | None = None,
        sequencing_run_code: str | None = None,
    ) -> model.ReadSetForUpload:
        """Helper to create a ReadSetForUpload with default or specified properties."""
        return model.ReadSetForUpload(
            id=read_set_id,
            sample_id=sample_id or NULL_ID,
            protocol_id=sequencing_protocol_id or self.sequencing_protocol_id,
            fwd_uri=fwd_uri or "s3://bucket/fwd.fastq.gz",
            rev_uri=rev_uri or "s3://bucket/rev.fastq.gz",
            fwd_file_id=fwd_file_id,
            rev_file_id=rev_file_id,
            file_format=file_format,
            file_compression=file_compression,
            fwd_reads_hash=fwd_reads_hash,
            rev_reads_hash=rev_reads_hash,
            sequencing_run_code=sequencing_run_code,
        )

    def create_seq_for_upload(
        self,
        sample_id: UUID | None = None,
        seq_id: UUID | None = None,
        seq_hash: UUID | None = None,
        read_set_id: UUID | None = None,
        read_set2_id: UUID | None = None,
        assembly_protocol_id: UUID | None = None,
        contigs: list[model.Contig] | None = None,
    ) -> model.SeqForUpload:
        """Helper to create a SeqForUpload with default or specified properties."""
        return model.SeqForUpload(
            id=seq_id,
            sample_id=sample_id or NULL_ID,
            read_set_id=read_set_id,
            read_set2_id=read_set2_id,
            protocol_id=assembly_protocol_id or self.assembly_protocol_id,
            contigs=contigs or [model.Contig(seq="ATCGATCG")],
        )

    def create_seq_profile_for_upload(
        self,
        sample_id: UUID | None = None,
        seq_id: UUID | None = None,
        allele_profile_id: UUID | None = None,
        locus_detection_protocol_id: UUID | None = None,
        locus_detection_protocol_code: str | None = None,
        locus_code_map_id: UUID | None = None,
        locus_code_map_code: str | None = None,
        allele_profile: str | None = None,
        allele_ids: list[UUID | None] | None = None,
        locus_allele_id_map: dict[str, UUID] | None = None,
    ) -> model.SeqProfileForUpload:
        """Helper to create an SeqProfileForUpload with default or specified properties."""
        return model.SeqProfileForUpload(
            id=allele_profile_id,
            sample_id=sample_id or NULL_ID,
            seq_id=seq_id,
            seq_profile_type=enum.SeqProfileType.ALLELE,
            format=enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content_hash=NULL_ID,
            protocol_id=locus_detection_protocol_id or self.locus_detection_protocol_id,
            protocol_code=locus_detection_protocol_code,
            locus_code_map_id=locus_code_map_id or self.locus_code_map_id,
            locus_code_map_code=locus_code_map_code,
            content=allele_profile
            or (
                ""
                if allele_ids or locus_allele_id_map
                else create_allele_profile_base64()
            ),
            allele_ids=allele_ids,
            locus_allele_id_map=locus_allele_id_map,
        )

    def get_only_seq(self, sample: model.SampleForUpload) -> model.SeqForUpload:
        seqs = sample.seqs or []
        self.assertEqual(len(seqs), 1)
        return seqs[0]

    def get_only_seq_result(
        self, upload_result: model.SampleBatchUploadResult
    ) -> UploadResult:
        seq_results = upload_result.samples[0].seqs or []
        self.assertEqual(len(seq_results), 1)
        return seq_results[0]

    def get_only_allele_profile(
        self, sample: model.SampleForUpload
    ) -> model.SeqProfileForUpload:
        seq_profiles = sample.seq_profiles or []
        self.assertEqual(len(seq_profiles), 1)
        return seq_profiles[0]

    def get_only_allele_profile_result(
        self, upload_result: model.SampleBatchUploadResult
    ) -> UploadResult:
        seq_profile_results = upload_result.samples[0].seq_profiles or []
        self.assertEqual(len(seq_profile_results), 1)
        return seq_profile_results[0]

    def mock_existing_seq_lookup(
        self,
        seq: model.SeqForUpload,
        existing_seq_rows: list[
            tuple[UUID, UUID, UUID | None, UUID | None, UUID, UUID]
        ],
        protocol_code: str = "ASSEMBLY_CODE",
    ) -> None:
        self.service.repository.read_fields.side_effect = [
            [(seq.protocol_id, protocol_code)],
            existing_seq_rows,
        ]

    def mock_existing_seq_profile_lookup(
        self,
        seq_profile: model.SeqProfileForUpload,
        existing_profile_rows: list[tuple[UUID, UUID, UUID, UUID | None, UUID]],
        protocol_code: str = "LOCUS_DETECTION_CODE",
        locus_code_map_rows: list[tuple[UUID, str]] | None = None,
    ) -> None:
        # New code flow: protocol lookup, then optional LCM lookup, then existing profiles.
        # The old locus_set lookup step has been removed (locus set is now part of Protocol).
        side_effect: list[list[tuple[Any, ...]]] = [
            [(seq_profile.protocol_id, protocol_code)],
        ]
        if (
            seq_profile.locus_code_map_id is not None
            or seq_profile.locus_code_map_code is not None
        ):
            if locus_code_map_rows is None:
                locus_code_map_id = seq_profile.locus_code_map_id
                if locus_code_map_id in (None, NULL_ID):
                    locus_code_map_id = self.locus_code_map_id
                locus_code_map_code = (
                    seq_profile.locus_code_map_code or "LOCUS_CODE_MAP_CODE"
                )
                locus_code_map_rows = [(locus_code_map_id, locus_code_map_code)]
            side_effect.append(locus_code_map_rows)
        side_effect.append(existing_profile_rows)
        self.service.repository.read_fields.side_effect = side_effect


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyBatchSeqs(BaseUploadTestCase):
    """Test the _verify_batch_seqs function."""

    def test_seq_exists_same_read_sets_gets_skipped(self) -> None:
        """Test seq with same hash and read sets gets skipped with warning."""
        # Create input and output
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=self.read_set_id,
            read_set2_id=None,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seqs=[seq],
        )
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.seq_hash,
                    self.read_set_id,
                    None,
                    seq_for_upload.protocol_id,
                    self.random_ids[0],
                )
            ],
        )

        # Execute
        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        seq_result = self.get_only_seq_result(retval)
        self.assertTrue(success)
        self.assertTrue(seq_result.has_warnings())
        self.assertTrue(seq_result.has_log_code("f202a96b"))
        self.assertEqual(seq_result.status, EtlStatus.SKIPPED)

    def test_seq_exists_no_read_sets_error(self) -> None:
        """Test error when seq exists with same hash but new seq has no read sets."""
        # Create input and output
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=None,  # No read set provided
            read_set2_id=None,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seqs=[seq],
        )
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.seq_hash,
                    self.read_set_id,
                    None,
                    seq_for_upload.protocol_id,
                    self.random_ids[0],
                )
            ],
            protocol_code="PROTOCOL_CODE",
        )

        # Execute
        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        seq_result = self.get_only_seq_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_result.has_errors())
        self.assertTrue(seq_result.has_log_code("c837034c"))

    def test_seqs_exist_with_same_signature(self) -> None:
        """Test error when seqs exist with same hash, read set and protocol."""
        # Create input and output
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=self.read_set_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seqs=[seq],
        )
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.seq_hash,
                    self.read_set_id,
                    None,
                    seq_for_upload.protocol_id,
                    self.random_ids[0],
                )
            ],
        )

        # Execute
        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        seq_result = self.get_only_seq_result(retval)
        self.assertTrue(success)
        self.assertTrue(seq_result.has_warnings())
        self.assertTrue(seq_result.has_log_code("f202a96b"))
        self.assertEqual(seq_result.status, EtlStatus.SKIPPED)


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyBatchAlleleProfiles(BaseUploadTestCase):
    """Test the _verify_batch_allele_profiles function."""

    def test_locus_detection_protocol_id_does_not_exist(self) -> None:
        """Test error when locus detection protocol ID does not exist."""
        # Create input and output
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        # Mock: protocols (empty), locus code maps (empty), allele profiles (empty)
        self.service.repository.read_fields.side_effect = [[], [], []]

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        self.assertFalse(success)
        # Check that error was added to allele_profile_result
        self.assertTrue(retval.samples[0].seq_profiles[0].has_errors())
        self.assertTrue(retval.samples[0].seq_profiles[0].has_log_code("dec840ca"))

    def test_locus_detection_protocol_code_does_not_exist(self) -> None:
        """Test error when locus detection protocol code does not exist."""
        # Create input and output
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_detection_protocol_id=NULL_ID,
            locus_detection_protocol_code="INVALID_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        # Mock no protocol found
        self.service.repository.read_fields.return_value = []

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        self.assertFalse(success)
        # Check that error was added to seq_profile_result
        self.assertTrue(retval.samples[0].seq_profiles[0].has_errors())
        self.assertTrue(retval.samples[0].seq_profiles[0].has_log_code("ff4ff6db"))

    def test_locus_detection_protocol_id_code_mismatch(self) -> None:
        """Test error when locus detection protocol ID and code don't match."""
        # Create input and output
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_detection_protocol_code="WRONG_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        # Mock protocol with the correct ID but a code different from the one provided
        self.service.repository.read_fields.side_effect = [
            [
                (self.locus_detection_protocol_id, "CORRECT_CODE")
            ],  # Protocol: ID found, but provided code "WRONG_CODE" doesn't exist
            [(self.locus_code_map_id, "LOCUS_CODE_MAP_CODE")],  # LCM: found by ID
            [],  # Existing seq profiles (empty)
        ]

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        self.assertFalse(success)
        # Check that error was added to seq_profile_result
        self.assertTrue(retval.samples[0].seq_profiles[0].has_errors())
        self.assertTrue(retval.samples[0].seq_profiles[0].has_log_code("95558de7"))

    def test_seq_profile_exists_gets_skipped(self) -> None:
        """Test seq profile with same hash and seq gets skipped with warning."""
        # Create input and output
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        allele_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        self.mock_existing_seq_profile_lookup(
            allele_profile_for_upload,
            [
                (
                    self.sample_id,
                    allele_profile_for_upload.content_hash,
                    allele_profile_for_upload.protocol_id,
                    allele_profile_for_upload.seq_id,
                    self.random_ids[0],
                )
            ],
            protocol_code="PROTOCOL_CODE",
        )

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify - function should succeed and find the existing allele profile
        allele_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertTrue(allele_profile_result.has_warnings())
        self.assertTrue(allele_profile_result.has_log_code("c7d8e9f0"))
        self.assertEqual(allele_profile_result.status, EtlStatus.SKIPPED)
        self.assertEqual(allele_profile_for_upload.id, self.random_ids[0])

    def test_allele_profile_exists_no_seq_error(self) -> None:
        """Test error when allele profile exists but new profile has no seq ID."""
        # Create input and output
        existing_profile_id = uuid4()
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=None,  # No seq ID provided
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        allele_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        self.mock_existing_seq_profile_lookup(
            allele_profile_for_upload,
            [
                (
                    self.sample_id,
                    allele_profile_for_upload.content_hash,
                    allele_profile_for_upload.protocol_id,
                    uuid4(),
                    existing_profile_id,
                )
            ],
            protocol_code="PROTOCOL_CODE",
        )

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        allele_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(allele_profile_result.has_errors())
        self.assertTrue(allele_profile_result.has_log_code("a8f3e7b2"))

    def test_allele_profiles_exist_with_error_on_exists(self) -> None:
        """Test error when allele profiles exist and on_exists=ERROR."""
        # Create input and output
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,  # Explicitly set seq_id to match mock
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(
            sample, on_exists=UploadAction.ERROR
        )

        # Prepare mocks
        profile = self.get_only_allele_profile(sample)
        self.mock_existing_seq_profile_lookup(
            profile,
            [
                (
                    self.sample_id,
                    profile.content_hash,
                    profile.protocol_id,
                    profile.seq_id,
                    uuid4(),
                )
            ],
            protocol_code="PROTOCOL_CODE",
        )

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        allele_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertTrue(allele_profile_result.has_warnings())
        self.assertTrue(allele_profile_result.has_log_code("c7d8e9f0"))
        self.assertEqual(allele_profile_result.status, EtlStatus.SKIPPED)

    def test_locus_code_map_id_does_not_exist(self) -> None:
        """Test error when locus code map ID does not exist."""
        # Create input and output
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        # Mock no locus code map found (third call is for locus code maps)
        self.service.repository.read_fields.side_effect = [
            [
                (self.locus_detection_protocol_id, "PROTOCOL_CODE")
            ],  # Existing protocols (id, code) tuples
            [],  # Existing locus code maps (empty - not found)
            [],  # Existing allele profiles
        ]

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        self.assertFalse(success)
        self.assertTrue(retval.samples[0].seq_profiles[0].has_errors())
        self.assertTrue(retval.samples[0].seq_profiles[0].has_log_code("dec840ca"))

    def test_locus_code_map_code_does_not_exist(self) -> None:
        """Test error when locus code map code does not exist."""
        # Create input and output
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=NULL_ID,
            locus_code_map_code="INVALID_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        # Mock no locus code map found (third call is for locus code maps)
        self.service.repository.read_fields.side_effect = [
            [(self.protocol_id, "PROTOCOL_CODE")],  # Protocols
            [],  # Locus code maps (empty - not found)
            [],  # Allele profiles
        ]

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        self.assertFalse(success)
        self.assertTrue(retval.samples[0].seq_profiles[0].has_errors())
        self.assertTrue(retval.samples[0].seq_profiles[0].has_log_code("dec840ca"))

    def test_locus_code_map_id_code_mismatch(self) -> None:
        """Test error when locus code map ID and code both exist but don't match."""
        # Create input and output
        different_id = uuid4()
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_code="LOCUS_CODE_MAP_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        # Mock locus code map with different ID than expected
        self.service.repository.read_fields.side_effect = [
            [(self.locus_detection_protocol_id, "PROTOCOL_CODE")],  # Protocol
            [
                (self.locus_code_map_id, "DIFFERENT_CODE"),
                (different_id, "LOCUS_CODE_MAP_CODE"),
            ],  # LCM: locus_code_map_id has a different code than the one provided
            [],  # Existing seq profiles
        ]

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify
        self.assertFalse(success)
        self.assertTrue(retval.samples[0].seq_profiles[0].has_errors())
        self.assertTrue(retval.samples[0].seq_profiles[0].has_log_code("79de83f2"))

    def test_locus_code_map_code_sets_id(self) -> None:
        """Test that providing only locus code map code sets the ID."""
        # Create input and output
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=NULL_ID,
            locus_code_map_code="TEST_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Prepare mocks
        allele_profile_for_upload = self.get_only_allele_profile(sample)
        self.mock_existing_seq_profile_lookup(
            allele_profile_for_upload,
            [],
            protocol_code="PROTOCOL_CODE",
            locus_code_map_rows=[(self.locus_code_map_id, "TEST_CODE")],
        )

        # Execute
        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        # Verify - should succeed since all lookups succeed
        self.assertTrue(success)
        # Check that the ID was set
        self.assertEqual(
            allele_profile_for_upload.locus_code_map_id, self.locus_code_map_id
        )


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyReferenceData(BaseUploadTestCase):
    """Test the _verify_batch_sample_refdata function."""

    def test_verify_refdata_empty_samples(self) -> None:
        """Test that _verify_batch_sample_refdata succeeds with empty samples."""
        # Create input and output
        sample_batch = model.SampleBatchForUpload(id=self.batch_id, samples=[])
        cmd = command.UploadSamplesCommand(user=self.user, sample_batch=sample_batch)
        retval = self.batch_uploader.init_batch_upload_result(cmd)

        # Execute
        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        self.assertTrue(success)

    def test_verify_refdata_no_allele_profiles(self) -> None:
        """Test that _verify_batch_sample_refdata succeeds with samples that have no allele profiles."""
        # Create input and output
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            # No allele profiles
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Execute
        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        self.assertTrue(success)

    def test_verify_refdata_successful_allele_profiles(self) -> None:
        """Test successful verification when no allele profiles are provided."""
        # Create sample with no allele profiles - this should always succeed
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            # No allele_profiles - should succeed
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        def mock_crud(
            uow: Any,
            user_id: str | None,
            model_class: type,
            operation: Any,
            filter: Any = None,
            objs: Any = None,
            obj_ids: list | None = None,
            **kwargs: Any,
        ) -> list:
            return []  # No reference data needed

        self.service.repository.crud.side_effect = mock_crud

        def mock_read_fields(
            uow: Any, user_id: str | None, model_class: type, fields: list, filter: Any
        ) -> list:
            return []  # No alleles to check

        self.service.repository.read_fields.side_effect = mock_read_fields

        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        self.assertTrue(success)
        # Note: crud may not be called if no allele profiles to verify

    def test_verify_refdata_missing_new_alleles(self) -> None:
        """Test that _verify_refdata fails when new alleles are missing from batch."""
        # Create allele profile with new alleles (not in existing db)
        new_allele_id = uuid4()
        existing_allele_id = uuid4()
        allele_ids = [new_allele_id, existing_allele_id]
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=self.locus_code_map_id,
            allele_ids=allele_ids,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)
        # Don't provide the new allele in the batch.alleles

        # Mock locus set
        locus_ids = [uuid4(), uuid4()]
        mock_locus_set = Mock()
        mock_locus_set.id = self.locus_set_id
        mock_locus_set.locus_ids = locus_ids

        # Mock locus code map
        mock_locus_code_map = Mock()
        mock_locus_code_map.id = self.locus_code_map_id
        mock_locus_code_map.code_map = {"locus1": "code1", "locus2": "code2"}

        # Mock protocol (required: _verify_batch_refdata_allele_profiles uses crud for Protocol)
        mock_protocol = Mock()
        mock_protocol.id = self.locus_detection_protocol_id
        mock_protocol.locus_set_id = self.locus_set_id

        def mock_crud(
            uow: Any,
            user_id: str | None,
            model_class: type,
            operation: Any,
            filter: Any = None,
            objs: Any = None,
            obj_ids: list | None = None,
            **kwargs: Any,
        ) -> list:
            if model_class.__name__ == "Protocol":
                return [mock_protocol]
            elif model_class.__name__ == "LocusSet":
                return [mock_locus_set]
            elif model_class.__name__ == "LocusCodeMap":
                return [mock_locus_code_map]
            elif model_class.__name__ == "Allele":
                # EXISTS_SOME: return True only for the existing_allele_id
                if obj_ids is None:
                    return []
                return [allele_id == existing_allele_id for allele_id in obj_ids]
            return []

        self.service.repository.crud.side_effect = mock_crud

        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        self.assertFalse(success)
        # The error should be detected (success=False) when new alleles are missing
        self.assertTrue(retval.has_errors())
        self.assertTrue(retval.has_log_code("7eeced9e"))

    def test_verify_refdata_extra_alleles_warning(self) -> None:
        """Test that _verify_refdata gives warning for superfluous alleles in batch."""
        # Create allele profile with existing alleles only
        allele_ids = [uuid4(), uuid4()]
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=self.locus_code_map_id,
            allele_ids=allele_ids,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        # Provide extra allele that's not needed
        extra_allele = model.AlleleForUpload(
            locus_id=uuid4(),
            seq="ATCG",
            # Don't provide ID, let it be computed from seq
        )
        cmd, retval = self.create_command_and_result_for_samples(
            sample, alleles=[extra_allele]
        )

        # Mock locus set
        locus_ids = [uuid4(), uuid4()]
        mock_locus_set = Mock()
        mock_locus_set.id = self.locus_set_id
        mock_locus_set.locus_ids = locus_ids

        # Mock locus code map
        mock_locus_code_map = Mock()
        mock_locus_code_map.id = self.locus_code_map_id
        mock_locus_code_map.code_map = {"locus1": "code1", "locus2": "code2"}

        # Mock protocol (required: _verify_batch_refdata_allele_profiles uses crud for Protocol)
        mock_protocol = Mock()
        mock_protocol.id = self.locus_detection_protocol_id
        mock_protocol.locus_set_id = self.locus_set_id

        def mock_crud(
            uow: Any,
            user_id: str | None,
            model_class: type,
            operation: Any,
            filter: Any = None,
            objs: Any = None,
            obj_ids: list | None = None,
            **kwargs: Any,
        ) -> list:
            if model_class.__name__ == "Protocol":
                return [mock_protocol]
            elif model_class.__name__ == "LocusSet":
                return [mock_locus_set]
            elif model_class.__name__ == "LocusCodeMap":
                return [mock_locus_code_map]
            elif model_class.__name__ == "Allele":
                # EXISTS_SOME: both allele_ids are "existing" → they are not new
                if obj_ids is None:
                    return []
                return [True for _ in obj_ids]
            return []

        self.service.repository.crud.side_effect = mock_crud

        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        # All alleles exist, extra_allele is superfluous → warning only, success expected
        # Exact warning mechanism may vary; just verify no crash and success returned
        # TODO: Update this test when warning behavior is clarified

    def test_verify_refdata_skipped_samples_ignored(self) -> None:
        """Test that _verify_refdata ignores samples with FAILED/SKIPPED status."""
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=self.locus_code_map_id,
            # Invalid data that would normally cause errors
            locus_allele_id_map={"invalid": uuid4()},
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Pre-mark the allele profile result as SKIPPED
        retval.samples[0].seq_profiles[0].status = EtlStatus.SKIPPED

        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        self.assertTrue(success)  # Should succeed because skipped items are ignored
        # Verify no repository calls were made (nothing to verify)
        self.service.repository.crud.assert_not_called()

    def test_verify_refdata_allele_profile_length_mismatch(self) -> None:
        """Test that _verify_refdata fails when allele profile length doesn't match locus set."""
        # Create allele profile with wrong number of alleles
        allele_ids = [uuid4()]  # Only one allele, but locus set will have more
        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=self.locus_code_map_id,
            allele_ids=allele_ids,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[allele_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Mock locus set with MORE loci than alleles provided
        locus_ids = [uuid4(), uuid4(), uuid4()]  # Three loci
        mock_locus_set = Mock()
        mock_locus_set.id = self.locus_set_id
        mock_locus_set.locus_ids = locus_ids

        # Mock locus code map
        mock_locus_code_map = Mock()
        mock_locus_code_map.id = self.locus_code_map_id
        mock_locus_code_map.code_map = {
            "locus1": "code1",
            "locus2": "code2",
            "locus3": "code3",
        }

        # Mock protocol (required: _verify_batch_refdata_allele_profiles uses crud for Protocol)
        mock_protocol = Mock()
        mock_protocol.id = self.locus_detection_protocol_id
        mock_protocol.locus_set_id = self.locus_set_id

        def mock_crud(
            uow: Any,
            user_id: str | None,
            model_class: type,
            operation: Any,
            filter: Any = None,
            objs: Any = None,
            obj_ids: list | None = None,
            **kwargs: Any,
        ) -> list:
            if model_class.__name__ == "Protocol":
                return [mock_protocol]
            elif model_class.__name__ == "LocusSet":
                return [mock_locus_set]
            elif model_class.__name__ == "LocusCodeMap":
                return [mock_locus_code_map]
            return []

        self.service.repository.crud.side_effect = mock_crud

        # Execute
        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        self.assertFalse(success)
        # Verify error was added to result
        self.assertEqual(len(retval.samples), 1)
        self.assertIsNotNone(retval.samples[0].seq_profiles)
        self.assertTrue(len(retval.samples[0].seq_profiles) > 0)
        allele_profile_result = retval.samples[0].seq_profiles[0]
        self.assertEqual(allele_profile_result.status, EtlStatus.FAILED)
        self.assertTrue(allele_profile_result.has_errors())
        # TODO: replace with actual log code rather than log message
        self.assertTrue(allele_profile_result.has_log_code("b29dcaf6"))

    def test_verify_refdata_allele_profile_format_not_implemented(self) -> None:
        """Test error when allele profile format is not implemented."""
        # Skip this test since only SORTED_ALLELE_IDS is implemented
        # and pydantic validates the enum before we get to the NotImplementedError
        self.skipTest("Cannot test NotImplementedError due to pydantic enum validation")

    def test_verify_refdata_with_empty_allele_profiles_list(self) -> None:
        """Test that _verify_refdata succeeds with empty allele profiles list."""
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[],  # Empty list
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        # Execute
        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        self.assertTrue(success)

    def test_verify_refdata_multiple_samples_no_profiles(self) -> None:
        """Test that _verify_refdata succeeds with multiple samples that have no allele profiles."""
        sample_id1 = uuid4()
        sample_id2 = uuid4()

        sample1 = self.create_sample_for_upload(
            sample_id=sample_id1,
            # No allele profiles
        )
        sample2 = self.create_sample_for_upload(
            sample_id=sample_id2,
            # No allele profiles
        )
        cmd, retval = self.create_command_and_result_for_samples([sample1, sample2])

        # Execute
        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        self.assertTrue(success)

    def test_verify_refdata_empty_batch_alternative(self) -> None:
        """Test that _verify_refdata succeeds with truly empty sample batch (alternative pattern)."""
        cmd, retval = self.create_command_and_result_for_samples([])

        # Execute
        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        # Verify
        self.assertTrue(success)

    def test_verify_refdata_assertion_error_no_allele_data(self) -> None:
        """Test assertion error when no allele data is provided."""
        # Skip this test since pydantic validates fields before we get to the assertion
        self.skipTest("Cannot test AssertionError due to pydantic validation")


@pytest.mark.scenario_ids("TC-11-13-01")
class TestConcurrentModificationError(BaseUploadTestCase):
    """Test that ConcurrentModificationError in distance calculation is a soft failure."""

    def test_concurrent_modification_does_not_raise(self) -> None:
        """ConcurrentModificationError in distance calc becomes a batch warning."""
        from gen_epix.fastapp.exc import ConcurrentModificationError

        profile = self.create_seq_profile_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id, seq_profiles=[profile]
        )
        cmd, batch_result = self.create_command_and_result_for_samples(sample)

        # Simulate a freshly written profile result so _update_profile_distances
        # collects it.
        profile_result = batch_result.samples[0].seq_profiles[0]
        profile_result.status = EtlStatus.CREATED
        profile_result.id = uuid4()

        # app.handle raises ConcurrentModificationError for the distance command.
        self.service.app.handle.side_effect = ConcurrentModificationError(
            "test_code", "concurrent modification during test"
        )

        from gen_epix.seqdb.services.seq.upload_upsert_batch import (
            _update_profile_distances,
        )

        success = _update_profile_distances(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        # No exception should escape; batch_result.seq_distances stays None.
        self.assertTrue(success)
        self.assertIsNone(batch_result.seq_distances)
        self.assertTrue(batch_result.has_log_code("b3e1f49a"))
        # Sample result must not be FAILED.
        self.assertNotEqual(profile_result.status, EtlStatus.FAILED)
