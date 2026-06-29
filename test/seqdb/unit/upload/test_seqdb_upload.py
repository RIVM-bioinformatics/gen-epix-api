"""
Unit tests for seqdb sample upload functionality.

Tests the seq_service_upload_samples function and its component steps.
"""

import base64
from typing import Any, Sequence, cast
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
    _verify_children_seq_classifications,
    _verify_children_seq_profiles,
    _verify_children_seqs,
    _verify_protocol,
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
        self.seq_category_id = UUID("550e8400-e29b-41d4-a716-446655440031")
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
        retval = cast(
            model.SampleBatchUploadResult,
            self.batch_uploader.init_batch_upload_result(cmd),
        )
        return cmd, retval

    def create_sample_for_upload(
        self,
        sample_id: UUID | None = None,
        read_sets: list[model.ReadSetForUpload] | None = None,
        seqs: list[model.SeqForUpload] | None = None,
        seq_taxonomies: list[model.SeqTaxonomy] | None = None,
        seq_profiles: list[model.SeqProfileForUpload] | None = None,
        seq_classifications: list[model.SeqClassificationForUpload] | None = None,
    ) -> model.SampleForUpload:
        """Helper to create a SampleForUpload with default or specified properties."""
        return model.SampleForUpload(
            id=sample_id,
            read_sets=read_sets or [],
            seqs=seqs or [],
            seq_taxonomies=seq_taxonomies or [],
            seq_profiles=seq_profiles or [],
            seq_classifications=seq_classifications or [],
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
        allele_ids: Sequence[UUID | None] | None = None,
        locus_allele_id_map: dict[str, UUID] | None = None,
    ) -> model.SeqProfileForUpload:
        """Helper to create an SeqProfileForUpload with default or specified properties."""
        kwargs: dict[str, Any] = {
            "id": allele_profile_id,
            "sample_id": sample_id or NULL_ID,
            "seq_id": seq_id,
            "seq_profile_type": enum.SeqProfileType.ALLELE,
            "format": enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            "content_hash": NULL_ID,
            "protocol_id": (
                locus_detection_protocol_id or self.locus_detection_protocol_id
            ),
            "protocol_code": locus_detection_protocol_code,
            "locus_code_map_id": locus_code_map_id or self.locus_code_map_id,
            "locus_code_map_code": locus_code_map_code,
            "content": allele_profile
            or (
                ""
                if allele_ids or locus_allele_id_map
                else create_allele_profile_base64()
            ),
            "allele_ids": allele_ids,
            "locus_allele_id_map": locus_allele_id_map,
        }
        return model.SeqProfileForUpload(**kwargs)

    def create_seq_classification_for_upload(
        self,
        sample_id: UUID | None = None,
        seq_id: UUID | None = None,
        protocol_id: UUID | None = None,
        primary_category_id: UUID | None = None,
        primary_category_code: str | None = None,
    ) -> model.SeqClassificationForUpload:
        """Helper to create a SeqClassificationForUpload with default or specified properties."""
        resolved_primary_category_id = primary_category_id
        if resolved_primary_category_id is None:
            # Keep ID unresolved when code-only input is explicitly provided.
            if primary_category_code is not None:
                resolved_primary_category_id = NULL_ID
            else:
                resolved_primary_category_id = self.seq_category_id

        kwargs: dict[str, Any] = {
            "sample_id": sample_id or NULL_ID,
            "seq_id": seq_id,
            "protocol_id": self.protocol_id if protocol_id is None else protocol_id,
            "primary_category_id": resolved_primary_category_id,
            "primary_category_code": primary_category_code,
            "format": enum.SeqClassificationFormat.PRIMARY_CATEGORY_ONLY,
            "content_hash": NULL_ID,
            "content": "",
        }
        return model.SeqClassificationForUpload(**kwargs)

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

    def get_only_seq_classification(
        self, sample: model.SampleForUpload
    ) -> model.SeqClassificationForUpload:
        seq_classifications = sample.seq_classifications or []
        self.assertEqual(len(seq_classifications), 1)
        return seq_classifications[0]

    def get_only_seq_classification_result(
        self, upload_result: model.SampleBatchUploadResult
    ) -> UploadResult:
        seq_classification_results = upload_result.samples[0].seq_classifications or []
        self.assertEqual(len(seq_classification_results), 1)
        return seq_classification_results[0]

    def mock_existing_seq_lookup(
        self,
        seq: model.SeqForUpload,
        existing_seq_rows: list[
            tuple[UUID, UUID, UUID | None, UUID | None, UUID, UUID]
        ],
        protocol_code: str = "ASSEMBLY_CODE",
        read_set_rows: list[tuple[UUID, UUID]] | None = None,
        read_set2_rows: list[tuple[UUID, UUID]] | None = None,
    ) -> None:
        read_set_rows = read_set_rows or []
        read_set2_rows = read_set2_rows or []
        self.service.repository.read_fields.side_effect = [
            [(seq.protocol_id, protocol_code)],
            existing_seq_rows,
            read_set_rows,
            read_set2_rows,
        ]

    def mock_existing_seq_profile_lookup(
        self,
        seq_profile: model.SeqProfileForUpload,
        existing_profile_rows: list[tuple[Any, ...]],
        seq_rows: list[tuple[UUID, UUID]] | None = None,
        protocol_code: str = "LOCUS_DETECTION_CODE",
        locus_code_map_rows: list[tuple[UUID, str]] | None = None,
        **kwargs: Any,
    ) -> None:
        seq_rows = seq_rows or []
        side_effect: list[list[tuple[Any, ...]]] = [
            [(seq_profile.protocol_id, protocol_code)],
        ]
        if (
            seq_profile.locus_code_map_id is not None
            or seq_profile.locus_code_map_code is not None
            or locus_code_map_rows is not None
        ):
            if locus_code_map_rows is None:
                locus_code_map_id = seq_profile.locus_code_map_id
                if locus_code_map_id in (None, NULL_ID):
                    locus_code_map_id = self.locus_code_map_id
                locus_code_map_code = (
                    seq_profile.locus_code_map_code or "LOCUS_CODE_MAP_CODE"
                )
                locus_code_map_rows = [
                    (cast(UUID, locus_code_map_id), locus_code_map_code)
                ]
            side_effect.append(locus_code_map_rows)
        side_effect.extend(
            [
                existing_profile_rows,
                seq_rows,
            ]
        )
        self.service.repository.read_fields.side_effect = side_effect

    def mock_existing_seq_classification_lookup(
        self,
        seq_classification: model.SeqClassificationForUpload,
        existing_seq_classification_rows: list[
            tuple[UUID, UUID, UUID | None, UUID, UUID]
        ],
        seq_rows: list[tuple[UUID, UUID]] | None = None,
        primary_category_rows: list[tuple[UUID, str]] | None = None,
        protocol_code: str = "CLASSIFICATION_CODE",
    ) -> None:
        seq_rows = seq_rows or []
        if primary_category_rows is None:
            if seq_classification.primary_category_id not in (None, NULL_ID):
                primary_category_rows = [
                    (seq_classification.primary_category_id, "PRIMARY_CATEGORY_CODE")
                ]
            else:
                primary_category_rows = []
        self.service.repository.read_fields.side_effect = [
            [(seq_classification.protocol_id, protocol_code)],
            primary_category_rows,
            existing_seq_classification_rows,
            seq_rows,
        ]


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyProtocol(BaseUploadTestCase):
    """Test the _verify_protocol helper."""

    def test_no_protocol_ids_returns_verify_link_result(self) -> None:
        """When no protocol IDs are present, no protocol-type query is needed."""
        seq = self.create_seq_for_upload(sample_id=self.sample_id)
        seq.protocol_id = NULL_ID
        seq.protocol_code = "ASSEMBLY_CODE"
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        cmd, retval = self.create_command_and_result_for_samples(sample)

        cast(Any, self.batch_uploader).verify_link_id = Mock(return_value=False)
        success = _verify_protocol(
            self.batch_uploader, cmd, retval, self.uow, model.Seq
        )

        self.assertFalse(success)
        self.service.repository.crud.assert_not_called()

    def test_valid_seq_protocol_type_succeeds_without_errors(self) -> None:
        """A protocol with ASSEMBLY type is accepted for Seq children."""
        seq = self.create_seq_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        cmd, retval = self.create_command_and_result_for_samples(sample)
        seq_result = self.get_only_seq_result(retval)
        self.service.repository.crud.return_value = [
            Mock(id=seq.protocol_id, protocol_type=enum.ProtocolType.ASSEMBLY)
        ]

        cast(Any, self.batch_uploader).verify_link_id = Mock(return_value=True)
        success = _verify_protocol(
            self.batch_uploader, cmd, retval, self.uow, model.Seq
        )

        self.assertTrue(success)
        self.assertFalse(seq_result.has_errors())

    def test_invalid_seq_protocol_type_adds_error(self) -> None:
        """A non-ASSEMBLY protocol for Seq should be flagged with code a4c9e18b."""
        seq = self.create_seq_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        cmd, retval = self.create_command_and_result_for_samples(sample)
        seq_result = self.get_only_seq_result(retval)
        self.service.repository.crud.return_value = [
            Mock(id=seq.protocol_id, protocol_type=enum.ProtocolType.SEQUENCING)
        ]

        cast(Any, self.batch_uploader).verify_link_id = Mock(return_value=True)
        success = _verify_protocol(
            self.batch_uploader, cmd, retval, self.uow, model.Seq
        )

        self.assertFalse(success)
        self.assertTrue(seq_result.has_errors())
        self.assertTrue(seq_result.has_log_code("a4c9e18b"))

    def test_invalid_type_on_skipped_child_does_not_add_child_error(self) -> None:
        """Skipped children are ignored for per-child error annotation."""
        seq = self.create_seq_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        cmd, retval = self.create_command_and_result_for_samples(sample)
        seq_result = self.get_only_seq_result(retval)
        seq_result.status = EtlStatus.SKIPPED
        self.service.repository.crud.return_value = [
            Mock(id=seq.protocol_id, protocol_type=enum.ProtocolType.SEQUENCING)
        ]

        cast(Any, self.batch_uploader).verify_link_id = Mock(return_value=True)
        success = _verify_protocol(
            self.batch_uploader, cmd, retval, self.uow, model.Seq
        )

        self.assertFalse(success)
        self.assertFalse(seq_result.has_errors())

    def test_user_none_is_forwarded_to_protocol_read(self) -> None:
        """Protocol lookup should use user_id=None when command user is None."""
        seq = self.create_seq_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        cmd, retval = self.create_command_and_result_for_samples(sample)
        cmd = cmd.model_copy(update={"user": None})
        self.service.repository.crud.return_value = [
            Mock(id=seq.protocol_id, protocol_type=enum.ProtocolType.ASSEMBLY)
        ]

        cast(Any, self.batch_uploader).verify_link_id = Mock(return_value=True)
        success = _verify_protocol(
            self.batch_uploader, cmd, retval, self.uow, model.Seq
        )

        self.assertTrue(success)
        self.assertEqual(self.service.repository.crud.call_args.args[1], None)

    def test_unsupported_child_model_class_raises_not_implemented(self) -> None:
        """Mapped but unsupported child classes should raise NotImplementedError."""
        seq = self.create_seq_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        cmd, retval = self.create_command_and_result_for_samples(sample)
        object.__setattr__(
            cmd.sample_batch,
            "get_all_children_for_upload",
            Mock(return_value=[Mock(protocol_id=self.protocol_id)]),
        )
        cast(Any, self.batch_uploader).verify_link_id = Mock(return_value=True)
        with self.assertRaises(NotImplementedError):
            _verify_protocol(
                self.batch_uploader,
                cmd,
                retval,
                self.uow,
                model.PcrMeasurement,
            )


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyChildrenSeqs(BaseUploadTestCase):
    """Test the _verify_children_seqs function."""

    def test_sample_marked_new_is_ignored(self) -> None:
        """When sample is new, seq conflict checks are skipped."""
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=self.read_set_id,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = True

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.protocol_id,
                    seq_for_upload.read_set_id,
                    seq_for_upload.read_set2_id,
                    uuid4(),
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertTrue(success)
        self.assertFalse(seq_result.has_errors())

    def test_no_existing_seqs_for_sample_is_noop(self) -> None:
        """No matching seq rows means function leaves the seq untouched."""
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=self.read_set_id,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_lookup(seq_for_upload, [])

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertTrue(success)
        self.assertFalse(seq_result.has_errors())

    def test_skipped_seq_result_is_ignored(self) -> None:
        """A pre-skipped seq result should not be re-validated."""
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=self.read_set_id,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False
        seq_result = self.get_only_seq_result(retval)
        seq_result.status = EtlStatus.SKIPPED

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.protocol_id,
                    seq_for_upload.read_set_id,
                    seq_for_upload.read_set2_id,
                    uuid4(),
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        self.assertTrue(success)
        self.assertFalse(seq_result.has_errors())

    def test_hash_mismatch_without_read_sets_adds_unknown_read_set_error(self) -> None:
        """Hash mismatch with read sets absent should emit 7c1e9ab4."""
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=None,
            read_set2_id=None,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.protocol_id,
                    None,
                    None,
                    uuid4(),
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_result.has_errors())
        self.assertTrue(seq_result.has_log_code("7c1e9ab4"))

    def test_hash_mismatch_with_read_sets_adds_natural_key_error(self) -> None:
        """Hash mismatch with read sets present should emit 9d3a4f1b."""
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=self.read_set_id,
            read_set2_id=None,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.protocol_id,
                    self.read_set_id,
                    None,
                    uuid4(),
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_result.has_errors())
        self.assertTrue(seq_result.has_log_code("9d3a4f1b"))

    def test_fallback_from_none_read_sets_can_resolve_existing_seq(self) -> None:
        """Fallback key (protocol, None, None) resolves identical seq."""
        existing_seq_id = self.random_ids[0]
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            seq_id=None,
            read_set_id=self.read_set_id,
            read_set2_id=None,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.protocol_id,
                    None,
                    None,
                    seq_for_upload.seq_hash,
                    existing_seq_id,
                )
            ],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertTrue(success)
        self.assertEqual(seq_for_upload.id, existing_seq_id)
        self.assertFalse(seq_result.is_new)
        self.assertEqual(seq_result.id, existing_seq_id)
        self.assertTrue(seq_result.has_log_code("b6e14c9f"))

    def test_temporary_seq_id_is_replaced_and_child_links_are_rewritten(self) -> None:
        """Temporary seq IDs are replaced with DB IDs across child links."""
        temp_seq_id = uuid4()
        existing_seq_id = self.random_ids[1]
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            seq_id=temp_seq_id,
            read_set_id=self.read_set_id,
            read_set2_id=None,
        )
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=temp_seq_id,
        )
        seq_taxonomy = model.SeqTaxonomy(
            id=self.random_ids[5],
            sample_id=self.sample_id,
            seq_id=temp_seq_id,
            protocol_id=self.protocol_id,
            primary_taxon_id=self.random_ids[6],
            format=enum.SeqTaxonomyFormat.TAXONOMY_FORMAT1,
            content_hash=self.random_ids[7],
            content="taxonomy",
        )
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=temp_seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seqs=[seq],
            seq_taxonomies=[seq_taxonomy],
            seq_profiles=[seq_profile],
            seq_classifications=[seq_classification],
        )
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.protocol_id,
                    self.read_set_id,
                    None,
                    seq_for_upload.seq_hash,
                    existing_seq_id,
                )
            ],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertTrue(success)
        self.assertEqual(seq_for_upload.id, existing_seq_id)
        seq_classifications = sample.seq_classifications or []
        seq_taxonomies = sample.seq_taxonomies or []
        seq_profiles = sample.seq_profiles or []
        self.assertEqual(seq_classifications[0].seq_id, existing_seq_id)
        self.assertEqual(seq_taxonomies[0].seq_id, existing_seq_id)
        self.assertEqual(seq_profiles[0].seq_id, existing_seq_id)
        self.assertFalse(seq_result.is_new)
        self.assertEqual(seq_result.id, existing_seq_id)
        self.assertTrue(seq_result.has_log_code("4fa2d87c"))

    def test_read_set_linked_to_other_sample_adds_error(self) -> None:
        """A read_set_id tied to another sample should fail validation."""
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            read_set_id=self.read_set_id,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [],
            read_set_rows=[(self.read_set_id, self.random_ids[8])],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_result.has_errors())
        self.assertTrue(seq_result.has_log_code("e5a19c72"))

    def test_existing_id_is_kept_when_already_matching(self) -> None:
        """When seq.id already matches DB id, no replacement info is logged."""
        existing_seq_id = self.random_ids[2]
        seq = self.create_seq_for_upload(
            sample_id=self.sample_id,
            seq_id=existing_seq_id,
            read_set_id=self.read_set_id,
            read_set2_id=None,
        )
        sample = self.create_sample_for_upload(sample_id=self.sample_id, seqs=[seq])
        seq_for_upload = self.get_only_seq(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_lookup(
            seq_for_upload,
            [
                (
                    self.sample_id,
                    seq_for_upload.protocol_id,
                    self.read_set_id,
                    None,
                    seq_for_upload.seq_hash,
                    existing_seq_id,
                )
            ],
        )

        success = _verify_children_seqs(self.batch_uploader, cmd, retval, self.uow)

        seq_result = self.get_only_seq_result(retval)
        self.assertTrue(success)
        self.assertEqual(seq_for_upload.id, existing_seq_id)
        self.assertFalse(seq_result.is_new)
        self.assertEqual(seq_result.id, existing_seq_id)
        self.assertFalse(seq_result.has_log_code("4fa2d87c"))

    def test_read_set2_only_does_not_use_fallback(self) -> None:
        """Model validation now forbids read_set2_id without read_set_id."""
        self.skipTest(
            "read_set2_id without read_set_id is no longer a valid SeqForUpload"
        )


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyChildrenSeqClassifications(BaseUploadTestCase):
    """Test the _verify_children_seq_classifications function."""

    def test_sample_marked_new_is_ignored(self) -> None:
        """When sample is new, existing-classification checks are skipped."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = True

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    seq_classification_for_upload.seq_id,
                    seq_classification_for_upload.primary_category_id,
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertTrue(success)
        self.assertFalse(seq_classification_result.has_errors())

    def test_no_existing_seq_classifications_for_sample_is_noop(self) -> None:
        """No existing rows means function leaves the item untouched."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(seq_classification_for_upload, [])

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertTrue(success)
        self.assertIsNone(seq_classification_result.id)
        self.assertFalse(seq_classification_result.has_errors())

    def test_skipped_seq_classification_result_is_ignored(self) -> None:
        """A pre-skipped result should not be re-validated."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False
        seq_classification_result = self.get_only_seq_classification_result(retval)
        seq_classification_result.status = EtlStatus.SKIPPED

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    seq_classification_for_upload.seq_id,
                    seq_classification_for_upload.primary_category_id,
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        self.assertTrue(success)
        self.assertFalse(seq_classification_result.has_errors())

    def test_seq_id_linked_to_other_sample_adds_error(self) -> None:
        """A seq_id tied to another sample should fail validation."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [],
            seq_rows=[(self.seq_id, self.random_ids[8])],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_classification_result.has_errors())
        self.assertTrue(seq_classification_result.has_log_code("c1d72e8a"))

    def test_primary_category_mismatch_without_seq_id_adds_unknown_seq_error(
        self,
    ) -> None:
        """Primary category mismatch with unknown seq should emit f2a84c91."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=None,
            primary_category_id=self.seq_category_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    None,
                    self.random_ids[2],
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_classification_result.has_errors())
        self.assertTrue(seq_classification_result.has_log_code("f2a84c91"))

    def test_primary_category_mismatch_with_seq_id_adds_natural_key_error(self) -> None:
        """Primary category mismatch with seq_id should emit 9d3a4f1b."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
            primary_category_id=self.seq_category_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    self.seq_id,
                    self.random_ids[2],
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_classification_result.has_errors())
        self.assertTrue(seq_classification_result.has_log_code("9d3a4f1b"))

    def test_fallback_from_none_seq_id_can_resolve_existing_seq_classification(
        self,
    ) -> None:
        """Fallback key (protocol, None) resolves identical classification."""
        existing_seq_classification_id = self.random_ids[0]
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
            primary_category_id=self.seq_category_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    None,
                    seq_classification_for_upload.primary_category_id,
                    existing_seq_classification_id,
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertTrue(success)
        self.assertEqual(
            seq_classification_for_upload.id,
            existing_seq_classification_id,
        )
        self.assertFalse(seq_classification_result.is_new)
        self.assertEqual(seq_classification_result.id, existing_seq_classification_id)
        self.assertTrue(seq_classification_result.has_log_code("8be3f4a1"))

    def test_temporary_seq_classification_id_is_replaced(
        self,
    ) -> None:
        """Temporary SeqClassification IDs are replaced by existing DB IDs."""
        temp_seq_classification_id = uuid4()
        existing_seq_classification_id = self.random_ids[1]
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
            primary_category_id=self.seq_category_id,
        )
        seq_classification.id = temp_seq_classification_id
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    seq_classification_for_upload.seq_id,
                    seq_classification_for_upload.primary_category_id,
                    existing_seq_classification_id,
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertTrue(success)
        self.assertEqual(
            seq_classification_for_upload.id, existing_seq_classification_id
        )
        self.assertFalse(seq_classification_result.is_new)
        self.assertEqual(seq_classification_result.id, existing_seq_classification_id)
        self.assertTrue(seq_classification_result.has_log_code("d91a7c4e"))

    def test_null_id_seq_id_with_primary_category_mismatch_adds_error(self) -> None:
        """With seq_id=NULL_ID, mismatch is treated as keyed mismatch (9d3a4f1b)."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=NULL_ID,
            primary_category_id=self.seq_category_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    NULL_ID,
                    self.random_ids[3],
                    self.random_ids[4],
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_classification_result.has_errors())
        self.assertTrue(seq_classification_result.has_log_code("9d3a4f1b"))

    def test_existing_id_is_kept_when_already_matching(self) -> None:
        """When id already matches DB id, no replacement info is logged."""
        existing_seq_classification_id = self.random_ids[2]
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
            primary_category_id=self.seq_category_id,
        )
        seq_classification.id = existing_seq_classification_id
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    seq_classification_for_upload.seq_id,
                    seq_classification_for_upload.primary_category_id,
                    existing_seq_classification_id,
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertTrue(success)
        self.assertEqual(
            seq_classification_for_upload.id,
            existing_seq_classification_id,
        )
        self.assertFalse(seq_classification_result.is_new)
        self.assertEqual(seq_classification_result.id, existing_seq_classification_id)
        self.assertFalse(seq_classification_result.has_log_code("d91a7c4e"))

    def test_null_id_seq_id_does_not_use_fallback(self) -> None:
        """Current behavior: fallback is gated by seq_id != NULL_ID."""
        seq_classification = self.create_seq_classification_for_upload(
            sample_id=self.sample_id,
            seq_id=NULL_ID,
            primary_category_id=self.seq_category_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[seq_classification],
        )
        seq_classification_for_upload = self.get_only_seq_classification(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_classification_lookup(
            seq_classification_for_upload,
            [
                (
                    self.sample_id,
                    seq_classification_for_upload.protocol_id,
                    None,
                    seq_classification_for_upload.primary_category_id,
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_classification_result = self.get_only_seq_classification_result(retval)
        self.assertTrue(success)
        self.assertIsNone(seq_classification_result.id)
        self.assertIsNone(seq_classification_result.id)
        self.assertEqual(seq_classification_for_upload.seq_id, NULL_ID)


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyChildrenSeqProfiles(BaseUploadTestCase):
    """Test the _verify_children_seq_profiles function."""

    def test_sample_marked_new_is_ignored(self) -> None:
        """When sample is new, existing-profile checks are skipped."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = True

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    seq_profile_for_upload.seq_id,
                    seq_profile_for_upload.content_hash,
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertFalse(seq_profile_result.has_errors())

    def test_no_existing_seq_profiles_for_sample_is_noop(self) -> None:
        """No existing rows means the profile is left untouched."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(seq_profile_for_upload, [])

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertIsNone(seq_profile_result.id)
        self.assertFalse(seq_profile_result.has_errors())

    def test_skipped_seq_profile_result_is_ignored(self) -> None:
        """A pre-skipped result should not be re-validated."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False
        seq_profile_result = self.get_only_allele_profile_result(retval)
        seq_profile_result.status = EtlStatus.SKIPPED

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    seq_profile_for_upload.seq_id,
                    seq_profile_for_upload.content_hash,
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        self.assertTrue(success)
        self.assertFalse(seq_profile_result.has_errors())

    def test_seq_id_linked_to_other_sample_adds_error(self) -> None:
        """A seq_id tied to another sample should fail validation."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [],
            seq_rows=[(self.seq_id, self.random_ids[8])],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("0f4a9c3d"))

    def test_content_hash_mismatch_without_seq_id_adds_unknown_seq_error(
        self,
    ) -> None:
        """Fallback without seq_id should emit 6b2f8e10."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=None,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    None,
                    self.random_ids[2],
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("6b2f8e10"))

    def test_content_hash_mismatch_with_seq_id_adds_natural_key_error(self) -> None:
        """Mismatch with seq_id should emit c4d8a2f7."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    self.seq_id,
                    self.random_ids[2],
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("c4d8a2f7"))

    def test_null_id_content_hash_with_seq_id_skips_mismatch_error(self) -> None:
        """locus_allele_id_map profile (content_hash=NULL_ID) with seq_id set
        does not trigger a mismatch error when the stored hash differs.

        The client cannot compute the hash without the locus code map, so
        NULL_ID means "unknown" — the upsert phase resolves it later.
        """
        existing_seq_profile_id = self.random_ids[0]
        existing_hash = self.random_ids[2]
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
            locus_allele_id_map={"locus1": self.allele_id},
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    self.seq_id,
                    existing_hash,
                    existing_seq_profile_id,
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertFalse(seq_profile_result.has_errors())
        self.assertFalse(seq_profile_result.has_log_code("c4d8a2f7"))
        self.assertFalse(seq_profile_result.has_log_code("1d7c9b53"))
        self.assertFalse(seq_profile_result.is_new)
        self.assertEqual(seq_profile_result.id, existing_seq_profile_id)

    def test_null_id_content_hash_without_seq_id_skips_mismatch_error(
        self,
    ) -> None:
        """locus_allele_id_map profile (content_hash=NULL_ID) without seq_id
        does not trigger a mismatch error when the stored hash differs.

        Before the fix, comparing NULL_ID against the real stored hash
        incorrectly triggered error 6b2f8e10.
        """
        existing_seq_profile_id = self.random_ids[0]
        existing_hash = self.random_ids[2]
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=None,
            locus_allele_id_map={"locus1": self.allele_id},
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    None,
                    existing_hash,
                    existing_seq_profile_id,
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertFalse(seq_profile_result.has_errors())
        self.assertFalse(seq_profile_result.has_log_code("6b2f8e10"))
        self.assertFalse(seq_profile_result.has_log_code("1d7c9b53"))
        self.assertFalse(seq_profile_result.is_new)
        self.assertEqual(seq_profile_result.id, existing_seq_profile_id)

    def test_fallback_from_none_seq_id_can_resolve_existing_seq_profile(
        self,
    ) -> None:
        """Fallback key (protocol, None) resolves identical profile."""
        existing_seq_profile_id = self.random_ids[0]
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    None,
                    seq_profile_for_upload.content_hash,
                    existing_seq_profile_id,
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertEqual(seq_profile_for_upload.id, existing_seq_profile_id)
        self.assertFalse(seq_profile_result.is_new)
        self.assertEqual(seq_profile_result.id, existing_seq_profile_id)
        self.assertTrue(seq_profile_result.has_log_code("1d7c9b53"))

    def test_null_id_seq_id_does_not_use_fallback(self) -> None:
        """Current behavior: fallback is gated by seq_id != NULL_ID."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=NULL_ID,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    None,
                    seq_profile_for_upload.content_hash,
                    self.random_ids[0],
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertIsNone(seq_profile_result.id)
        self.assertEqual(seq_profile_for_upload.seq_id, NULL_ID)

    def test_temporary_seq_profile_id_is_replaced(self) -> None:
        """Temporary SeqProfile IDs are replaced by existing DB IDs."""
        temp_seq_profile_id = uuid4()
        existing_seq_profile_id = self.random_ids[1]
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        seq_profile.id = temp_seq_profile_id
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    seq_profile_for_upload.seq_id,
                    seq_profile_for_upload.content_hash,
                    existing_seq_profile_id,
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertEqual(seq_profile_for_upload.id, existing_seq_profile_id)
        self.assertFalse(seq_profile_result.is_new)
        self.assertEqual(seq_profile_result.id, existing_seq_profile_id)
        self.assertTrue(seq_profile_result.has_log_code("a7f1c6d8"))

    def test_existing_id_is_kept_when_already_matching(self) -> None:
        """When id already matches DB id, no replacement info is logged."""
        existing_seq_profile_id = self.random_ids[2]
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        seq_profile.id = existing_seq_profile_id
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        seq_profile_for_upload = self.get_only_allele_profile(sample)
        cmd, retval = self.create_command_and_result_for_samples(sample)
        retval.samples[0].is_new = False

        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [
                (
                    self.sample_id,
                    seq_profile_for_upload.protocol_id,
                    seq_profile_for_upload.seq_id,
                    seq_profile_for_upload.content_hash,
                    existing_seq_profile_id,
                )
            ],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertEqual(seq_profile_for_upload.id, existing_seq_profile_id)
        self.assertFalse(seq_profile_result.is_new)
        self.assertEqual(seq_profile_result.id, existing_seq_profile_id)
        self.assertFalse(seq_profile_result.has_log_code("a7f1c6d8"))

    def test_locus_detection_protocol_id_does_not_exist(self) -> None:
        """Error is raised when locus detection protocol ID does not exist."""
        seq_profile = self.create_seq_profile_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        self.service.repository.read_fields.side_effect = [[], [], []]

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("dec840ca"))

    def test_locus_detection_protocol_code_does_not_exist(self) -> None:
        """Error is raised when locus detection protocol code does not exist."""
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

        self.service.repository.read_fields.return_value = []

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("ff4ff6db"))

    def test_locus_detection_protocol_id_code_mismatch(self) -> None:
        """Error is raised when locus detection protocol ID and code mismatch."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_detection_protocol_code="WRONG_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        self.service.repository.read_fields.side_effect = [
            [(self.locus_detection_protocol_id, "CORRECT_CODE")],
            [(self.locus_code_map_id, "LOCUS_CODE_MAP_CODE")],
            [],
        ]

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("95558de7"))

    def test_allele_profiles_exist_with_error_on_exists(self) -> None:
        """Existing identical profile resolves to existing ID for on_exists=ERROR."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            seq_id=self.seq_id,
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(
            sample, on_exists=UploadAction.ERROR
        )
        retval.samples[0].is_new = False

        profile = self.get_only_allele_profile(sample)
        self.mock_existing_seq_profile_lookup(
            profile,
            [
                (
                    self.sample_id,
                    profile.protocol_id,
                    profile.seq_id,
                    profile.content_hash,
                    uuid4(),
                )
            ],
            protocol_code="PROTOCOL_CODE",
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertTrue(success)
        self.assertFalse(seq_profile_result.has_warnings())
        self.assertFalse(seq_profile_result.has_errors())
        self.assertFalse(seq_profile_result.is_new)
        self.assertIsNotNone(seq_profile_result.id)

    def test_locus_code_map_id_does_not_exist(self) -> None:
        """Error is raised when locus code map ID does not exist."""
        seq_profile = self.create_seq_profile_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        self.service.repository.read_fields.side_effect = [
            [(self.locus_detection_protocol_id, "PROTOCOL_CODE")],
            [],
            [],
        ]

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("dec840ca"))

    def test_locus_code_map_code_does_not_exist(self) -> None:
        """Error is raised when locus code map code does not exist."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=NULL_ID,
            locus_code_map_code="INVALID_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        self.service.repository.read_fields.side_effect = [
            [(self.protocol_id, "PROTOCOL_CODE")],
            [],
            [],
        ]

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("dec840ca"))

    def test_locus_code_map_id_code_mismatch(self) -> None:
        """Error is raised when locus code map ID/code mismatch."""
        different_id = uuid4()
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_code="LOCUS_CODE_MAP_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        self.service.repository.read_fields.side_effect = [
            [(self.locus_detection_protocol_id, "PROTOCOL_CODE")],
            [
                (self.locus_code_map_id, "DIFFERENT_CODE"),
                (different_id, "LOCUS_CODE_MAP_CODE"),
            ],
            [],
        ]

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        seq_profile_result = self.get_only_allele_profile_result(retval)
        self.assertFalse(success)
        self.assertTrue(seq_profile_result.has_errors())
        self.assertTrue(seq_profile_result.has_log_code("79de83f2"))

    def test_locus_code_map_code_sets_id(self) -> None:
        """Supplying only locus code map code resolves and sets locus_code_map_id."""
        seq_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_code_map_id=NULL_ID,
            locus_code_map_code="TEST_CODE",
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_profiles=[seq_profile],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        seq_profile_for_upload = self.get_only_allele_profile(sample)
        self.mock_existing_seq_profile_lookup(
            seq_profile_for_upload,
            [],
            protocol_code="PROTOCOL_CODE",
            locus_code_map_rows=[(self.locus_code_map_id, "TEST_CODE")],
        )

        success = _verify_children_seq_profiles(
            self.batch_uploader, cmd, retval, self.uow
        )

        self.assertTrue(success)
        self.assertEqual(
            seq_profile_for_upload.locus_code_map_id,
            self.locus_code_map_id,
        )


@pytest.mark.scenario_ids("TC-11-13-01")
class TestVerifyReferenceData(BaseUploadTestCase):
    """Test the _verify_batch_sample_refdata function."""

    def test_verify_refdata_empty_samples(self) -> None:
        """Test that _verify_batch_sample_refdata succeeds with empty samples."""
        # Create input and output
        sample_batch = model.SampleBatchForUpload(id=self.batch_id, samples=[])
        cmd = command.UploadSamplesCommand(user=self.user, sample_batch=sample_batch)
        retval = cast(
            model.SampleBatchUploadResult,
            self.batch_uploader.init_batch_upload_result(cmd),
        )

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
        allele_ids: list[UUID | None] = [new_allele_id, existing_allele_id]
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
        allele_ids: list[UUID | None] = [uuid4(), uuid4()]
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

        # All profile alleles exist → else-branch clears provided_alleles; extra_allele
        # is dropped silently so _create_sample_refdata skips the wasteful UPSERT_SOME.
        self.assertTrue(success)
        self.assertEqual(cmd.sample_batch.alleles, [])

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
        seq_profile_result = self.get_only_allele_profile_result(retval)
        seq_profile_result.status = EtlStatus.SKIPPED

        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        self.assertTrue(success)  # Should succeed because skipped items are ignored
        # Verify no repository calls were made (nothing to verify)
        self.service.repository.crud.assert_not_called()

    def test_verify_refdata_allele_profile_length_mismatch(self) -> None:
        """Test that _verify_refdata fails when allele profile length doesn't match locus set."""
        # Create allele profile with wrong number of alleles
        allele_ids: list[UUID | None] = [
            uuid4()
        ]  # Only one allele, but locus set will have more
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
        allele_profile_result = self.get_only_allele_profile_result(retval)
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

    def test_locus_allele_id_map_encoded_in_locus_set_order(self) -> None:
        """Alleles must be encoded in locus_ids order, not locus_allele_id_map dict order.

        Dict has code2 (→ locus2 → a2) first; locus_ids has locus1 first.
        A bug that iterates the dict produces [a2, a1]. Correct code produces [a1, a2].
        """
        a1, a2 = uuid4(), uuid4()
        locus1_id, locus2_id = uuid4(), uuid4()

        allele_profile = self.create_seq_profile_for_upload(
            sample_id=self.sample_id,
            locus_allele_id_map={"code2": a2, "code1": a1},  # reversed vs locus_ids
        )
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id, seq_profiles=[allele_profile]
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)

        mock_locus_set = Mock()
        mock_locus_set.id = self.locus_set_id
        mock_locus_set.locus_ids = [locus1_id, locus2_id]  # locus1 first

        mock_locus_code_map = Mock()
        mock_locus_code_map.id = self.locus_code_map_id
        mock_locus_code_map.code_map = {"code1": locus1_id, "code2": locus2_id}

        mock_protocol = Mock()
        mock_protocol.id = self.locus_detection_protocol_id
        mock_protocol.locus_set_id = self.locus_set_id

        def mock_crud(
            uow: Any,
            user_id: Any,
            model_class: type,
            operation: Any,
            filter: Any = None,
            objs: Any = None,
            obj_ids: Any = None,
            **kwargs: Any,
        ) -> Any:
            if model_class.__name__ == "Protocol":
                return [mock_protocol]
            if model_class.__name__ == "LocusSet":
                return [mock_locus_set]
            if model_class.__name__ == "LocusCodeMap":
                return [mock_locus_code_map]
            if model_class.__name__ == "Allele" and obj_ids is not None:
                return [True for _ in obj_ids]  # all alleles already exist
            return []

        self.service.repository.crud.side_effect = mock_crud

        success = _verify_sample_refdata(self.batch_uploader, cmd, retval, self.uow)

        self.assertTrue(success)
        encoded = cmd.sample_batch.samples[0].seq_profiles[0]
        self.assertNotEqual(encoded.content, "")
        content_bytes = base64.b64decode(encoded.content)
        self.assertEqual(content_bytes[0:16], a1.bytes)   # locus1 is first → a1
        self.assertEqual(content_bytes[16:32], a2.bytes)  # locus2 is second → a2

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
        profile_result = self.get_only_allele_profile_result(batch_result)
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

    def test_calculate_distances_false_skips_distance_calculation(self) -> None:
        """When calculate_distances=False, _update_profile_distances returns early
        without calling app.handle, so no SeqDistance records are created."""
        from gen_epix.seqdb.services.seq.upload_upsert_batch import (
            _update_profile_distances,
        )

        profile = self.create_seq_profile_for_upload(sample_id=self.sample_id)
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id, seq_profiles=[profile]
        )
        cmd, batch_result = self.create_command_and_result_for_samples(sample)
        cmd = cmd.model_copy(update={"calculate_distances": False})

        # Simulate a freshly written profile so it would normally be collected.
        profile_result = self.get_only_allele_profile_result(batch_result)
        profile_result.status = EtlStatus.CREATED
        profile_result.id = uuid4()

        success = _update_profile_distances(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        self.assertTrue(success)
        self.assertIsNone(batch_result.seq_distances)
        self.service.app.handle.assert_not_called()


@pytest.mark.scenario_ids("TC-11-14-01")
class TestVerifyBatchSeqClassifications(BaseUploadTestCase):
    """Tests for _verify_children_seq_classifications primary_category_id validation."""

    def _run(
        self, sc: model.SeqClassificationForUpload
    ) -> tuple[bool, model.SampleBatchUploadResult]:
        sample = self.create_sample_for_upload(
            sample_id=self.sample_id,
            seq_classifications=[sc],
        )
        cmd, retval = self.create_command_and_result_for_samples(sample)
        success = _verify_children_seq_classifications(
            self.batch_uploader, cmd, retval, self.uow
        )
        return success, retval

    def test_primary_category_id_not_found(self) -> None:
        """Function returns failure when primary-category link verification fails."""
        sc = self.create_seq_classification_for_upload(
            primary_category_id=self.seq_category_id,
        )
        cast(Any, self.batch_uploader).verify_link_id = Mock(side_effect=[True, False])

        success, retval = self._run(sc)

        seq_classification_results = retval.samples[0].seq_classifications or []
        sc_result = seq_classification_results[0]
        self.assertFalse(success)
        self.assertFalse(sc_result.has_log_code("d91a7c4e"))

    def test_primary_category_code_not_found(self) -> None:
        """Function returns failure when primary-category code cannot be resolved."""
        sc = self.create_seq_classification_for_upload(
            primary_category_code="UNKNOWN_SEROTYPE",
        )
        cast(Any, self.batch_uploader).verify_link_id = Mock(side_effect=[True, False])

        success, retval = self._run(sc)

        seq_classification_results = retval.samples[0].seq_classifications or []
        sc_result = seq_classification_results[0]
        self.assertFalse(success)
        self.assertFalse(sc_result.has_log_code("d91a7c4e"))

    def test_primary_category_code_resolves_to_id(self) -> None:
        """Function succeeds when both protocol and primary-category links verify."""
        sc = self.create_seq_classification_for_upload(
            primary_category_code="TYPHIMURIUM",
        )
        cast(Any, self.batch_uploader).verify_link_id = Mock(side_effect=[True, True])

        success, retval = self._run(sc)

        self.assertTrue(success)
        self.assertFalse(retval.has_errors())
