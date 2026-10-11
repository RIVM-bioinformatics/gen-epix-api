"""
Unit tests for _verify_batch_refdata_snp_profiles.

Tests validate the SNP batch validation logic in
upload_verify_batch_refdata.py.
"""

from test.util.mock_compat import Mock
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import UploadAction
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import UploadResult, User
from gen_epix.etl.enum import EtlStatus, EtlStatusSet
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.enum import Role
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.seqdb.services.seq import SampleBatchUploader
from gen_epix.seqdb.services.seq.upload_verify_batch_refdata import (
    _collect_pending_allele_profiles,
    _collect_pending_profiles,
    _convert_allele_profiles_to_ids,
    _format_allele_ids,
    _get_allele_ids_for_profile,
    _get_existing_allele_ids,
    _get_repeat_numbers_for_profile,
    _handle_locus_allele_pair_mismatch,
    _load_profile_reference_data,
    _reconcile_provided_alleles,
    _verify_batch_refdata_allele_profiles,
    _verify_batch_refdata_kmer_profiles,
    _verify_batch_refdata_mlva_profiles,
    _verify_batch_refdata_snp_profiles,
    _verify_snp_reference_sequences,
)


class BaseSnpUploadTestCase:
    """Base test case for SNP upload validation."""

    def setup_method(self) -> None:
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
            format=enum.SeqProfileFormat.NEXTCLADE,
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

    def create_profile(
        self,
        profile_type: enum.SeqProfileType,
        profile_format: enum.SeqProfileFormat,
        content: str = "",
    ) -> model.SeqProfileForUpload:
        """Create an upload profile without invoking model validation."""
        profile = self.create_snp_profile(content=content)
        profile.seq_profile_type = profile_type
        profile.format = profile_format
        return profile

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

    def expectBatchProcessed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in EtlStatusSet.SUCCEEDED.value:
            pytest.fail(
                "Upload was not processed," f" status: {upload_result.status.value}"
            )

    def expectBatchFailed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in EtlStatusSet.FAILED.value:
            pytest.fail("Upload did not fail," f" status: {upload_result.status.value}")

    def expectHasLogCode(
        self,
        upload_result: UploadResult,
        code: list[str] | str,
    ) -> None:
        if isinstance(code, str):
            code = [code]
        missing_codes = [x for x in code if not upload_result.has_log_code(x)]
        if missing_codes:
            missing_str = ", ".join(missing_codes)
            pytest.fail(f"Log missing for code {missing_str}")


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

        assert success
        self.service.repository.crud.assert_not_called()


@pytest.mark.scenario_ids("TC-11-13-01")
class TestSnpValidCases(BaseSnpUploadTestCase):
    """Valid SNP profile scenarios."""

    def test_valid_snp_content_passes(
        self,
    ) -> None:
        """Valid SNP profile with Nextclade JSON

        content passes and sets format."""
        profile = self.create_snp_profile(content='{"sample1": {"subs": "A1T"}}')
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        assert success
        assert profile.format == enum.SeqProfileFormat.NEXTCLADE
        pr = self.get_profile_result(retval)
        assert not pr.has_errors()

    def test_matching_ref_seq_accepted(self) -> None:
        """Existing ref_seq passes validation."""
        profile = self.create_snp_profile(content='{"s1": {"subs": "A1T"}}')
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        assert success
        # Verify EXISTS_SOME was called for RefSeq
        crud_calls = self.service.repository.crud.call_args_list
        assert len(crud_calls) == 2
        assert crud_calls[1].args[2] == model.RefSeq
        assert crud_calls[1].args[3] == CrudOperation.EXISTS_SOME

    def test_two_profiles_same_ref_seq_same_length(
        self,
    ) -> None:
        """Two profiles for the same ref_seq with

        valid JSON both pass."""
        p1 = self.create_snp_profile(content='{"s1": {"subs": "A1T"}}')
        p2 = self.create_snp_profile(content='{"s2": {"subs": "C3G"}}')
        cmd, retval = self.create_command_and_result([p1, p2])
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        assert success
        assert p1.format == enum.SeqProfileFormat.NEXTCLADE
        assert p2.format == enum.SeqProfileFormat.NEXTCLADE


@pytest.mark.scenario_ids("TC-11-13-01")
class TestSnpInvalidCases(BaseSnpUploadTestCase):
    """Invalid SNP profile scenarios."""

    def test_empty_content_fails(self) -> None:
        """Empty content → d3e2f1a0."""
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

        assert not success
        pr = self.get_profile_result(retval)
        assert pr.has_errors()
        self.expectHasLogCode(pr, "d3e2f1a0")

    def test_missing_ref_seq_fails(self) -> None:
        """Non-existent ref_seq → b7c6d5e4 on

        batch result."""
        profile = self.create_snp_profile(content='{"s1": {"subs": "A1T"}}')
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[False])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        assert not success
        # Error is on the batch result, not
        # the profile result
        assert retval.has_errors()
        self.expectHasLogCode(retval, "b7c6d5e4")

    def test_protocol_no_ref_seq_id_fails(
        self,
    ) -> None:
        """Protocol without ref_seq_id →

        a6b5c4d3."""
        profile = self.create_snp_profile(content='{"s1": {"subs": "A1T"}}')
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

        assert not success
        pr = self.get_profile_result(retval)
        assert pr.has_errors()
        self.expectHasLogCode(pr, "a6b5c4d3")

    def test_any_valid_json_passes_structural_only(
        self,
    ) -> None:
        """Any valid JSON passes; no biological

        validation is performed."""
        profile = self.create_snp_profile(
            content='"just a string"',
        )
        cmd, retval = self.create_command_and_result(profile)
        protocol = self.create_protocol()
        self.mock_crud_for_snp([protocol], ref_seq_exists=[True])

        success = _verify_batch_refdata_snp_profiles(
            self.batch_uploader,
            cmd,
            retval,
            self.uow,
        )

        assert success
        pr = self.get_profile_result(retval)
        assert not pr.has_errors()


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
        assert success
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

        assert success
        self.service.repository.crud.assert_not_called()

    def test_batch_validation_idempotent(
        self,
    ) -> None:
        """Calling validation twice on same

        batch yields same result."""
        profile = self.create_snp_profile(content='{"s1": {"subs": "A1T"}}')
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

        assert r1
        assert r2

    def test_snp_reference_sequences_report_only_missing_ids(self) -> None:
        present_id, missing_id = uuid4(), uuid4()
        profiles = [
            self.create_snp_profile(protocol_id=present_id, content="present"),
            self.create_snp_profile(protocol_id=missing_id, content="missing"),
        ]
        protocols = {
            present_id: self.create_protocol(present_id, self.ref_seq_id),
            missing_id: self.create_protocol(missing_id, uuid4()),
        }
        self.service.repository.crud.return_value = [True, False]
        batch_result = model.SampleBatchUploadResult(samples=[])

        success = _verify_snp_reference_sequences(
            self.batch_uploader,
            self.uow,
            self.user.id,
            profiles,
            protocols,
            batch_result,
        )

        assert not success
        assert batch_result.has_log_code("b7c6d5e4")

    def test_snp_reference_sequence_without_ids_needs_no_repository_read(self) -> None:
        profile = self.create_snp_profile(content="content")
        protocol = self.create_protocol(ref_seq_id=None)
        batch_result = model.SampleBatchUploadResult(samples=[])

        success = _verify_snp_reference_sequences(
            self.batch_uploader,
            self.uow,
            self.user.id,
            [profile],
            {self.protocol_id: protocol},
            batch_result,
        )

        assert success
        self.service.repository.crud.assert_not_called()


class TestAlleleProfiles(BaseSnpUploadTestCase):
    """Allele-profile reference-data handling."""

    def test_ordered_content_resolves_and_assigns_new_allele_locus(self) -> None:
        allele_id = uuid4()
        locus_id = uuid4()
        locus_set_id = uuid4()
        profile = self.create_snp_profile(
            content=model.SeqProfile.get_ordered_allele_ids_representation([allele_id])
        )
        profile.seq_profile_type = enum.SeqProfileType.ALLELE
        profile.format = enum.SeqProfileFormat.ORDERED_ALLELE_IDS
        protocol = self.create_protocol()
        protocol.locus_set_id = locus_set_id
        locus_set = model.LocusSet.model_construct(
            id=locus_set_id, code="test", name="test", locus_ids=[locus_id]
        )
        cmd, batch_result = self.create_command_and_result(profile)
        allele = model.AlleleForUpload.model_construct(id=allele_id, locus_id=None)
        cmd.sample_batch.alleles = [allele]
        self.service.repository.crud.side_effect = [
            [protocol],
            [locus_set],
            [],
            [False],
        ]

        success = _verify_batch_refdata_allele_profiles(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        assert success
        assert profile.allele_ids == [allele_id]
        assert allele.locus_id == locus_id

    def test_collect_pending_allele_profiles_filters_type_and_status(self) -> None:
        allele_profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        other_profile = self.create_profile(
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        )
        non_allele_profile = self.create_profile(
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
        )
        cmd, batch_result = self.create_command_and_result(
            [allele_profile, other_profile, non_allele_profile]
        )
        skipped_result = batch_result.samples[0].seq_profiles[1]
        skipped_result.status = EtlStatus.SKIPPED

        profiles, results = _collect_pending_allele_profiles(cmd, batch_result)

        assert profiles == [allele_profile]
        assert results == [batch_result.samples[0].seq_profiles[0]]

    def test_allele_verification_without_allele_profiles_returns_success(self) -> None:
        profile = self.create_profile(
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        )
        cmd, batch_result = self.create_command_and_result(profile)

        success = _verify_batch_refdata_allele_profiles(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        assert success
        self.service.repository.crud.assert_not_called()

    @pytest.mark.parametrize(
        ("representation", "expected_error"),
        [
            ("ordered-content", False),
            ("unsupported-content", True),
            ("no-representation", True),
        ],
        ids=["ordered-content", "unsupported-format", "missing-input"],
    )
    def test_get_allele_ids_for_profile_representations(
        self, representation: str, expected_error: bool
    ) -> None:
        allele_id, locus_id, code_map_id = uuid4(), uuid4(), uuid4()
        profile_result = UploadResult()
        if representation == "ordered-content":
            profile = self.create_profile(
                enum.SeqProfileType.ALLELE,
                enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
                content=model.SeqProfile.get_ordered_allele_ids_representation(
                    [allele_id]
                ),
            )
        elif representation == "unsupported-content":
            profile = self.create_profile(
                enum.SeqProfileType.ALLELE,
                enum.SeqProfileFormat.NEXTCLADE,
                content="content",
            )
        else:
            profile = self.create_profile(
                enum.SeqProfileType.ALLELE,
                enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            )

        allele_ids = _get_allele_ids_for_profile(
            profile,
            profile_result,
            [locus_id],
            {},
        )

        if expected_error:
            assert allele_ids is None
            assert profile_result.has_errors()
        else:
            assert allele_ids == [allele_id]
            assert profile.allele_ids == [allele_id]
            assert not profile_result.has_errors()

    def test_get_allele_ids_for_profile_maps_locus_codes_in_locus_order(self) -> None:
        first_locus_id, second_locus_id = uuid4(), uuid4()
        first_allele_id, second_allele_id = uuid4(), uuid4()
        code_map_id = uuid4()
        profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        profile.locus_code_map_id = code_map_id
        profile.locus_allele_id_map = {
            "second": second_allele_id,
            "first": first_allele_id,
        }

        allele_ids = _get_allele_ids_for_profile(
            profile,
            UploadResult(),
            [first_locus_id, second_locus_id],
            {code_map_id: {first_locus_id: "first", second_locus_id: "second"}},
        )

        assert allele_ids == [first_allele_id, second_allele_id]
        assert profile.allele_ids == [first_allele_id, second_allele_id]
        assert profile.locus_allele_id_map is None

    def test_convert_allele_profiles_rejects_incomplete_and_malformed_inputs(
        self,
    ) -> None:
        locus_id, locus_set_id, protocol_id = uuid4(), uuid4(), uuid4()
        empty_profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        short_profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        short_profile.allele_ids = [uuid4(), uuid4()]
        skipped_profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        profiles = [empty_profile, short_profile, skipped_profile]
        results = [
            UploadResult(),
            UploadResult(),
            UploadResult(status=EtlStatus.SKIPPED),
        ]
        protocol_map = {self.protocol_id: Mock(locus_set_id=locus_set_id)}
        locus_set_map = {locus_set_id: Mock(locus_ids=[locus_id])}

        success, allele_ids = _convert_allele_profiles_to_ids(
            profiles, results, protocol_map, locus_set_map, {}
        )

        assert not success
        assert allele_ids == set()
        assert results[0].has_log_code("b4cb2ea0")
        assert results[1].has_log_code("b29dcaf6")
        assert not results[2].has_errors()

    def test_load_profile_reference_data_reverses_locus_code_map(self) -> None:
        locus_id, locus_set_id, code_map_id = uuid4(), uuid4(), uuid4()
        profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        profile.locus_code_map_id = code_map_id
        protocol = Mock(id=self.protocol_id, locus_set_id=locus_set_id)
        locus_set = Mock(id=locus_set_id)
        code_map = Mock(id=code_map_id, code_map={"L1": locus_id})
        self.service.repository.crud.side_effect = [
            [protocol],
            [locus_set],
            [code_map],
        ]

        protocol_map, locus_set_map, reverse_maps = _load_profile_reference_data(
            self.batch_uploader, self.uow, self.user.id, [profile]
        )

        assert protocol_map == {self.protocol_id: protocol}
        assert locus_set_map == {locus_set_id: locus_set}
        assert reverse_maps == {code_map_id: {locus_id: "L1"}}

    def test_get_existing_allele_ids_splits_reads_at_chunk_limit(self) -> None:
        allele_ids = {uuid4() for _ in range(1001)}
        self.service.repository.crud.side_effect = [
            [True] * 1000,
            [True],
        ]

        existing_ids = _get_existing_allele_ids(
            self.batch_uploader, self.uow, self.user.id, allele_ids
        )

        assert existing_ids == allele_ids
        assert [
            len(call.kwargs["obj_ids"])
            for call in self.service.repository.crud.call_args_list
        ] == [1000, 1]

    @pytest.mark.parametrize(
        ("n_ids", "expected_suffix"),
        [(5, ""), (6, "... (and 1 more)")],
        ids=["within-display-limit", "truncated"],
    )
    def test_format_allele_ids_bounds_diagnostic_list(
        self, n_ids: int, expected_suffix: str
    ) -> None:
        allele_ids = {UUID(int=value) for value in range(1, n_ids + 1)}

        formatted = _format_allele_ids(allele_ids)

        assert formatted.endswith(expected_suffix)
        assert formatted.count(",") == min(n_ids - 1, 5)

    @pytest.mark.parametrize(
        ("n_pairs", "expected_suffix"),
        [(5, ""), (6, "... (and 1 more)")],
        ids=["within-display-limit", "truncated"],
    )
    def test_handle_locus_allele_mismatch_bounds_diagnostic(
        self, n_pairs: int, expected_suffix: str
    ) -> None:
        pairs = [(uuid4(), uuid4()) for _ in range(n_pairs)]
        profile_result = UploadResult()

        _handle_locus_allele_pair_mismatch(profile_result, pairs)

        assert profile_result.has_log_code("c9b8a7d6")
        assert profile_result.logs[0].message.endswith(expected_suffix)

    def test_reconcile_provided_alleles_deduplicates_and_assigns_loci(self) -> None:
        first_id, second_id, extra_id = uuid4(), uuid4(), uuid4()
        expected_locus_id, wrong_locus_id = uuid4(), uuid4()
        batch_result = model.SampleBatchUploadResult(samples=[])
        sample_batch = model.SampleBatchForUpload.model_construct(
            batch_id=uuid4(),
            samples=[],
            alleles=[
                model.AlleleForUpload.model_construct(id=first_id, locus_id=None),
                model.AlleleForUpload.model_construct(id=first_id, locus_id=None),
                model.AlleleForUpload.model_construct(
                    id=second_id, locus_id=wrong_locus_id
                ),
                model.AlleleForUpload.model_construct(id=extra_id, locus_id=None),
            ],
        )

        success = _reconcile_provided_alleles(
            batch_result,
            sample_batch,
            {first_id: expected_locus_id, second_id: expected_locus_id},
        )

        assert success
        assert [allele.id for allele in sample_batch.alleles] == [first_id, second_id]
        assert [allele.locus_id for allele in sample_batch.alleles] == [
            expected_locus_id,
            expected_locus_id,
        ]
        assert batch_result.has_log_code("dda74ae0")
        assert batch_result.has_log_code("e401b1bd")

    def test_reconcile_provided_alleles_reports_missing_new_alleles(self) -> None:
        missing_id = uuid4()
        batch_result = model.SampleBatchUploadResult(samples=[])
        sample_batch = model.SampleBatchForUpload.model_construct(
            batch_id=uuid4(), samples=[], alleles=[]
        )

        success = _reconcile_provided_alleles(
            batch_result, sample_batch, {missing_id: uuid4()}
        )

        assert not success
        assert batch_result.has_log_code("7eeced9e")
        assert str(missing_id) in batch_result.logs[0].message

    def test_all_existing_alleles_drop_redundant_payload(self) -> None:
        allele_id, locus_id, locus_set_id = uuid4(), uuid4(), uuid4()
        profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        profile.allele_ids = [allele_id]
        protocol = self.create_protocol()
        protocol.locus_set_id = locus_set_id
        locus_set = model.LocusSet.model_construct(
            id=locus_set_id, code="test", name="test", locus_ids=[locus_id]
        )
        cmd, batch_result = self.create_command_and_result(profile)
        cmd.sample_batch.alleles = [
            model.AlleleForUpload.model_construct(id=allele_id, locus_id=None)
        ]
        self.service.repository.crud.side_effect = [
            [protocol],
            [locus_set],
            [],
            [True],
        ]

        success = _verify_batch_refdata_allele_profiles(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        assert success
        assert cmd.sample_batch.alleles == []
        assert (
            profile.content
            == model.SeqProfile.get_ordered_allele_ids_representation([allele_id])
        )
        assert profile.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS
        assert profile.allele_ids is None


class TestMlvaProfiles(BaseSnpUploadTestCase):
    """MLVA profile representation and batch validation."""

    def test_collect_pending_profiles_filters_status_and_profile_type(self) -> None:
        mlva_profile = self.create_profile(
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        )
        other_profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        cmd, batch_result = self.create_command_and_result(
            [mlva_profile, other_profile]
        )
        batch_result.samples[0].seq_profiles[1].status = EtlStatus.SKIPPED

        profiles, results = _collect_pending_profiles(
            cmd, batch_result, enum.SeqProfileTypeSet.MLVA.value
        )

        assert profiles == [mlva_profile]
        assert results == [batch_result.samples[0].seq_profiles[0]]

    def test_repeat_number_map_follows_locus_order_and_clears_map(self) -> None:
        first_locus_id, second_locus_id, code_map_id = uuid4(), uuid4(), uuid4()
        profile = self.create_profile(
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        )
        profile.locus_code_map_id = code_map_id
        profile.locus_repeat_number_map = {"L2": 8, "L1": 3}

        repeat_numbers = _get_repeat_numbers_for_profile(
            profile,
            UploadResult(),
            [first_locus_id, second_locus_id],
            {code_map_id: {first_locus_id: "L1", second_locus_id: "L2"}},
        )

        assert repeat_numbers == [3, 8]
        assert profile.repeat_numbers == [3, 8]
        assert profile.locus_repeat_number_map is None

    @pytest.mark.parametrize(
        ("representation", "expected_values", "expected_error"),
        [
            ("ordered-content", [4, None], False),
            ("repeat-numbers", [4, None], False),
            ("unsupported-content", None, True),
            ("missing-input", None, True),
        ],
        ids=[
            "ordered-content-sentinel",
            "repeat-number-list",
            "unsupported-format",
            "missing-input",
        ],
    )
    def test_get_repeat_numbers_for_profile_representations(
        self,
        representation: str,
        expected_values: list[int | None] | None,
        expected_error: bool,
    ) -> None:
        profile_result = UploadResult()
        if representation == "ordered-content":
            profile = self.create_profile(
                enum.SeqProfileType.MLVA,
                enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
                content=f"[4, {MLVA_NO_LOCUS_REPEAT_NUMBER}]",
            )
        elif representation == "repeat-numbers":
            profile = self.create_profile(
                enum.SeqProfileType.MLVA,
                enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            )
            profile.repeat_numbers = [4, None]
        elif representation == "unsupported-content":
            profile = self.create_profile(
                enum.SeqProfileType.MLVA,
                enum.SeqProfileFormat.NEXTCLADE,
                content="content",
            )
        else:
            profile = self.create_profile(
                enum.SeqProfileType.MLVA,
                enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            )

        repeat_numbers = _get_repeat_numbers_for_profile(
            profile, profile_result, [uuid4(), uuid4()], {}
        )

        assert repeat_numbers == expected_values
        assert profile_result.has_errors() is expected_error

    def test_mlva_batch_normalizes_repeat_numbers_and_rejects_length_mismatch(
        self,
    ) -> None:
        locus_id, locus_set_id = uuid4(), uuid4()
        valid_profile = self.create_profile(
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        )
        valid_profile.repeat_numbers = [7]
        invalid_profile = self.create_profile(
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        )
        invalid_profile.repeat_numbers = [2, 3]
        cmd, batch_result = self.create_command_and_result(
            [valid_profile, invalid_profile]
        )
        protocol = Mock(id=self.protocol_id, locus_set_id=locus_set_id)
        locus_set = model.LocusSet.model_construct(
            id=locus_set_id, code="test", name="test", locus_ids=[locus_id]
        )
        self.service.repository.crud.side_effect = [[protocol], [locus_set], []]

        success = _verify_batch_refdata_mlva_profiles(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        assert not success
        assert (
            valid_profile.content
            == model.SeqProfile.get_ordered_repeat_numbers_representation([7])
        )
        assert valid_profile.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS
        assert valid_profile.repeat_numbers is None
        assert batch_result.samples[0].seq_profiles[1].has_log_code("f4b6a1c8")

    def test_mlva_batch_reports_missing_profile_representation(self) -> None:
        locus_id, locus_set_id = uuid4(), uuid4()
        profile = self.create_profile(
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        )
        cmd, batch_result = self.create_command_and_result(profile)
        protocol = Mock(id=self.protocol_id, locus_set_id=locus_set_id)
        locus_set = model.LocusSet.model_construct(
            id=locus_set_id, code="test", name="test", locus_ids=[locus_id]
        )
        self.service.repository.crud.side_effect = [[protocol], [locus_set], []]

        success = _verify_batch_refdata_mlva_profiles(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        assert not success
        assert batch_result.samples[0].seq_profiles[0].has_log_code("e6f7a8b9")

    def test_mlva_batch_without_profiles_returns_success(self) -> None:
        profile = self.create_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        )
        cmd, batch_result = self.create_command_and_result(profile)

        assert _verify_batch_refdata_mlva_profiles(
            self.batch_uploader, cmd, batch_result, self.uow
        )
        self.service.repository.crud.assert_not_called()


class TestKmerProfiles(BaseSnpUploadTestCase):
    """K-mer profiles remain explicitly unsupported."""

    def test_pending_kmer_profiles_fail_but_other_and_skipped_profiles_are_ignored(
        self,
    ) -> None:
        kmer_profile = self.create_profile(
            enum.SeqProfileType.KMER,
            enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
            content="{}",
        )
        other_profile = self.create_profile(
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
            content="{}",
        )
        skipped_kmer_profile = self.create_profile(
            enum.SeqProfileType.KMER,
            enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
            content="{}",
        )
        cmd, batch_result = self.create_command_and_result(
            [kmer_profile, other_profile, skipped_kmer_profile]
        )
        batch_result.samples[0].seq_profiles[2].status = EtlStatus.SKIPPED

        success = _verify_batch_refdata_kmer_profiles(
            self.batch_uploader, cmd, batch_result, self.uow
        )

        assert not success
        assert batch_result.samples[0].seq_profiles[0].has_log_code("a9b0c1d2")
        assert not batch_result.samples[0].seq_profiles[1].has_errors()
        assert not batch_result.samples[0].seq_profiles[2].has_errors()
