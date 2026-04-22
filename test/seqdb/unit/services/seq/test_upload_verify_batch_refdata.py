"""
Unit tests for _verify_batch_refdata_snp_profiles.

Tests validate the SNP batch validation logic in
upload_verify_batch_refdata.py.
"""

from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import EtlStatus, UploadAction, UploadStatusSet
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import UploadResult, User
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.enum import Role
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.seqdb.services.seq import SampleBatchUploader
from gen_epix.seqdb.services.seq.upload_verify_batch_refdata import (
    _verify_batch_refdata_snp_profiles,
)


class BaseSnpUploadTestCase(TestCase):
    """Base test case for SNP upload validation."""

    def setUp(self) -> None:
        """Set up test fixtures."""
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
        self.protocol_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.ref_seq_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.batch_id = UUID("550e8400-e29b-41d4-a716-446655440004")

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

        # Mock app
        self.service.app = Mock(spec=App)
        self.service.app.handle.return_value = []

        self.batch_uploader = SampleBatchUploader(self.service)

    def create_snp_profile(
        self,
        protocol_id: UUID | None = None,
        content: str = "",
        aligned_nucleotide_seq: str | None = None,
    ) -> model.SeqProfileForUpload:
        """Create a SNP profile for upload."""
        return model.SeqProfileForUpload.model_construct(
            id=None,
            sample_id=self.sample_id,
            seq_id=None,
            seq_profile_type=enum.SeqProfileType.SNP,
            format=None,
            content_hash=NULL_ID,
            protocol_id=protocol_id or self.protocol_id,
            protocol_code=None,
            locus_code_map_id=None,
            locus_code_map_code=None,
            content=content,
            aligned_nucleotide_seq=aligned_nucleotide_seq,
            allele_ids=None,
            locus_allele_id_map=None,
            repeat_numbers=None,
            locus_repeat_number_map=None,
            kmer_frequency_map=None,
        )

    def create_command_and_result(
        self,
        profiles: list[model.SeqProfileForUpload] | model.SeqProfileForUpload,
        on_exists: UploadAction = UploadAction.UPDATE,
        on_new: UploadAction = UploadAction.CREATE,
    ) -> tuple[
        command.UploadSamplesCommand,
        model.SampleBatchUploadResult,
    ]:
        """Create command and result for profiles.

        Uses model_construct to bypass pydantic
        validation so the function under test is
        exercised directly.
        """
        if not isinstance(profiles, list):
            profiles = [profiles]
        # Bypass pydantic validation; we test
        # the verification function, not model
        # validators.
        sample = model.SampleForUpload.model_construct(
            id=self.sample_id,
            sample=None,
            read_sets=None,
            seqs=None,
            seq_taxonomies=None,
            seq_classifications=None,
            seq_profiles=profiles,
            pcr_measurements=None,
            ast_measurements=None,
            identifiers=None,
        )
        sample_batch = model.SampleBatchForUpload.model_construct(
            batch_id=self.batch_id,
            samples=[sample],
            alleles=None,
        )
        cmd = command.UploadSamplesCommand(
            user=self.user,
            sample_batch=sample_batch,
            on_exists=on_exists,  # type: ignore[call-arg]
            on_new=on_new,  # type: ignore[call-arg]
        )
        retval = self.batch_uploader.init_batch_upload_result(cmd)
        return cmd, retval  # type: ignore[return-value]

    def create_protocol(
        self,
        protocol_id: UUID | None = None,
        ref_seq_id: UUID | None = "USE_DEFAULT",  # type: ignore[assignment]
    ) -> Mock:
        """Create a mock Protocol with ref_seq_id."""
        protocol = Mock()
        protocol.id = protocol_id or self.protocol_id
        protocol.ref_seq_id = (
            self.ref_seq_id if ref_seq_id == "USE_DEFAULT" else ref_seq_id
        )
        return protocol

    def mock_crud_for_snp(
        self,
        protocols: list[Mock],
        ref_seq_exists: list[bool] | None = None,
    ) -> None:
        """Set up repository.crud side_effect."""
        calls: list[Any] = [protocols]
        if ref_seq_exists is not None:
            calls.append(ref_seq_exists)

        self.service.repository.crud.side_effect = calls

    def get_profile_result(
        self,
        batch_result: model.SampleBatchUploadResult,
        sample_idx: int = 0,
        profile_idx: int = 0,
    ) -> UploadResult:
        """Get profile result at given indices."""
        return batch_result.samples[sample_idx].seq_profiles[profile_idx]

    def assertBatchProcessed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.PROCESSED.value:
            self.fail(
                "Upload was not processed," f" status: {upload_result.status.value}"
            )

    def assertBatchFailed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.FAILED.value:
            self.fail("Upload did not fail," f" status: {upload_result.status.value}")

    def assertHasLogCode(
        self,
        upload_result: UploadResult,
        code: list[str] | str,
    ) -> None:
        if isinstance(code, str):
            code = [code]
        missing_codes = [x for x in code if not upload_result.has_log_code(x)]
        if missing_codes:
            missing_str = ", ".join(missing_codes)
            self.fail(f"Log missing for code {missing_str}")


@pytest.mark.scenario_ids("TC-11-13-01")
class TestSnpNoProfiles(BaseSnpUploadTestCase):
    """No SNP profiles → early return."""

    def test_no_snp_profiles_returns_true(
        self,
    ) -> None:
        """Empty batch with no SNP profiles
        returns success."""
        sample = model.SampleForUpload.model_construct(
            id=self.sample_id,
            sample=None,
            read_sets=None,
            seqs=None,
            seq_taxonomies=None,
            seq_classifications=None,
            seq_profiles=[],
            pcr_measurements=None,
            ast_measurements=None,
            identifiers=None,
        )
        sample_batch = model.SampleBatchForUpload.model_construct(
            batch_id=self.batch_id,
            samples=[sample],
            alleles=None,
        )
        cmd = command.UploadSamplesCommand(
            user=self.user,
            sample_batch=sample_batch,
        )
        retval = self.batch_uploader.init_batch_upload_result(cmd)

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,  # type: ignore[arg-type]
            self.uow,
        )

        self.assertTrue(success)
        self.service.repository.crud.assert_not_called()


@pytest.mark.scenario_ids("TC-11-13-01")
class TestSnpValidCases(BaseSnpUploadTestCase):
    """Valid SNP profile scenarios."""

    def test_valid_snp_content_passes(
        self,
    ) -> None:
        """Valid SNP profile with content
        passes and sets format."""
        profile = self.create_snp_profile(content="ACGTN-")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertTrue(success)
        self.assertEqual(
            profile.format,
            enum.SeqProfileFormat.REF_ALN_SEQ,
        )
        pr = self.get_profile_result(retval)
        self.assertFalse(pr.has_errors())

    def test_valid_aligned_nucleotide_seq_converts(
        self,
    ) -> None:
        """aligned_nucleotide_seq is copied to
        content and cleared."""
        profile = self.create_snp_profile(aligned_nucleotide_seq="ACGT")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertTrue(success)
        self.assertEqual(profile.content, "ACGT")
        self.assertIsNone(profile.aligned_nucleotide_seq)
        self.assertEqual(
            profile.format,
            enum.SeqProfileFormat.REF_ALN_SEQ,
        )

    def test_matching_ref_seq_accepted(self) -> None:
        """Existing ref_seq passes validation."""
        profile = self.create_snp_profile(content="ACGT")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertTrue(success)
        # Verify EXISTS_SOME was called for RefSeq
        crud_calls = self.service.repository.crud.call_args_list
        self.assertEqual(len(crud_calls), 2)
        self.assertEqual(crud_calls[1].args[2], model.RefSeq)
        self.assertEqual(
            crud_calls[1].args[3],
            CrudOperation.EXISTS_SOME,
        )

    def test_two_profiles_same_ref_seq_same_length(
        self,
    ) -> None:
        """Two profiles for the same ref_seq with
        equal length both pass."""
        p1 = self.create_snp_profile(content="ACGT")
        p2 = self.create_snp_profile(content="TGCA")
        cmd, retval = self.create_command_and_result([p1, p2])
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertTrue(success)
        self.assertEqual(
            p1.format,
            enum.SeqProfileFormat.REF_ALN_SEQ,
        )
        self.assertEqual(
            p2.format,
            enum.SeqProfileFormat.REF_ALN_SEQ,
        )


@pytest.mark.scenario_ids("TC-11-13-01")
class TestSnpInvalidCases(BaseSnpUploadTestCase):
    """Invalid SNP profile scenarios."""

    def test_empty_sequence_fails(self) -> None:
        """Empty content and no
        aligned_nucleotide_seq → d3e2f1a0."""
        profile = self.create_snp_profile(content="")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertFalse(success)
        pr = self.get_profile_result(retval)
        self.assertTrue(pr.has_errors())
        self.assertHasLogCode(pr, "d3e2f1a0")

    def test_invalid_characters_fails(self) -> None:
        """Sequence with invalid chars → e2f1a0b9."""
        profile = self.create_snp_profile(content="ACGT!@X")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertFalse(success)
        pr = self.get_profile_result(retval)
        self.assertTrue(pr.has_errors())
        self.assertHasLogCode(pr, "e2f1a0b9")

    def test_missing_ref_seq_fails(self) -> None:
        """Non-existent ref_seq → b7c6d5e4 on
        batch result."""
        profile = self.create_snp_profile(content="ACGT")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[False])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertFalse(success)
        # Error is on the batch result, not
        # the profile result
        self.assertTrue(retval.has_errors())
        self.assertHasLogCode(retval, "b7c6d5e4")

    def test_protocol_no_ref_seq_id_fails(
        self,
    ) -> None:
        """Protocol without ref_seq_id →
        a6b5c4d3."""
        profile = self.create_snp_profile(content="ACGT")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol(ref_seq_id=None)
        # No ref_seq_ids → no EXISTS_SOME call
        self.mock_crud_for_snp([protocol])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertFalse(success)
        pr = self.get_profile_result(retval)
        self.assertTrue(pr.has_errors())
        self.assertHasLogCode(pr, "a6b5c4d3")

    def test_length_mismatch_fails(self) -> None:
        """Profiles with different lengths for
        same ref_seq → f1a0b9c8."""
        p1 = self.create_snp_profile(content="ACGT")
        p2 = self.create_snp_profile(content="ACGTNN")
        cmd, retval = self.create_command_and_result([p1, p2])
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertFalse(success)
        # First profile passes, second fails
        pr1 = self.get_profile_result(retval, 0, 0)
        pr2 = self.get_profile_result(retval, 0, 1)
        self.assertFalse(pr1.has_errors())
        self.assertTrue(pr2.has_errors())
        self.assertHasLogCode(pr2, "f1a0b9c8")


@pytest.mark.scenario_ids("TC-11-13-01")
class TestSnpBehavior(BaseSnpUploadTestCase):
    """Behavioral / boundary tests."""

    def test_skipped_profile_ignored(self) -> None:
        """Pre-SKIPPED profile is not validated."""
        profile = self.create_snp_profile(content="!!INVALID!!")
        cmd, retval = self.create_command_and_result(profile)
        # Mark profile result as SKIPPED before
        # calling the function
        retval.samples[0].seq_profiles[0].status = EtlStatus.SKIPPED

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        # Skipped profile is not collected, so
        # early return with no profiles
        self.assertTrue(success)
        self.service.repository.crud.assert_not_called()

    def test_non_snp_profile_ignored(self) -> None:
        """Allele profile is not picked up by
        SNP validation."""
        profile = self.create_snp_profile(content="ACGT")
        # Override type to ALLELE
        profile.seq_profile_type = enum.SeqProfileType.ALLELE
        cmd, retval = self.create_command_and_result(profile)

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertTrue(success)
        self.service.repository.crud.assert_not_called()

    def test_valid_chars_boundary(self) -> None:
        """All valid chars ACGTN- accepted,
        lowercase rejected."""
        profile_ok = self.create_snp_profile(content="ACGTN-")
        cmd_ok, retval_ok = self.create_command_and_result(profile_ok)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success_ok = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd_ok,
            retval_ok,
            self.uow,
        )
        self.assertTrue(success_ok)

        # Lowercase is invalid
        profile_lc = self.create_snp_profile(content="acgt")
        cmd_lc, retval_lc = self.create_command_and_result(profile_lc)
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success_lc = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd_lc,
            retval_lc,
            self.uow,
        )
        self.assertFalse(success_lc)
        pr = self.get_profile_result(retval_lc)
        self.assertHasLogCode(pr, "e2f1a0b9")

    def test_batch_validation_idempotent(
        self,
    ) -> None:
        """Calling validation twice on same
        batch yields same result."""
        profile = self.create_snp_profile(content="ACGT")
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        r1 = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        # Reset mock for second call; profile
        # is now processed (format set)
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])
        r2 = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        self.assertTrue(r1)
        self.assertTrue(r2)
