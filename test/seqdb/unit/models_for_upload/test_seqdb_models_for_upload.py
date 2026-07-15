"""
Unit tests for IDSDB ETL model classes.

Tests the Identifier, AlleleForUpload, AlleleProfileForUpload,
and SampleBatchForUpload models with various validation scenarios.
"""

import base64
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.seqdb.domain import model


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelIdentifier:

    def test_valid_with_identifier_issuer_code(self) -> None:
        """Test valid Identifier with identifier_issuer_code."""
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER", external_id="SAMPLE123"
        )
        assert identifier_for_upload.identifier_issuer_code == "TEST_ISSUER"
        assert identifier_for_upload.identifier_issuer_id is None
        assert identifier_for_upload.external_id == "SAMPLE123"

    def test_valid_with_identifier_issuer_id(self) -> None:
        """Test valid Identifier with identifier_issuer_id."""
        issuer_id = uuid4()
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_id=issuer_id, external_id="SAMPLE123"
        )
        assert identifier_for_upload.identifier_issuer_code is None
        assert identifier_for_upload.identifier_issuer_id == issuer_id
        assert identifier_for_upload.external_id == "SAMPLE123"

    def test_valid_with_both_issuer_fields(self) -> None:
        """Test valid Identifier with both issuer fields."""
        issuer_id = uuid4()
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER",
            identifier_issuer_id=issuer_id,
            external_id="SAMPLE123",
        )
        assert identifier_for_upload.identifier_issuer_code == "TEST_ISSUER"
        assert identifier_for_upload.identifier_issuer_id == issuer_id

    def test_invalid_missing_both_issuer_fields(self) -> None:
        """Test ValidationError when both issuer fields are missing."""
        with pytest.raises(ValidationError):
            model.IdentifierForUpload(external_id="SAMPLE123")

    def test_max_length_validation(self) -> None:
        """Test field length validation."""
        # Valid lengths
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="A" * 255, external_id="B" * 255
        )
        assert len(identifier_for_upload.identifier_issuer_code or []) == 255
        assert len(identifier_for_upload.external_id) == 255
        # Exceeding max lengths
        with pytest.raises(ValidationError):
            model.IdentifierForUpload(
                identifier_issuer_code="A" * 256, external_id="B" * 255
            )
            model.IdentifierForUpload(
                identifier_issuer_code="A" * 255, external_id="B" * 256
            )


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelAlleleForUpload:

    def test_valid_with_locus_id(self) -> None:
        """Test valid AlleleForUpload with locus_id."""
        locus_id = uuid4()
        allele = model.AlleleForUpload(locus_id=locus_id, seq="ATCG")
        assert allele.locus_id == locus_id

    def test_inheritance_from_seqdb_allele(self) -> None:
        """Test that AlleleForUpload inherits seqdb.Allele properties."""
        allele = model.AlleleForUpload(seq="ATCG", length=4)
        assert allele.seq == "atcg"  # seq is normalized to lowercase
        assert allele.length == 4

    def test_id_equals_hash(self) -> None:
        """Test that id must equal seq_hash when both are provided."""
        # This should work - providing matching id and seq_hash

        sequence = "ATCG"
        expected_hash = UUID(
            hashlib.sha256(sequence.lower().encode("ascii")).digest()[:16].hex()
        )

        allele = model.AlleleForUpload(seq=sequence, id=expected_hash)
        assert allele.id == expected_hash

    def test_invalid_id_mismatches_hash(self) -> None:
        """Test ValidationError when id doesn't match computed seq_hash."""
        with pytest.raises(ValidationError):
            model.AlleleForUpload(
                seq="ATCG",
                id=uuid4(),  # Random id that won't match computed seq_hash
            )


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelBaseSeq:
    """Test cases for BaseSeq model validation and functionality."""

    @staticmethod
    def _get_valid_dna_sequence() -> str:
        """Return a valid DNA sequence for testing."""
        return "ATCGATCGATCG"

    @staticmethod
    def _get_invalid_dna_sequence() -> str:
        """Return an invalid DNA sequence for testing."""
        return "ATCGXYZ123"

    @staticmethod
    def _compute_expected_hash(sequence: str) -> UUID:
        """Compute the expected sequence hash for a given sequence."""
        normalized_seq = sequence.lower()
        return UUID(hashlib.sha256(normalized_seq.encode("ascii")).digest()[:16].hex())

    def test_valid_sequence_creation(self) -> None:
        """Test creating BaseSeq with valid DNA sequence."""
        seq = "ATCGATCG"
        base_seq = model.BaseSeq(seq=seq)
        assert base_seq.seq == seq.lower()
        assert base_seq.length == len(seq)
        assert base_seq.seq_format == model.enum.SeqFormat.STR_DNA
        assert base_seq.id is not None

    def test_sequence_normalization(self) -> None:
        """Test that DNA sequences are normalized to lowercase."""
        seq = "ATCGATCG"
        base_seq = model.BaseSeq(seq=seq)
        assert base_seq.seq == seq.lower()

    def test_automatic_length_calculation(self) -> None:
        """Test that length is automatically calculated when set to 0."""
        seq = self._get_valid_dna_sequence()
        base_seq = model.BaseSeq(seq=seq, length=0)
        assert base_seq.length == len(seq)

    def test_explicit_length_validation(self) -> None:
        """Test that explicit length must match sequence length."""
        seq = self._get_valid_dna_sequence()
        # Valid matching length
        base_seq = model.BaseSeq(seq=seq, length=len(seq))
        assert base_seq.length == len(seq)

        # Invalid mismatched length
        with pytest.raises(
            ValidationError, match="Provided length does not match computed length"
        ):
            model.BaseSeq(seq=seq, length=len(seq) + 1)

    def test_hash_calculation(self) -> None:
        """Test that sequence hash is correctly calculated."""
        seq = self._get_valid_dna_sequence()
        base_seq = model.BaseSeq(seq=seq)
        expected_hash = self._compute_expected_hash(seq)
        assert base_seq.id == expected_hash

    def test_explicit_hash_validation(self) -> None:
        """Test that explicit hash must match computed hash."""
        seq = self._get_valid_dna_sequence()
        expected_hash = self._compute_expected_hash(seq)

        # Valid matching hash
        base_seq = model.BaseSeq(seq=seq, id=expected_hash)
        assert base_seq.id == expected_hash

        # Invalid mismatched hash
        with pytest.raises(
            ValidationError, match="does not match computed sequence hash"
        ):
            model.BaseSeq(seq=seq, id=uuid4())

    def test_invalid_dna_characters(self) -> None:
        """Test that invalid DNA characters raise ValidationError."""
        invalid_seq = self._get_invalid_dna_sequence()
        with pytest.raises(ValidationError, match="invalid characters"):
            model.BaseSeq(seq=invalid_seq)

    def test_ambiguous_dna_characters(self) -> None:
        """Test that ambiguous IUPAC DNA characters are allowed."""
        seq_with_ambiguous = "ATCGRYSWKMBDHVN"
        base_seq = model.BaseSeq(seq=seq_with_ambiguous)
        assert base_seq.seq == seq_with_ambiguous.lower()
        assert base_seq.length == len(seq_with_ambiguous)

    def test_empty_sequence_error(self) -> None:
        """Test that empty sequence raises appropriate error."""
        with pytest.raises(
            ValidationError, match="Unable to calculate sequence length"
        ):
            model.BaseSeq(seq="", length=0)

    def test_seq_format_serialization(self) -> None:
        """Test that seq_format is properly serialized."""
        seq = self._get_valid_dna_sequence()
        base_seq = model.BaseSeq(seq=seq)
        serialized = base_seq.model_dump()
        assert serialized["seq_format"] == 2

    def test_different_seq_formats(self) -> None:
        """Test handling of different sequence formats."""
        seq = self._get_valid_dna_sequence()
        # Test with explicit format
        base_seq = model.BaseSeq(seq=seq, seq_format=model.enum.SeqFormat.STR_DNA)
        assert base_seq.seq_format == model.enum.SeqFormat.STR_DNA

        # Test with hash only format (should rely on provided hash)
        custom_hash = uuid4()
        with pytest.raises(
            ValidationError, match="Unable to calculate sequence length"
        ):
            model.BaseSeq(
                seq="custom_format_seq",
                seq_format=model.enum.SeqFormat.HASH_ONLY,
                id=custom_hash,
            )


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelSeq:
    """Test cases for Seq model functionality and inheritance."""

    @staticmethod
    def _create_valid_contig() -> model.Contig:
        """Create a valid Contig for testing."""
        return model.Contig(seq="ATCGATCG")

    @staticmethod
    def _create_sample_seq(**kwargs: Any) -> model.Seq:
        """Create a sample Seq with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_{uuid4().hex[:8]}",
            "contigs": [TestModelSeq._create_valid_contig()],
        }
        defaults.update(kwargs)
        return model.Seq(**defaults)  # type: ignore[arg-type]

    def test_seq_creation_with_contigs(self) -> None:
        """Test creating Seq with contigs."""
        contigs = [self._create_valid_contig(), model.Contig(seq="GCTAGCTA")]
        seq = model.Seq(
            sample_id=uuid4(), code="test_seq", contigs=contigs  # type: ignore[call-arg]
        )
        assert len(seq.contigs) == 2
        assert seq.code == "test_seq"
        assert seq.is_available

    def test_seq_without_contigs(self) -> None:
        """Test creating Seq without contigs (not available)."""
        seq = model.Seq(
            sample_id=uuid4(), code="test_seq", contigs=[]  # type: ignore[call-arg]
        )
        assert len(seq.contigs) == 0
        assert not seq.is_available

    def test_sample_mixin_inheritance(self) -> None:
        """Test that Seq inherits HasSampleMixin properties."""
        sample_id = uuid4()
        seq = self._create_sample_seq(sample_id=sample_id)
        assert seq.sample_id == sample_id

    def test_code_mixin_inheritance(self) -> None:
        """Test that Seq inherits CodeMixin properties."""
        code = "custom_seq_code"
        seq = self._create_sample_seq(code=code)
        assert seq.code == code

    def test_quality_mixin_inheritance(self) -> None:
        """Test that Seq inherits QualityMixin properties."""
        qc_score = 0.95
        qc_result = model.enum.QualityControlResult.PASS
        seq = self._create_sample_seq(qc_score=qc_score, qc_result=qc_result)
        assert seq.qc_score == qc_score
        assert seq.qc_result == qc_result

    def test_computed_contig_lengths(self) -> None:
        """Test computed fields for contig lengths."""
        short_contig = model.Contig(seq="ATCG")
        long_contig = model.Contig(seq="ATCGATCGATCGATCG")
        seq = model.Seq(
            sample_id=uuid4(),  # type: ignore[call-arg]
            code="test_seq",  # type: ignore[call-arg]
            contigs=[short_contig, long_contig],
        )
        assert seq.min_contig_length == 4
        assert seq.max_contig_length == 16

    def test_empty_contigs_computed_lengths(self) -> None:
        """Test computed lengths with empty contigs list."""
        seq = model.Seq(
            sample_id=uuid4(), code="test_seq", contigs=[]  # type: ignore[call-arg]
        )
        assert seq.min_contig_length == 0
        assert seq.max_contig_length == 0

    def test_assembly_protocol_link(self) -> None:
        """Test assembly protocol relationship."""
        protocol_id = uuid4()
        seq = self._create_sample_seq(protocol_id=protocol_id)
        assert seq.protocol_id == protocol_id

    def test_file_and_read_set_relationships(self) -> None:
        """Test file and read set relationships."""
        file_id = uuid4()
        read_set_id = uuid4()
        read_set2_id = uuid4()

        seq = self._create_sample_seq(
            file_id=file_id,
            file_format=model.enum.SeqFileFormat.FASTA,
            read_set_id=read_set_id,
            read_set2_id=read_set2_id,
        )
        assert seq.file_id == file_id
        assert seq.read_set_id == read_set_id
        assert seq.read_set2_id == read_set2_id

    def test_uri_field(self) -> None:
        """Test URI field functionality."""
        uri = "https://example.com/seq/123"
        seq = self._create_sample_seq(uri=uri)
        assert seq.uri == uri

    def test_contigs_serialization(self) -> None:
        """Test that contigs field exists and has proper structure."""
        seq = self._create_sample_seq()
        # Check that contigs field exists and is a list of Contig objects
        assert isinstance(seq.contigs, list)
        assert len(seq.contigs) > 0
        for contig in seq.contigs:
            assert isinstance(contig, model.Contig)


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelSeqForUpload:
    """Test cases for SeqForUpload model functionality and upload-specific features."""

    @staticmethod
    def _create_sample_seq_for_upload(**kwargs: Any) -> model.SeqForUpload:
        """Create a sample SeqForUpload with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_upload_{uuid4().hex[:8]}",
            "contigs": [model.Contig(seq="ATCGATCG")],
            "protocol_id": uuid4(),  # Required: either protocol_id or protocol_code
        }
        defaults.update(kwargs)
        return model.SeqForUpload(**defaults)  # type: ignore[arg-type]

    def test_seq_for_upload_creation(self) -> None:
        """Test creating SeqForUpload with basic fields."""
        sample_id = uuid4()
        code = "test_seq_upload"
        seq_upload = model.SeqForUpload(
            sample_id=sample_id,
            code=code,  # type: ignore[call-arg]
            contigs=[model.Contig(seq="ATCGATCG")],
            protocol_code="TEST_PROTOCOL",  # Required: either protocol_id or protocol_code
        )
        assert seq_upload.sample_id == sample_id
        assert seq_upload.code == code
        assert seq_upload.is_available

    def test_inheritance_from_seq(self) -> None:
        """Test that SeqForUpload inherits all Seq properties."""
        contigs = [model.Contig(seq="ATCGATCG"), model.Contig(seq="GCTAGCTA")]
        seq_upload = self._create_sample_seq_for_upload(contigs=contigs)

        # Should inherit Seq functionality
        assert len(seq_upload.contigs) == 2
        assert seq_upload.is_available
        assert seq_upload.min_contig_length == 8
        assert seq_upload.max_contig_length == 8

    def test_sample_id_with_null_id(self) -> None:
        """Test SeqForUpload with NULL_ID for sample_id."""
        seq_upload = model.SeqForUpload(
            sample_id=NULL_ID,
            code="test_seq",  # type: ignore[call-arg]
            contigs=[model.Contig(seq="ATCGATCG")],
            protocol_code="TEST_PROTOCOL",  # Required: either protocol_id or protocol_code
        )
        assert seq_upload.sample_id == NULL_ID

    def test_sample_id_serialization(self) -> None:
        """Test that sample_id serialization handles NULL_ID correctly."""
        # Test with valid UUID
        sample_id = uuid4()
        seq_upload = self._create_sample_seq_for_upload(sample_id=sample_id)
        # Note: model_dump may fail due to contigs serialization, but we can test the field directly
        assert seq_upload.sample_id == sample_id

        # Test with NULL_ID
        seq_upload_null = self._create_sample_seq_for_upload(sample_id=NULL_ID)
        assert seq_upload_null.sample_id == NULL_ID

        # Test that the field serializer works during JSON serialization
        # The field serializer is now handled by BatchForUpload base class
        json_data = seq_upload_null.model_dump_json()
        import json

        parsed_data = json.loads(json_data)
        assert parsed_data["sample_id"] == str(NULL_ID)

    def test_upload_specific_fields(self) -> None:
        """Test upload-specific field handling."""
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        # Should still inherit all Seq functionality
        assert seq_upload.code is not None
        assert isinstance(seq_upload.contigs, list)

        # Upload-specific behavior
        assert seq_upload.sample_id == NULL_ID

    def test_json_serialization(self) -> None:
        """Test JSON serialization structure of SeqForUpload."""
        seq_upload = self._create_sample_seq_for_upload()

        # Test that the model has the expected fields
        assert seq_upload.sample_id is not None
        assert seq_upload.code is not None
        assert seq_upload.contigs is not None
        assert seq_upload.is_available

        # Test actual JSON serialization
        json_str = seq_upload.model_dump_json()
        data = json.loads(json_str)

        # Verify structure
        assert "sample_id" in data
        assert "code" in data
        assert "contigs" in data

        # Contigs are serialized as a JSON string, so parse it
        contigs_str = data["contigs"]
        assert isinstance(contigs_str, str)
        contigs_data = json.loads(contigs_str)
        assert isinstance(contigs_data, list)
        assert len(contigs_data) > 0

        # Verify that each contig has the expected fields including properly serialized UUID
        contig = contigs_data[0]
        assert "id" in contig
        assert "seq" in contig
        assert "seq_format" in contig
        assert "length" in contig
        assert isinstance(contig["id"], str)  # UUID should be serialized as string

    def test_quality_fields_inheritance(self) -> None:
        """Test that quality fields are properly inherited."""
        qc_score = 0.85
        qc_result = model.enum.QualityControlResult.WARN

        seq_upload = self._create_sample_seq_for_upload(
            qc_score=qc_score, qc_result=qc_result
        )

        assert seq_upload.qc_score == qc_score
        assert seq_upload.qc_result == qc_result

    def test_optional_relationships(self) -> None:
        """Test optional relationship fields in upload context."""
        file_id = uuid4()
        protocol_id = uuid4()

        seq_upload = self._create_sample_seq_for_upload(
            file_id=file_id,
            file_format=model.enum.SeqFileFormat.FASTA,
            protocol_id=protocol_id,
        )

        assert seq_upload.file_id == file_id
        assert seq_upload.file_format == model.enum.SeqFileFormat.FASTA
        assert seq_upload.protocol_id == protocol_id

    def test_contig_validation_inheritance(self) -> None:
        """Test that contig validation is inherited from Seq."""
        # Valid contigs should work
        valid_contigs = [model.Contig(seq="ATCGATCG")]
        seq_upload = self._create_sample_seq_for_upload(contigs=valid_contigs)
        assert len(seq_upload.contigs) == 1

        # Empty contigs should result in not available
        empty_seq_upload = self._create_sample_seq_for_upload(contigs=[])
        assert not empty_seq_upload.is_available

    def test_assembly_protocol_id_validation(self) -> None:
        """Test that assembly_protocol_id is properly validated."""
        protocol_id = uuid4()
        seq_upload = self._create_sample_seq_for_upload(
            protocol_id=protocol_id,
            protocol_code=None,  # Override default to test only ID
        )
        assert seq_upload.protocol_id == protocol_id
        assert seq_upload.protocol_code is None

    def test_assembly_protocol_code_validation(self) -> None:
        """Test that assembly_protocol_code is properly validated."""
        protocol_code = "TEST_ASSEMBLY_PROTOCOL"
        seq_upload = self._create_sample_seq_for_upload(
            protocol_code=protocol_code,
            protocol_id=NULL_ID,  # Override default to test only code
        )
        assert seq_upload.protocol_code == protocol_code
        assert seq_upload.protocol_id == NULL_ID

    def test_assembly_protocol_both_provided(self) -> None:
        """Test that both assembly_protocol_id and assembly_protocol_code can be provided."""
        protocol_id = uuid4()
        protocol_code = "TEST_ASSEMBLY_PROTOCOL"
        seq_upload = self._create_sample_seq_for_upload(
            protocol_id=protocol_id,
            protocol_code=protocol_code,
        )
        assert seq_upload.protocol_id == protocol_id
        assert seq_upload.protocol_code == protocol_code

    def test_assembly_protocol_validation_failure(self) -> None:
        """Test that validation fails when neither assembly_protocol_id nor assembly_protocol_code is provided."""
        with pytest.raises(ValueError) as context:
            model.SeqForUpload(
                sample_id=uuid4(),
                contigs=[model.Contig(seq="ATCGATCG")],
                protocol_id=NULL_ID,  # Not provided
                protocol_code=None,  # Not provided
            )

        assert "Either protocol_code or protocol_id must be provided" in str(
            context.value
        )


@pytest.mark.scenario_ids("TC-RBAC-04-11", "TC-SEC-31-01")
class TestModelSeqProfileForUpload:

    def test_json_serialization(self) -> None:
        """Test JSON serialization of AlleleProfileForUpload."""
        allele_id1, allele_id2 = uuid4(), uuid4()
        allele_ids: list[UUID | None] = [allele_id1, allele_id2]
        allele_profile = model.SeqProfileForUpload(
            protocol_code="PROTOCOL123",
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content=base64.b64encode(
                b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
            ).decode("ascii"),
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),
        )
        json_str = allele_profile.model_dump_json()
        data = json.loads(json_str)
        assert data["protocol_code"] == "PROTOCOL123"
        # The stored profile uses sorted allele IDs
        assert data["content"] == base64.b64encode(
            b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
        ).decode("ascii")
        # n_loci is not a direct field; compute via helper
        assert allele_profile.get_n_loci() == 2
        assert data["content_hash"] == str(
            model.SeqProfile.get_allele_profile_hash(allele_ids)
        )

    def test_valid_with_protocol_code_and_locus_set_code(self) -> None:
        """Test valid AlleleProfileForUpload with codes."""
        allele_id1, allele_id2 = uuid4(), uuid4()
        # Sort allele IDs to match hash calculation
        allele_ids: list[UUID | None] = [allele_id1, allele_id2]
        allele_profile = model.SeqProfileForUpload(
            protocol_code="PROTOCOL123",
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content=base64.b64encode(
                b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
            ).decode("ascii"),
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),
        )
        assert allele_profile.protocol_code == "PROTOCOL123"
        # locus_set fields removed in refactor; protocol_id falls back to NULL_ID
        assert allele_profile.protocol_id == NULL_ID

    def test_valid_with_protocol_id_and_locus_set_id(self) -> None:
        """Test valid AlleleProfileForUpload with IDs."""
        protocol_id = uuid4()
        allele_id1, allele_id2 = uuid4(), uuid4()
        # Sort allele IDs to match hash calculation
        allele_ids: list[UUID | None] = [allele_id1, allele_id2]
        allele_profile = model.SeqProfileForUpload(
            protocol_id=protocol_id,
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content=base64.b64encode(
                b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
            ).decode("ascii"),
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),
        )
        assert allele_profile.protocol_id == protocol_id
        # locus_set_id removed from SeqProfileForUpload in refactor
        # assert allele_profile.locus_set_id is None
        assert allele_profile.protocol_code is None
        # assert allele_profile.locus_set_code is None
        assert allele_profile.allele_ids is None
        assert allele_profile.locus_allele_id_map is None

    def test_valid_with_alleles(self) -> None:
        """Test valid AlleleProfileForUpload with allele_ids."""
        allele_ids: list[UUID | None] = [
            uuid4(),
            uuid4(),
        ]
        allele_profile = model.SeqProfileForUpload(
            protocol_code="PROTOCOL123",
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            locus_code_map_code="MAP123",
            allele_ids=allele_ids,
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),
        )
        # content should be generated from allele_ids
        assert (
            allele_profile.content
            == model.SeqProfile.get_ordered_allele_ids_representation(allele_ids)
        )
        assert len(allele_profile.allele_ids or []) == 2
        assert allele_profile.locus_allele_id_map is None

    def test_valid_with_locus_allele_id_map(self) -> None:
        """Test valid AlleleProfileForUpload with locus_allele_id_map."""
        locus_allele_id_map = {"locus1": uuid4(), "locus2": uuid4()}
        allele_profile = model.SeqProfileForUpload(
            protocol_code="PROTOCOL123",
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            locus_code_map_code="MAP123",
            locus_allele_id_map=locus_allele_id_map,
            content_hash=model.SeqProfile.get_allele_profile_hash(
                list(locus_allele_id_map.values())
            ),
        )
        assert allele_profile.content == ""
        assert allele_profile.allele_ids is None
        assert allele_profile.locus_allele_id_map == locus_allele_id_map

    def test_valid_with_locus_code_map_when_needed(self) -> None:
        """Test valid AlleleProfileForUpload with locus_code_map when using allele_ids."""
        allele_ids: list[UUID | None] = [uuid4()]
        allele_profile = model.SeqProfileForUpload(
            protocol_code="PROTOCOL123",
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            locus_code_map_code="MAP123",
            allele_ids=allele_ids,
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),
        )
        assert allele_profile.locus_code_map_code == "MAP123"
        assert len(allele_profile.allele_ids or []) == 1
        assert allele_profile.locus_allele_id_map is None

    def test_invalid_missing_protocol_fields(self) -> None:
        """Test ValidationError when both protocol fields are missing."""
        with pytest.raises(ValidationError):
            allele_id = uuid4()
            model.SeqProfileForUpload(
                seq_profile_type=model.enum.SeqProfileType.ALLELE,
                format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
                content=base64.b64encode(allele_id.bytes).decode("ascii"),
                content_hash=model.SeqProfile.get_allele_profile_hash([allele_id]),
            )

    def test_invalid_missing_locus_set_fields(self) -> None:
        """Test ValidationError when both locus_set fields are missing."""
        # locus_set fields removed in refactor; providing protocol_code and content should be valid
        allele_id = uuid4()
        allele_profile = model.SeqProfileForUpload(
            protocol_code="PROTOCOL123",
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content=base64.b64encode(allele_id.bytes).decode("ascii"),
            content_hash=model.SeqProfile.get_allele_profile_hash([allele_id]),
        )
        assert allele_profile.protocol_code == "PROTOCOL123"

    def test_invalid_missing_allele_data(self) -> None:
        """Test ValidationError when all allele data fields are missing."""
        with pytest.raises(ValidationError):
            model.SeqProfileForUpload(
                protocol_code="PROTOCOL123",
                seq_profile_type=model.enum.SeqProfileType.ALLELE,
                format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            )

    def test_invalid_missing_locus_code_map_when_needed(self) -> None:
        """Test ValidationError when locus_code_map is missing but alleles have locus_code."""
        locus_allele_id_map: dict[str, UUID] = {"locus1": uuid4()}
        with pytest.raises(ValidationError):
            model.SeqProfileForUpload(
                protocol_code="PROTOCOL123",
                seq_profile_type=model.enum.SeqProfileType.ALLELE,
                format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
                locus_allele_id_map=locus_allele_id_map,
            )

    def test_valid_without_locus_code_map_when_not_needed(self) -> None:
        """Test valid AlleleProfileForUpload without locus_code_map when using allele_ids."""
        # Test using allele_ids to avoid locus_code_map requirement
        allele_id1, allele_id2 = uuid4(), uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id1, allele_id2]
        )
        assert allele_profile.locus_code_map_code is None
        assert allele_profile.locus_code_map_id == None
        assert allele_profile.allele_ids is None

    def test_quality_mixin_inheritance(self) -> None:
        """Test that AlleleProfileForUpload inherits QualityMixin properties."""
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id], qc_score=0.95
        )
        assert allele_profile.qc_score == 0.95

    @staticmethod
    def _get_allele_profile_for_ids(
        allele_ids: list[UUID | None], **kwargs: Any
    ) -> model.SeqProfileForUpload:
        # Sort allele IDs to match hash calculation
        allele_bytes = b"".join(
            NULL_ID.bytes if x is None else x.bytes for x in allele_ids
        )
        # Add NULL_ID bytes for any None values
        null_count = sum(x is None for x in allele_ids)
        return model.SeqProfileForUpload(
            protocol_code="PROTOCOL456",
            seq_profile_type=model.enum.SeqProfileType.ALLELE,
            format=model.enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content=base64.b64encode(allele_bytes).decode("ascii"),
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),
            **kwargs,
        )


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelSampleForUpload:

    @staticmethod
    def _create_sample_seq_for_upload(**kwargs: Any) -> model.SeqForUpload:
        """Create a sample SeqForUpload with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_upload_{uuid4().hex[:8]}",
            "contigs": [model.Contig(seq="ATCGATCG")],
            "protocol_id": uuid4(),  # Required: either protocol_id or protocol_code
        }
        defaults.update(kwargs)
        return model.SeqForUpload(**defaults)  # type: ignore[arg-type]

    def test_valid_with_sample_id(self) -> None:
        """Test valid SampleForUpload with sample_id."""
        sample_id = uuid4()
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            id=sample_id,
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )
        assert sample.id == sample_id
        assert sample.identifiers is None

    def test_valid_with_sample_ids(self) -> None:
        """Test valid SampleForUpload with Identifiers."""

        identifier_for_upload = IdentifierForUpload(
            identifier_issuer_id=uuid4(),
            external_id="SAMPLE123",
        )
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            identifiers=[identifier_for_upload],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )
        assert sample.id is None
        assert len(sample.identifiers or []) == 1

    def test_valid_with_both_sample_identifiers(self) -> None:
        """Test valid SampleForUpload with both sample_id and sample_ids."""
        sample_id = uuid4()
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="ISSUER123", external_id="SAMPLE123"
        )
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            id=sample_id,
            identifiers=[identifier_for_upload],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )
        assert sample.id == sample_id
        assert len(sample.identifiers or []) == 1

    def test_valid_with_multiple_identifiers(self) -> None:
        """Test valid SampleForUpload with multiple identifiers."""
        identifiers_for_upload = [
            model.IdentifierForUpload(
                identifier_issuer_code="ISSUER1", external_id="SAMPLE1"
            ),
            model.IdentifierForUpload(
                identifier_issuer_code="ISSUER2", external_id="SAMPLE2"
            ),
        ]
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample_for_upload = model.SampleForUpload(
            identifiers=identifiers_for_upload,
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )
        assert len(sample_for_upload.identifiers or []) == 2

    def test_valid_with_optional_fields(self) -> None:
        """Test valid SampleForUpload with optional fields."""
        data_collection_id = uuid4()
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample_for_upload = model.SampleForUpload(
            id=uuid4(),
            sample=model.Sample(created_in_data_collection_id=data_collection_id),
            seq_profiles=[allele_profile],
        )
        sample: model.Sample = sample_for_upload.sample  # type: ignore[assignment]
        assert sample.created_in_data_collection_id == data_collection_id

    def test_invalid_missing_sample_identification(self) -> None:
        """Test that SampleForUpload works without sample_id or Identifiers (they are optional)."""
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        # This should not raise ValidationError since both fields are optional
        sample = model.SampleForUpload(
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )
        assert sample.id is None
        assert sample.identifiers is None

    def test_invalid_empty_sample_ids(self) -> None:
        """Test that SampleForUpload accepts empty Identifiers list."""
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        # This should not raise ValidationError since empty list is valid
        sample_for_upload = model.SampleForUpload(
            identifiers=[],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )
        assert len(sample_for_upload.identifiers or []) == 0

    def test_valid_with_single_seq(self) -> None:
        """Test SampleForUpload with a single SeqForUpload."""
        sample_id = uuid4()
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_upload],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        assert sample.id == sample_id
        assert len(sample.seqs or []) == 1
        assert (sample.seqs or [])[0].sample_id == NULL_ID
        assert isinstance((sample.seqs or [])[0], model.SeqForUpload)

    def test_valid_with_multiple_seqs(self) -> None:
        """Test SampleForUpload with multiple SeqForUpload instances."""
        sample_id = uuid4()
        seq1 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_001")
        seq2 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_002")
        seq3 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_003")

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample_for_upload = model.SampleForUpload(
            id=sample_id,
            seqs=[seq1, seq2, seq3],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        assert len(sample_for_upload.seqs or []) == 3
        assert (sample_for_upload.seqs or [])[0].code == "seq_001"
        assert (sample_for_upload.seqs or [])[1].code == "seq_002"
        assert (sample_for_upload.seqs or [])[2].code == "seq_003"

        # All seqs should have NULL_ID as sample_id when sample has an id
        for seq in sample_for_upload.seqs or []:
            assert seq.sample_id == NULL_ID
            assert isinstance(seq, model.SeqForUpload)

    def test_valid_with_empty_seqs_list(self) -> None:
        """Test SampleForUpload with empty seqs list."""
        sample_id = uuid4()
        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample_for_upload = model.SampleForUpload(
            id=sample_id,
            seqs=[],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        assert sample_for_upload.id == sample_id
        assert len(sample_for_upload.seqs or []) == 0
        assert isinstance(sample_for_upload.seqs, list)

    def test_valid_with_seqs_and_identifiers(self) -> None:
        """Test SampleForUpload with both seqs and Identifiers."""
        sample_id = uuid4()
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER", external_id="SAMPLE_123"
        )
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample_for_upload = model.SampleForUpload(
            id=sample_id,
            identifiers=[identifier_for_upload],
            seqs=[seq_upload],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        assert sample_for_upload.id == sample_id
        assert len(sample_for_upload.identifiers or []) == 1
        assert len(sample_for_upload.seqs or []) == 1
        assert (sample_for_upload.seqs or [])[0].sample_id == NULL_ID

    def test_valid_seqs_with_different_properties(self) -> None:
        """Test SampleForUpload with seqs having different properties."""
        sample_id = uuid4()
        file_id = uuid4()
        protocol_id = uuid4()

        # Create seqs with different characteristics (all with NULL_ID sample_id)
        seq_with_file = self._create_sample_seq_for_upload(
            sample_id=NULL_ID,
            code="seq_with_file",
            file_id=file_id,
            file_format=model.enum.SeqFileFormat.FASTA,
        )

        seq_with_protocol = self._create_sample_seq_for_upload(
            sample_id=NULL_ID,
            code="seq_with_protocol",
            protocol_id=protocol_id,
        )

        seq_with_quality = self._create_sample_seq_for_upload(
            sample_id=NULL_ID,
            code="seq_with_qc",
            qc_score=0.95,
            qc_result=model.enum.QualityControlResult.PASS,
        )

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_with_file, seq_with_protocol, seq_with_quality],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        assert len(sample.seqs or []) == 3

        # Verify specific properties of each seq
        file_seq = next(s for s in sample.seqs or [] if s.code == "seq_with_file")
        assert file_seq.file_id == file_id
        assert file_seq.file_format == model.enum.SeqFileFormat.FASTA

        protocol_seq = next(
            s for s in sample.seqs or [] if s.code == "seq_with_protocol"
        )
        assert protocol_seq.protocol_id == protocol_id

        quality_seq = next(s for s in sample.seqs or [] if s.code == "seq_with_qc")
        assert quality_seq.qc_score == 0.95
        assert quality_seq.qc_result == model.enum.QualityControlResult.PASS

    def test_seqs_serialization_structure(self) -> None:
        """Test that seqs property maintains proper structure for serialization."""
        sample_id = uuid4()
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_upload],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        # Test that the seqs property exists and has correct type
        assert isinstance(sample.seqs, list)
        assert len(sample.seqs or []) == 1

        # Test that each seq in the list is a SeqForUpload instance
        for seq in sample.seqs or []:
            assert isinstance(seq, model.SeqForUpload)
            assert seq.code is not None
            assert seq.contigs is not None
            assert seq.sample_id == NULL_ID

    def test_valid_seqs_with_own_sample_ids(self) -> None:
        """Test SampleForUpload without id where seqs can have their own sample_ids."""
        # When SampleForUpload has no id (NULL_ID), seqs can have their own sample_ids
        seq_sample_id1 = uuid4()
        seq_sample_id2 = uuid4()

        seq1 = self._create_sample_seq_for_upload(
            sample_id=seq_sample_id1, code="seq_001"
        )
        seq2 = self._create_sample_seq_for_upload(
            sample_id=seq_sample_id2, code="seq_002"
        )

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=NULL_ID,  # Sample has no specific id
            seqs=[seq1, seq2],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        assert sample.id == None
        assert len(sample.seqs or []) == 2

        # Seqs can have their own sample_ids when sample has no id
        seq_codes_to_sample_ids = {x.code: x.sample_id for x in sample.seqs or []}
        assert seq_codes_to_sample_ids["seq_001"] == seq_sample_id1
        assert seq_codes_to_sample_ids["seq_002"] == seq_sample_id2

    def test_valid_sample_without_id_seqs_with_null_ids(self) -> None:
        """Test SampleForUpload without id where seqs also have NULL_ID sample_ids."""
        seq1 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_001")
        seq2 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_002")

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        # Sample without id, seqs also without specific sample_ids
        sample = model.SampleForUpload(
            id=NULL_ID,
            seqs=[seq1, seq2],
            seq_profiles=[allele_profile],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        assert sample.id == None
        assert len(sample.seqs or []) == 2

        # All seqs should have NULL_ID as sample_id
        for seq in sample.seqs or []:
            assert seq.sample_id == NULL_ID
            assert isinstance(seq, model.SeqForUpload)


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelSampleBatchForUpload:

    def setup_method(self) -> None:
        self.test_dir = Path(__file__).parent

    @staticmethod
    def _create_sample_seq_for_upload(**kwargs: Any) -> model.SeqForUpload:
        """Create a sample SeqForUpload with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_upload_{uuid4().hex[:8]}",
            "contigs": [model.Contig(seq="ATCGATCG")],
            "protocol_id": uuid4(),  # Required: either protocol_id or protocol_code
        }
        defaults.update(kwargs)
        return model.SeqForUpload(**defaults)  # type: ignore[arg-type]

    @staticmethod
    def _create_sample_with_seqs(
        sample_id: UUID | None = None, num_seqs: int = 1, **kwargs: Any
    ) -> model.SampleForUpload:
        """Create a SampleForUpload with specified number of SeqForUpload instances."""
        if sample_id is None:
            sample_id = uuid4()

        # Create seqs with proper sample_id based on validation rules
        seq_sample_id = NULL_ID if sample_id != NULL_ID else uuid4()
        seqs = [
            TestModelSampleBatchForUpload._create_sample_seq_for_upload(
                sample_id=seq_sample_id, code=f"seq_{i:03d}"
            )
            for i in range(num_seqs)
        ]

        allele_id = uuid4()
        allele_profile = TestModelSeqProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        defaults = {
            "id": sample_id,
            "seqs": seqs,
            "allele_profiles": [allele_profile],
            "created_in_data_collection_id": uuid4(),
        }
        defaults.update(kwargs)
        return model.SampleForUpload(**defaults)  # type: ignore[arg-type]

    def test_read_source_complete_sample_batch1_json(self) -> None:
        """Test reading sample_batch_for_upload1.json as SampleBatchForUpload model."""
        file_path = self.test_dir / "sample_batch_for_upload1.json.gz"
        with gzip.open(file_path, "rt") as f:
            data = json.load(f)
        # file_path = self.test_dir / "sample_set_for_upload1.json"
        # with open(file_path, "rt") as f:
        #     data = json.load(f)

        sample_batch = model.SampleBatchForUpload(**data)
        assert isinstance(sample_batch, model.SampleBatchForUpload)

    def test_read_source_sample_batch2_json(self) -> None:
        """Test reading sample_batch_for_upload2.json as SampleBatchForUpload model."""
        file_path = self.test_dir / "sample_batch_for_upload2.json"
        with open(file_path, "rt") as f:
            data = json.load(f)

        sample_batch = model.SampleBatchForUpload(**data)
        assert isinstance(sample_batch, model.SampleBatchForUpload)

        # Validate structure: 4 samples with different seq/contig configurations
        assert len(sample_batch.samples) == 4

        # Sample 1: 1 seq with 1 contig
        sample_for_upload1 = sample_batch.samples[0]
        assert len(sample_for_upload1.seqs or []) == 1
        assert len((sample_for_upload1.seqs or [])[0].contigs) == 1
        assert (sample_for_upload1.seqs or [])[0].code == "seq_001_single"

        # Sample 2: 1 seq with 2 contigs
        sample_for_upload2 = sample_batch.samples[1]
        assert len(sample_for_upload2.seqs or []) == 1
        assert len((sample_for_upload2.seqs or [])[0].contigs) == 2
        assert (sample_for_upload2.seqs or [])[0].code == "seq_002_double"

        # Sample 3: 2 seqs with 1 contig each
        sample_for_upload3 = sample_batch.samples[2]
        assert len(sample_for_upload3.seqs or []) == 2
        assert len((sample_for_upload3.seqs or [])[0].contigs) == 1
        assert len((sample_for_upload3.seqs or [])[1].contigs) == 1
        assert (sample_for_upload3.seqs or [])[0].code == "seq_003a_single"
        assert (sample_for_upload3.seqs or [])[1].code == "seq_003b_single"

        # Sample 4: 2 seqs with 2 contigs each
        sample_for_upload4 = sample_batch.samples[3]
        assert len(sample_for_upload4.seqs or []) == 2
        assert len((sample_for_upload4.seqs or [])[0].contigs) == 2
        assert len((sample_for_upload4.seqs or [])[1].contigs) == 2
        assert (sample_for_upload4.seqs or [])[0].code == "seq_004a_double"
        assert (sample_for_upload4.seqs or [])[1].code == "seq_004b_double"

        # Verify computed field
        assert sample_batch.has_seqs

    def test_valid_minimal(self) -> None:
        """Test valid SampleBatchForUpload with minimal data."""
        allele_id = uuid4()
        sample = model.SampleForUpload(
            id=uuid4(),
            sample=model.Sample(created_in_data_collection_id=uuid4()),
            seq_profiles=[
                TestModelSeqProfileForUpload._get_allele_profile_for_ids([allele_id])
            ],
        )
        sample_set = model.SampleBatchForUpload(samples=[sample])
        assert len(sample_set.samples) == 1
        assert sample_set.alleles is None

    def test_valid_with_alleles(self) -> None:
        """Test valid SampleBatchForUpload with alleles."""
        allele = model.AlleleForUpload(locus_id=uuid4(), seq="ATCG")
        allele_id = uuid4()
        sample = model.SampleForUpload(
            id=uuid4(),
            sample=model.Sample(created_in_data_collection_id=uuid4()),
            seq_profiles=[
                TestModelSeqProfileForUpload._get_allele_profile_for_ids([allele_id])
            ],
        )
        sample_set = model.SampleBatchForUpload(samples=[sample], alleles=[allele])
        assert len(sample_set.samples or []) == 1
        assert len(sample_set.alleles or []) == 1

    def test_valid_with_multiple_samples(self) -> None:
        """Test valid SampleBatchForUpload with multiple samples including seqs."""
        # Sample with seqs
        sample_with_seqs = self._create_sample_with_seqs(num_seqs=2)

        # Sample without seqs (traditional style)
        allele_id2 = uuid4()
        sample_without_seqs = model.SampleForUpload(
            id=uuid4(),
            sample=model.Sample(created_in_data_collection_id=uuid4()),
            seq_profiles=[
                TestModelSeqProfileForUpload._get_allele_profile_for_ids([allele_id2])
            ],
        )

        sample_set = model.SampleBatchForUpload(
            samples=[sample_with_seqs, sample_without_seqs]
        )
        assert len(sample_set.samples) == 2

        # Verify first sample has seqs
        assert len(sample_set.samples[0].seqs or []) == 2

        # Verify second sample has no seqs
        assert sample_set.samples[1].seqs is None

        # Test computed field
        assert sample_set.has_seqs

    def test_valid_empty_samples_list(self) -> None:
        """Test valid SampleBatchForUpload with empty samples list."""
        sample_set = model.SampleBatchForUpload(samples=[])
        assert len(sample_set.samples) == 0

    def test_valid_with_samples_containing_seqs(self) -> None:
        """Test SampleBatchForUpload where all samples contain SeqForUpload instances."""
        sample1 = self._create_sample_with_seqs(num_seqs=1)
        sample2 = self._create_sample_with_seqs(num_seqs=3)
        sample3 = self._create_sample_with_seqs(num_seqs=2)

        sample_batch = model.SampleBatchForUpload(samples=[sample1, sample2, sample3])

        assert len(sample_batch.samples) == 3
        assert len(sample_batch.samples[0].seqs or []) == 1
        assert len(sample_batch.samples[1].seqs or []) == 3
        assert len(sample_batch.samples[2].seqs or []) == 2

        # Test computed field
        assert sample_batch.has_seqs

        # Verify all seqs are SeqForUpload instances
        for sample in sample_batch.samples:
            for seq in sample.seqs or []:
                assert isinstance(seq, model.SeqForUpload)

    def test_valid_samples_with_different_seq_configurations(self) -> None:
        """Test SampleBatchForUpload with samples having different seq configurations."""
        # Sample with file-linked seqs
        file_id = uuid4()
        seq_with_file = self._create_sample_seq_for_upload(
            sample_id=NULL_ID,
            file_id=file_id,
            file_format=model.enum.SeqFileFormat.FASTA,
        )
        sample_with_file = self._create_sample_with_seqs()
        sample_with_file.seqs = [seq_with_file]

        # Sample with quality-controlled seqs
        seq_with_qc = self._create_sample_seq_for_upload(
            sample_id=NULL_ID,
            qc_score=0.95,
            qc_result=model.enum.QualityControlResult.PASS,
        )
        sample_with_qc = self._create_sample_with_seqs()
        sample_with_qc.seqs = [seq_with_qc]

        # Sample with assembly protocol seqs
        protocol_id = uuid4()
        seq_with_protocol = self._create_sample_seq_for_upload(
            sample_id=NULL_ID, protocol_id=protocol_id
        )
        sample_with_protocol = self._create_sample_with_seqs()
        sample_with_protocol.seqs = [seq_with_protocol]

        sample_batch = model.SampleBatchForUpload(
            samples=[sample_with_file, sample_with_qc, sample_with_protocol]
        )

        assert len(sample_batch.samples) == 3
        assert sample_batch.has_seqs

        # Verify specific seq properties
        file_seq = (sample_batch.samples[0].seqs or [])[0]
        assert file_seq.file_id == file_id
        assert file_seq.file_format == model.enum.SeqFileFormat.FASTA

        qc_seq = (sample_batch.samples[1].seqs or [])[0]
        assert qc_seq.qc_score == 0.95
        assert qc_seq.qc_result == model.enum.QualityControlResult.PASS

        protocol_seq = (sample_batch.samples[2].seqs or [])[0]
        assert protocol_seq.protocol_id == protocol_id

    def test_valid_mixed_samples_with_and_without_seqs(self) -> None:
        """Test SampleBatchForUpload with mix of samples with and without seqs."""
        # Sample with multiple seqs
        sample_with_seqs = self._create_sample_with_seqs(num_seqs=2)

        # Sample with empty seqs list
        sample_with_empty_seqs = self._create_sample_with_seqs(num_seqs=0)

        # Sample without seqs property (None)
        allele_id = uuid4()
        sample_without_seqs = model.SampleForUpload(
            id=uuid4(),
            sample=model.Sample(created_in_data_collection_id=uuid4()),
            seq_profiles=[
                TestModelSeqProfileForUpload._get_allele_profile_for_ids([allele_id])
            ],
        )

        sample_batch = model.SampleBatchForUpload(
            samples=[sample_with_seqs, sample_with_empty_seqs, sample_without_seqs]
        )

        assert len(sample_batch.samples) == 3
        assert len(sample_batch.samples[0].seqs or []) == 2  # Has seqs
        assert len(sample_batch.samples[1].seqs or []) == 0  # Empty seqs list
        assert sample_batch.samples[2].seqs is None  # No seqs property

        # Should still report has_seqs as True since at least one sample has seqs
        assert sample_batch.has_seqs

    def test_valid_sample_set_with_seqs_and_alleles(self) -> None:
        """Test SampleBatchForUpload with both sample seqs and reference alleles."""
        # Create samples with seqs
        sample1 = self._create_sample_with_seqs(num_seqs=2)
        sample2 = self._create_sample_with_seqs(num_seqs=1)

        # Create reference alleles
        allele1 = model.AlleleForUpload(locus_id=uuid4(), seq="ATCGATCG")
        allele2 = model.AlleleForUpload(locus_id=uuid4(), seq="GCTAGCTA")

        sample_batch = model.SampleBatchForUpload(
            samples=[sample1, sample2], alleles=[allele1, allele2]
        )

        assert len(sample_batch.samples) == 2
        assert len(sample_batch.alleles or []) == 2
        assert sample_batch.has_seqs

        # Verify samples have seqs
        for sample in sample_batch.samples:
            assert sample.seqs is not None
            assert len(sample.seqs or []) > 0

    def test_computed_field_has_seqs_false(self) -> None:
        """Test has_seqs computed field returns False when no samples have seqs."""
        # Create samples without seqs
        allele_id1 = uuid4()
        allele_id2 = uuid4()
        samples = [
            model.SampleForUpload(
                id=uuid4(),
                sample=model.Sample(created_in_data_collection_id=uuid4()),
                seq_profiles=[
                    TestModelSeqProfileForUpload._get_allele_profile_for_ids(
                        [allele_id1]
                    )
                ],
            ),
            model.SampleForUpload(
                id=uuid4(),
                sample=model.Sample(created_in_data_collection_id=uuid4()),
                seq_profiles=[
                    TestModelSeqProfileForUpload._get_allele_profile_for_ids(
                        [allele_id2]
                    )
                ],
            ),
        ]

        sample_batch = model.SampleBatchForUpload(samples=samples)
        assert not sample_batch.has_seqs

    def test_computed_field_has_seqs_true_with_empty_seqs_list(self) -> None:
        """Test has_seqs computed field with samples having empty seqs lists."""
        # Sample with empty seqs list should not count as having seqs
        sample_with_empty_seqs = model.SampleForUpload(
            id=uuid4(),
            seqs=[],  # Empty list
            seq_profiles=[
                TestModelSeqProfileForUpload._get_allele_profile_for_ids([uuid4()])
            ],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        sample_batch = model.SampleBatchForUpload(samples=[sample_with_empty_seqs])
        # Empty seqs list should result in has_seqs being False
        assert not sample_batch.has_seqs

    def test_samples_with_seqs_validation_compliance(self) -> None:
        """Test that samples with seqs follow proper validation rules."""
        # Sample with id - seqs must have NULL_ID sample_id
        sample_id = uuid4()
        seq_with_null_sample_id = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        sample_with_id = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_with_null_sample_id],
            seq_profiles=[
                TestModelSeqProfileForUpload._get_allele_profile_for_ids([uuid4()])
            ],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        # Sample without id - seqs can have their own sample_ids
        seq_sample_id = uuid4()
        seq_with_own_sample_id = self._create_sample_seq_for_upload(
            sample_id=seq_sample_id
        )

        sample_without_id = model.SampleForUpload(
            id=NULL_ID,
            seqs=[seq_with_own_sample_id],
            seq_profiles=[
                TestModelSeqProfileForUpload._get_allele_profile_for_ids([uuid4()])
            ],
            sample=model.Sample(created_in_data_collection_id=uuid4()),
        )

        sample_batch = model.SampleBatchForUpload(
            samples=[sample_with_id, sample_without_id]
        )

        assert len(sample_batch.samples) == 2
        assert sample_batch.has_seqs

        # Verify validation compliance
        assert (sample_batch.samples[0].seqs or [])[0].sample_id == NULL_ID
        assert (sample_batch.samples[1].seqs or [])[0].sample_id == seq_sample_id
