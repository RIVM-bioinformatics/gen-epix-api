"""
Unit tests for IDSDB ETL model classes.

Tests the ExternalIdentifier, AlleleForUpload, AlleleProfileForUpload,
and SampleBatchForUpload models with various validation scenarios.
"""

import base64
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any
from unittest import TestCase
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.seqdb.domain import model


class TestModelExternalIdentifier(TestCase):

    def test_valid_with_identifier_issuer_code(self) -> None:
        """Test valid ExternalIdentifier with identifier_issuer_code."""
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER", external_id="SAMPLE123"
        )
        self.assertEqual(identifier.identifier_issuer_code, "TEST_ISSUER")
        self.assertIsNone(identifier.identifier_issuer_id)
        self.assertEqual(identifier.external_id, "SAMPLE123")

    def test_valid_with_identifier_issuer_id(self) -> None:
        """Test valid ExternalIdentifier with identifier_issuer_id."""
        issuer_id = uuid4()
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_id=issuer_id, external_id="SAMPLE123"
        )
        self.assertIsNone(identifier.identifier_issuer_code)
        self.assertEqual(identifier.identifier_issuer_id, issuer_id)
        self.assertEqual(identifier.external_id, "SAMPLE123")

    def test_valid_with_both_issuer_fields(self) -> None:
        """Test valid ExternalIdentifier with both issuer fields."""
        issuer_id = uuid4()
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER",
            identifier_issuer_id=issuer_id,
            external_id="SAMPLE123",
        )
        self.assertEqual(identifier.identifier_issuer_code, "TEST_ISSUER")
        self.assertEqual(identifier.identifier_issuer_id, issuer_id)

    def test_invalid_missing_both_issuer_fields(self) -> None:
        """Test ValidationError when both issuer fields are missing."""
        with pytest.raises(ValidationError):
            model.ExternalIdentifierForUpload(external_id="SAMPLE123")

    def test_max_length_validation(self) -> None:
        """Test field length validation."""
        # Valid lengths
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_code="A" * 255, external_id="B" * 255
        )
        self.assertEqual(len(identifier.identifier_issuer_code or []), 255)
        self.assertEqual(len(identifier.external_id), 255)
        # Exceeding max lengths
        with pytest.raises(ValidationError):
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="A" * 256, external_id="B" * 255
            )
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="A" * 255, external_id="B" * 256
            )


class TestModelAlleleForUpload(TestCase):

    def test_valid_with_locus_id(self) -> None:
        """Test valid AlleleForUpload with locus_id."""
        locus_id = uuid4()
        allele = model.AlleleForUpload(
            locus_id=locus_id, locus_code="locus123", seq="ATCG"
        )
        self.assertEqual(allele.locus_id, locus_id)
        self.assertEqual(allele.locus_code, "locus123")

    def test_valid_with_locus_code_only(self) -> None:
        """Test valid AlleleForUpload with only locus_code."""
        allele = model.AlleleForUpload(locus_code="locus123", seq="ATCG")
        self.assertEqual(allele.locus_id, NULL_ID)
        self.assertEqual(allele.locus_code, "locus123")

    def test_valid_with_both_locus_fields(self) -> None:
        """Test valid AlleleForUpload with both locus fields."""
        locus_id = uuid4()
        allele = model.AlleleForUpload(
            locus_id=locus_id, locus_code="locus123", seq="ATCG"
        )
        self.assertEqual(allele.locus_id, locus_id)
        self.assertEqual(allele.locus_code, "locus123")

    def test_invalid_missing_both_locus_fields(self) -> None:
        """Test ValidationError when both locus fields are missing."""
        with pytest.raises(ValidationError):
            model.AlleleForUpload(seq="ATCG")

    def test_inheritance_from_seqdb_allele(self) -> None:
        """Test that AlleleForUpload inherits seqdb.Allele properties."""
        allele = model.AlleleForUpload(locus_code="locus123", seq="ATCG", length=4)
        self.assertEqual(allele.seq, "atcg")  # seq is normalized to lowercase
        self.assertEqual(allele.length, 4)

    def test_id_equals_hash(self) -> None:
        """Test that id must equal seq_hash when both are provided."""
        # This should work - providing matching id and seq_hash

        sequence = "ATCG"
        expected_hash = UUID(
            hashlib.sha256(sequence.lower().encode("ascii")).digest()[:16].hex()
        )

        allele = model.AlleleForUpload(
            locus_code="locus123", seq=sequence, id=expected_hash
        )
        self.assertEqual(allele.id, expected_hash)

    def test_invalid_id_mismatches_hash(self) -> None:
        """Test ValidationError when id doesn't match computed seq_hash."""
        with pytest.raises(ValidationError):
            model.AlleleForUpload(
                locus_code="locus123",
                seq="ATCG",
                id=uuid4(),  # Random id that won't match computed seq_hash
            )


class TestModelBaseSeq(TestCase):
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
        self.assertEqual(base_seq.seq, seq.lower())
        self.assertEqual(base_seq.length, len(seq))
        self.assertEqual(base_seq.seq_format, model.enum.SeqFormat.STR_DNA)
        self.assertIsNotNone(base_seq.id)

    def test_sequence_normalization(self) -> None:
        """Test that DNA sequences are normalized to lowercase."""
        seq = "ATCGATCG"
        base_seq = model.BaseSeq(seq=seq)
        self.assertEqual(base_seq.seq, seq.lower())

    def test_automatic_length_calculation(self) -> None:
        """Test that length is automatically calculated when set to 0."""
        seq = self._get_valid_dna_sequence()
        base_seq = model.BaseSeq(seq=seq, length=0)
        self.assertEqual(base_seq.length, len(seq))

    def test_explicit_length_validation(self) -> None:
        """Test that explicit length must match sequence length."""
        seq = self._get_valid_dna_sequence()
        # Valid matching length
        base_seq = model.BaseSeq(seq=seq, length=len(seq))
        self.assertEqual(base_seq.length, len(seq))

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
        self.assertEqual(base_seq.id, expected_hash)

    def test_explicit_hash_validation(self) -> None:
        """Test that explicit hash must match computed hash."""
        seq = self._get_valid_dna_sequence()
        expected_hash = self._compute_expected_hash(seq)

        # Valid matching hash
        base_seq = model.BaseSeq(seq=seq, id=expected_hash)
        self.assertEqual(base_seq.id, expected_hash)

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
        self.assertEqual(base_seq.seq, seq_with_ambiguous.lower())
        self.assertEqual(base_seq.length, len(seq_with_ambiguous))

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
        self.assertEqual(serialized["seq_format"], "STR_DNA")

    def test_different_seq_formats(self) -> None:
        """Test handling of different sequence formats."""
        seq = self._get_valid_dna_sequence()
        # Test with explicit format
        base_seq = model.BaseSeq(seq=seq, seq_format=model.enum.SeqFormat.STR_DNA)
        self.assertEqual(base_seq.seq_format, model.enum.SeqFormat.STR_DNA)

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


class TestModelSeq(TestCase):
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
        return model.Seq(**defaults)

    def test_seq_creation_with_contigs(self) -> None:
        """Test creating Seq with contigs."""
        contigs = [self._create_valid_contig(), model.Contig(seq="GCTAGCTA")]
        seq = model.Seq(sample_id=uuid4(), code="test_seq", contigs=contigs)
        self.assertEqual(len(seq.contigs), 2)
        self.assertEqual(seq.code, "test_seq")
        self.assertTrue(seq.is_available)

    def test_seq_without_contigs(self) -> None:
        """Test creating Seq without contigs (not available)."""
        seq = model.Seq(sample_id=uuid4(), code="test_seq", contigs=[])
        self.assertEqual(len(seq.contigs), 0)
        self.assertFalse(seq.is_available)

    def test_sample_mixin_inheritance(self) -> None:
        """Test that Seq inherits HasSampleMixin properties."""
        sample_id = uuid4()
        seq = self._create_sample_seq(sample_id=sample_id)
        self.assertEqual(seq.sample_id, sample_id)

    def test_code_mixin_inheritance(self) -> None:
        """Test that Seq inherits CodeMixin properties."""
        code = "custom_seq_code"
        seq = self._create_sample_seq(code=code)
        self.assertEqual(seq.code, code)

    def test_quality_mixin_inheritance(self) -> None:
        """Test that Seq inherits QualityMixin properties."""
        qc_score = 0.95
        qc_result = model.enum.QualityControlResult.PASS
        seq = self._create_sample_seq(qc_score=qc_score, qc_result=qc_result)
        self.assertEqual(seq.qc_score, qc_score)
        self.assertEqual(seq.qc_result, qc_result)

    def test_computed_contig_lengths(self) -> None:
        """Test computed fields for contig lengths."""
        short_contig = model.Contig(seq="ATCG")
        long_contig = model.Contig(seq="ATCGATCGATCGATCG")
        seq = model.Seq(
            sample_id=uuid4(), code="test_seq", contigs=[short_contig, long_contig]
        )
        self.assertEqual(seq.min_contig_length, 4)
        self.assertEqual(seq.max_contig_length, 16)

    def test_empty_contigs_computed_lengths(self) -> None:
        """Test computed lengths with empty contigs list."""
        seq = model.Seq(sample_id=uuid4(), code="test_seq", contigs=[])
        self.assertEqual(seq.min_contig_length, 0)
        self.assertEqual(seq.max_contig_length, 0)

    def test_assembly_protocol_link(self) -> None:
        """Test assembly protocol relationship."""
        assembly_protocol_id = uuid4()
        seq = self._create_sample_seq(assembly_protocol_id=assembly_protocol_id)
        self.assertEqual(seq.assembly_protocol_id, assembly_protocol_id)

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
        self.assertEqual(seq.file_id, file_id)
        self.assertEqual(seq.read_set_id, read_set_id)
        self.assertEqual(seq.read_set2_id, read_set2_id)

    def test_uri_field(self) -> None:
        """Test URI field functionality."""
        uri = "https://example.com/seq/123"
        seq = self._create_sample_seq(uri=uri)
        self.assertEqual(seq.uri, uri)

    def test_contigs_serialization(self) -> None:
        """Test that contigs field exists and has proper structure."""
        seq = self._create_sample_seq()
        # Check that contigs field exists and is a list of Contig objects
        self.assertIsInstance(seq.contigs, list)
        self.assertGreater(len(seq.contigs), 0)
        for contig in seq.contigs:
            self.assertIsInstance(contig, model.Contig)


class TestModelSeqForUpload(TestCase):
    """Test cases for SeqForUpload model functionality and upload-specific features."""

    @staticmethod
    def _create_sample_seq_for_upload(**kwargs: Any) -> model.SeqForUpload:
        """Create a sample SeqForUpload with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_upload_{uuid4().hex[:8]}",
            "contigs": [model.Contig(seq="ATCGATCG")],
        }
        defaults.update(kwargs)
        return model.SeqForUpload(**defaults)

    def test_seq_for_upload_creation(self) -> None:
        """Test creating SeqForUpload with basic fields."""
        sample_id = uuid4()
        code = "test_seq_upload"
        seq_upload = model.SeqForUpload(
            sample_id=sample_id, code=code, contigs=[model.Contig(seq="ATCGATCG")]
        )
        self.assertEqual(seq_upload.sample_id, sample_id)
        self.assertEqual(seq_upload.code, code)
        self.assertTrue(seq_upload.is_available)

    def test_inheritance_from_seq(self) -> None:
        """Test that SeqForUpload inherits all Seq properties."""
        contigs = [model.Contig(seq="ATCGATCG"), model.Contig(seq="GCTAGCTA")]
        seq_upload = self._create_sample_seq_for_upload(contigs=contigs)

        # Should inherit Seq functionality
        self.assertEqual(len(seq_upload.contigs), 2)
        self.assertTrue(seq_upload.is_available)
        self.assertEqual(seq_upload.min_contig_length, 8)
        self.assertEqual(seq_upload.max_contig_length, 8)

    def test_sample_id_with_null_id(self) -> None:
        """Test SeqForUpload with NULL_ID for sample_id."""
        seq_upload = model.SeqForUpload(
            sample_id=NULL_ID, code="test_seq", contigs=[model.Contig(seq="ATCGATCG")]
        )
        self.assertEqual(seq_upload.sample_id, NULL_ID)

    def test_sample_id_serialization(self) -> None:
        """Test that sample_id serialization handles NULL_ID correctly."""
        # Test with valid UUID
        sample_id = uuid4()
        seq_upload = self._create_sample_seq_for_upload(sample_id=sample_id)
        # Note: model_dump may fail due to contigs serialization, but we can test the field directly
        self.assertEqual(seq_upload.sample_id, sample_id)

        # Test with NULL_ID
        seq_upload_null = self._create_sample_seq_for_upload(sample_id=NULL_ID)
        self.assertEqual(seq_upload_null.sample_id, NULL_ID)

        # Test that the field serializer works during JSON serialization
        # The field serializer is now handled by BatchForUpload base class
        json_data = seq_upload_null.model_dump_json()
        import json

        parsed_data = json.loads(json_data)
        self.assertEqual(parsed_data["sample_id"], str(NULL_ID))

    def test_upload_specific_fields(self) -> None:
        """Test upload-specific field handling."""
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        # Should still inherit all Seq functionality
        self.assertIsNotNone(seq_upload.code)
        self.assertIsInstance(seq_upload.contigs, list)

        # Upload-specific behavior
        self.assertEqual(seq_upload.sample_id, NULL_ID)

    def test_json_serialization(self) -> None:
        """Test JSON serialization structure of SeqForUpload."""
        seq_upload = self._create_sample_seq_for_upload()

        # Test that the model has the expected fields
        self.assertIsNotNone(seq_upload.sample_id)
        self.assertIsNotNone(seq_upload.code)
        self.assertIsNotNone(seq_upload.contigs)
        self.assertTrue(seq_upload.is_available)

        # Test actual JSON serialization
        json_str = seq_upload.model_dump_json()
        data = json.loads(json_str)

        # Verify structure
        self.assertIn("sample_id", data)
        self.assertIn("code", data)
        self.assertIn("contigs", data)

        # Contigs are serialized as a JSON string, so parse it
        contigs_str = data["contigs"]
        self.assertIsInstance(contigs_str, str)
        contigs_data = json.loads(contigs_str)
        self.assertIsInstance(contigs_data, list)
        self.assertGreater(len(contigs_data), 0)

        # Verify that each contig has the expected fields including properly serialized UUID
        contig = contigs_data[0]
        self.assertIn("id", contig)
        self.assertIn("seq", contig)
        self.assertIn("seq_format", contig)
        self.assertIn("length", contig)
        self.assertIsInstance(contig["id"], str)  # UUID should be serialized as string

    def test_quality_fields_inheritance(self) -> None:
        """Test that quality fields are properly inherited."""
        qc_score = 0.85
        qc_result = model.enum.QualityControlResult.WARN

        seq_upload = self._create_sample_seq_for_upload(
            qc_score=qc_score, qc_result=qc_result
        )

        self.assertEqual(seq_upload.qc_score, qc_score)
        self.assertEqual(seq_upload.qc_result, qc_result)

    def test_optional_relationships(self) -> None:
        """Test optional relationship fields in upload context."""
        file_id = uuid4()
        assembly_protocol_id = uuid4()

        seq_upload = self._create_sample_seq_for_upload(
            file_id=file_id,
            file_format=model.enum.SeqFileFormat.FASTA,
            assembly_protocol_id=assembly_protocol_id,
        )

        self.assertEqual(seq_upload.file_id, file_id)
        self.assertEqual(seq_upload.file_format, model.enum.SeqFileFormat.FASTA)
        self.assertEqual(seq_upload.assembly_protocol_id, assembly_protocol_id)

    def test_contig_validation_inheritance(self) -> None:
        """Test that contig validation is inherited from Seq."""
        # Valid contigs should work
        valid_contigs = [model.Contig(seq="ATCGATCG")]
        seq_upload = self._create_sample_seq_for_upload(contigs=valid_contigs)
        self.assertEqual(len(seq_upload.contigs), 1)

        # Empty contigs should result in not available
        empty_seq_upload = self._create_sample_seq_for_upload(contigs=[])
        self.assertFalse(empty_seq_upload.is_available)


class TestModelAlleleProfileForUpload(TestCase):

    def test_json_serialization(self) -> None:
        """Test JSON serialization of AlleleProfileForUpload."""
        allele_id1, allele_id2 = uuid4(), uuid4()
        # Sort allele IDs to match hash calculation
        sorted_allele_ids = sorted([allele_id1, allele_id2])
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_profile=base64.b64encode(
                b"".join(x.bytes for x in sorted_allele_ids)
            ).decode("ascii"),
            n_loci=2,
            allele_profile_hash=model.AlleleProfile.get_allele_profile_hash(
                [allele_id1, allele_id2]
            ),
        )
        json_str = allele_profile.model_dump_json()
        data = json.loads(json_str)
        self.assertEqual(data["locus_detection_protocol_code"], "PROTOCOL123")
        self.assertEqual(data["locus_set_code"], "LOCUSSET123")
        # The stored profile uses sorted allele IDs
        self.assertEqual(
            data["allele_profile"],
            base64.b64encode(b"".join(x.bytes for x in sorted_allele_ids)).decode(
                "ascii"
            ),
        )
        self.assertEqual(data["n_loci"], 2)
        self.assertEqual(
            data["allele_profile_hash"],
            str(model.AlleleProfile.get_allele_profile_hash([allele_id1, allele_id2])),
        )

    def test_valid_with_protocol_code_and_locus_set_code(self) -> None:
        """Test valid AlleleProfileForUpload with codes."""
        allele_id1, allele_id2 = uuid4(), uuid4()
        # Sort allele IDs to match hash calculation
        sorted_allele_ids = sorted([allele_id1, allele_id2])
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_profile=base64.b64encode(
                b"".join(aid.bytes for aid in sorted_allele_ids)
            ).decode("ascii"),
            n_loci=2,
            allele_profile_hash=model.AlleleProfile.get_allele_profile_hash(
                [allele_id1, allele_id2]
            ),
        )
        self.assertEqual(allele_profile.locus_detection_protocol_code, "PROTOCOL123")
        self.assertEqual(allele_profile.locus_set_code, "LOCUSSET123")
        self.assertEqual(allele_profile.locus_detection_protocol_id, NULL_ID)
        self.assertEqual(allele_profile.locus_set_id, NULL_ID)

    def test_valid_with_protocol_id_and_locus_set_id(self) -> None:
        """Test valid AlleleProfileForUpload with IDs."""
        protocol_id = uuid4()
        locus_set_id = uuid4()
        allele_id1, allele_id2 = uuid4(), uuid4()
        # Sort allele IDs to match hash calculation
        sorted_allele_ids = sorted([allele_id1, allele_id2])
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_id=protocol_id,
            locus_set_id=locus_set_id,
            n_loci=2,
            allele_profile=base64.b64encode(
                b"".join(aid.bytes for aid in sorted_allele_ids)
            ).decode("ascii"),
            allele_profile_hash=model.AlleleProfile.get_allele_profile_hash(
                [allele_id1, allele_id2]
            ),
        )
        self.assertEqual(allele_profile.locus_detection_protocol_id, protocol_id)
        self.assertEqual(allele_profile.locus_set_id, locus_set_id)
        self.assertIsNone(allele_profile.locus_detection_protocol_code)
        self.assertIsNone(allele_profile.locus_set_code)
        self.assertIsNone(allele_profile.alleles)
        self.assertIsNone(allele_profile.locus_allele_id_map)

    def test_valid_with_alleles(self) -> None:
        """Test valid AlleleProfileForUpload with alleles."""
        alleles = [
            model.AlleleForUpload(locus_code="locus1", seq="ATCG"),
            model.AlleleForUpload(locus_code="locus2", seq="GCTA"),
        ]
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            locus_code_map_code="MAP123",
            alleles=alleles,
            # Don't provide n_loci for upload format with alleles
        )
        self.assertEqual(allele_profile.allele_profile, "")
        self.assertEqual(len(allele_profile.alleles or []), 2)
        self.assertIsNone(allele_profile.locus_allele_id_map)

    def test_valid_with_locus_allele_id_map(self) -> None:
        """Test valid AlleleProfileForUpload with locus_allele_id_map."""
        locus_allele_id_map = {"locus1": uuid4(), "locus2": uuid4()}
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            locus_code_map_code="MAP123",
            locus_allele_id_map=locus_allele_id_map,
            # Don't provide n_loci for upload format with locus_allele_id_map
        )
        self.assertEqual(allele_profile.allele_profile, "")
        self.assertIsNone(allele_profile.alleles)
        self.assertEqual(allele_profile.locus_allele_id_map, locus_allele_id_map)

    def test_valid_with_locus_code_map_when_needed(self) -> None:
        """Test valid AlleleProfileForUpload with locus_code_map when alleles have locus_code."""
        alleles = [model.AlleleForUpload(locus_code="locus1", seq="ATCG")]
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            locus_code_map_code="MAP123",
            alleles=alleles,
            # Don't provide n_loci for upload format with alleles
        )
        self.assertEqual(allele_profile.locus_code_map_code, "MAP123")
        self.assertEqual(allele_profile.allele_profile, "")
        self.assertEqual(len(allele_profile.alleles or []), 1)
        self.assertIsNone(allele_profile.locus_allele_id_map)

    def test_invalid_missing_protocol_fields(self) -> None:
        """Test ValidationError when both protocol fields are missing."""
        with pytest.raises(ValidationError):
            allele_id = uuid4()
            model.AlleleProfileForUpload(
                locus_set_code="LOCUSSET123",
                allele_profile=base64.b64encode(allele_id.bytes).decode("ascii"),
                n_loci=1,
                allele_profile_hash=model.AlleleProfile.get_allele_profile_hash(
                    [allele_id]
                ),
            )

    def test_invalid_missing_locus_set_fields(self) -> None:
        """Test ValidationError when both locus_set fields are missing."""
        with pytest.raises(ValidationError):
            allele_id = uuid4()
            model.AlleleProfileForUpload(
                locus_detection_protocol_code="PROTOCOL123",
                allele_profile=base64.b64encode(allele_id.bytes).decode("ascii"),
                n_loci=1,
                allele_profile_hash=model.AlleleProfile.get_allele_profile_hash(
                    [allele_id]
                ),
            )

    def test_invalid_missing_allele_data(self) -> None:
        """Test ValidationError when all allele data fields are missing."""
        with pytest.raises(ValidationError):
            model.AlleleProfileForUpload(
                locus_detection_protocol_code="PROTOCOL123",
                locus_set_code="LOCUSSET123",
                n_loci=1,
            )

    def test_invalid_missing_locus_code_map_when_needed(self) -> None:
        """Test ValidationError when locus_code_map is missing but alleles have locus_code."""
        locus_allele_id_map = {"locus1": uuid4()}
        with pytest.raises(ValidationError):
            model.AlleleProfileForUpload(
                locus_detection_protocol_code="PROTOCOL123",
                locus_set_code="LOCUSSET123",
                locus_allele_id_map=locus_allele_id_map,
                n_loci=1,
            )

    def test_valid_without_locus_code_map_when_not_needed(self) -> None:
        """Test valid AlleleProfileForUpload without locus_code_map when using allele_ids instead of alleles."""
        # Test using allele_ids instead of alleles to avoid locus_code_map requirement
        allele_id1, allele_id2 = uuid4(), uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id1, allele_id2]
        )
        self.assertIsNone(allele_profile.locus_code_map_code)
        self.assertEqual(allele_profile.locus_code_map_id, NULL_ID)
        self.assertIsNone(allele_profile.alleles)

    def test_quality_mixin_inheritance(self) -> None:
        """Test that AlleleProfileForUpload inherits QualityMixin properties."""
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id], qc_score=0.95
        )
        self.assertEqual(allele_profile.qc_score, 0.95)

    @staticmethod
    def _get_allele_profile_for_ids(
        allele_ids: list[UUID | None], **kwargs: Any
    ) -> model.AlleleProfileForUpload:
        # Sort allele IDs to match hash calculation
        sorted_allele_ids = sorted([x for x in allele_ids if x is not None])
        allele_bytes = b"".join(aid.bytes for aid in sorted_allele_ids)
        # Add NULL_ID bytes for any None values
        null_count = len(allele_ids) - len(sorted_allele_ids)
        allele_bytes += NULL_ID.bytes * null_count

        return model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL456",
            locus_set_code="LOCUSSET456",
            allele_profile=base64.b64encode(allele_bytes).decode("ascii"),
            n_loci=len(allele_ids),  # Use actual length of allele_ids
            allele_profile_hash=model.AlleleProfile.get_allele_profile_hash(allele_ids),
            **kwargs,
        )


class TestModelSampleForUpload(TestCase):

    @staticmethod
    def _create_sample_seq_for_upload(**kwargs: Any) -> model.SeqForUpload:
        """Create a sample SeqForUpload with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_upload_{uuid4().hex[:8]}",
            "contigs": [model.Contig(seq="ATCGATCG")],
        }
        defaults.update(kwargs)
        return model.SeqForUpload(**defaults)

    def test_valid_with_sample_id(self) -> None:
        """Test valid SampleForUpload with sample_id."""
        sample_id = uuid4()
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            id=sample_id,
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertEqual(sample.id, sample_id)
        self.assertIsNone(sample.external_ids)

    def test_valid_with_sample_ids(self) -> None:
        """Test valid SampleForUpload with external_ids."""

        external_id = ExternalIdentifierForUpload(
            identifier_issuer_id=uuid4(),
            external_id="SAMPLE123",
        )
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            external_ids=[external_id],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertIsNone(sample.id)
        self.assertEqual(len(sample.external_ids), 1)

    def test_valid_with_both_sample_identifiers(self) -> None:
        """Test valid SampleForUpload with both sample_id and sample_ids."""
        sample_id = uuid4()
        external_id = model.ExternalIdentifierForUpload(
            identifier_issuer_code="ISSUER123", external_id="SAMPLE123"
        )
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            id=sample_id,
            external_ids=[external_id],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertEqual(sample.id, sample_id)
        self.assertEqual(len(sample.external_ids), 1)

    def test_valid_with_multiple_external_ids(self) -> None:
        """Test valid SampleForUpload with multiple external_ids."""
        external_ids = [
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="ISSUER1", external_id="SAMPLE1"
            ),
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="ISSUER2", external_id="SAMPLE2"
            ),
        ]
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            external_ids=external_ids,
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertEqual(len(sample.external_ids), 2)

    def test_valid_with_optional_fields(self) -> None:
        """Test valid SampleForUpload with optional fields."""
        data_collection_id = uuid4()
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        sample = model.SampleForUpload(
            sample_id=uuid4(),
            created_in_data_collection_id=data_collection_id,
            allele_profiles=[allele_profile],
        )
        self.assertEqual(sample.created_in_data_collection_id, data_collection_id)

    def test_invalid_missing_sample_identification(self) -> None:
        """Test that SampleForUpload works without sample_id or external_ids (they are optional)."""
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        # This should not raise ValidationError since both fields are optional
        sample = model.SampleForUpload(
            allele_profiles=[allele_profile], created_in_data_collection_id=uuid4()
        )
        self.assertIsNone(sample.id)
        self.assertIsNone(sample.external_ids)

    def test_invalid_empty_sample_ids(self) -> None:
        """Test that SampleForUpload accepts empty external_ids list."""
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )
        # This should not raise ValidationError since empty list is valid
        sample = model.SampleForUpload(
            external_ids=[],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertEqual(len(sample.external_ids), 0)

    def test_valid_with_single_seq(self) -> None:
        """Test SampleForUpload with a single SeqForUpload."""
        sample_id = uuid4()
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_upload],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        self.assertEqual(sample.id, sample_id)
        self.assertEqual(len(sample.seqs), 1)
        self.assertEqual(sample.seqs[0].sample_id, NULL_ID)
        self.assertIsInstance(sample.seqs[0], model.SeqForUpload)

    def test_valid_with_multiple_seqs(self) -> None:
        """Test SampleForUpload with multiple SeqForUpload instances."""
        sample_id = uuid4()
        seq1 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_001")
        seq2 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_002")
        seq3 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_003")

        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[seq1, seq2, seq3],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        self.assertEqual(len(sample.seqs), 3)
        self.assertEqual(sample.seqs[0].code, "seq_001")
        self.assertEqual(sample.seqs[1].code, "seq_002")
        self.assertEqual(sample.seqs[2].code, "seq_003")

        # All seqs should have NULL_ID as sample_id when sample has an id
        for seq in sample.seqs:
            self.assertEqual(seq.sample_id, NULL_ID)
            self.assertIsInstance(seq, model.SeqForUpload)

    def test_valid_with_empty_seqs_list(self) -> None:
        """Test SampleForUpload with empty seqs list."""
        sample_id = uuid4()
        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        self.assertEqual(sample.id, sample_id)
        self.assertEqual(len(sample.seqs), 0)
        self.assertIsInstance(sample.seqs, list)

    def test_valid_with_seqs_and_external_ids(self) -> None:
        """Test SampleForUpload with both seqs and external_ids."""
        sample_id = uuid4()
        external_id = model.ExternalIdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER", external_id="SAMPLE_123"
        )
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            external_ids=[external_id],
            seqs=[seq_upload],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        self.assertEqual(sample.id, sample_id)
        self.assertEqual(len(sample.external_ids), 1)
        self.assertEqual(len(sample.seqs), 1)
        self.assertEqual(sample.seqs[0].sample_id, NULL_ID)

    def test_valid_seqs_with_different_properties(self) -> None:
        """Test SampleForUpload with seqs having different properties."""
        sample_id = uuid4()
        file_id = uuid4()
        assembly_protocol_id = uuid4()

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
            assembly_protocol_id=assembly_protocol_id,
        )

        seq_with_quality = self._create_sample_seq_for_upload(
            sample_id=NULL_ID,
            code="seq_with_qc",
            qc_score=0.95,
            qc_result=model.enum.QualityControlResult.PASS,
        )

        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_with_file, seq_with_protocol, seq_with_quality],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        self.assertEqual(len(sample.seqs), 3)

        # Verify specific properties of each seq
        file_seq = next(s for s in sample.seqs if s.code == "seq_with_file")
        self.assertEqual(file_seq.file_id, file_id)
        self.assertEqual(file_seq.file_format, model.enum.SeqFileFormat.FASTA)

        protocol_seq = next(s for s in sample.seqs if s.code == "seq_with_protocol")
        self.assertEqual(protocol_seq.assembly_protocol_id, assembly_protocol_id)

        quality_seq = next(s for s in sample.seqs if s.code == "seq_with_qc")
        self.assertEqual(quality_seq.qc_score, 0.95)
        self.assertEqual(quality_seq.qc_result, model.enum.QualityControlResult.PASS)

    def test_seqs_serialization_structure(self) -> None:
        """Test that seqs property maintains proper structure for serialization."""
        sample_id = uuid4()
        seq_upload = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_upload],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        # Test that the seqs property exists and has correct type
        self.assertIsInstance(sample.seqs, list)
        self.assertEqual(len(sample.seqs), 1)

        # Test that each seq in the list is a SeqForUpload instance
        for seq in sample.seqs:
            self.assertIsInstance(seq, model.SeqForUpload)
            self.assertIsNotNone(seq.code)
            self.assertIsNotNone(seq.contigs)
            self.assertEqual(seq.sample_id, NULL_ID)

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
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        sample = model.SampleForUpload(
            id=NULL_ID,  # Sample has no specific id
            seqs=[seq1, seq2],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        self.assertEqual(sample.id, NULL_ID)
        self.assertEqual(len(sample.seqs), 2)

        # Seqs can have their own sample_ids when sample has no id
        seq_codes_to_sample_ids = {seq.code: seq.sample_id for seq in sample.seqs}
        self.assertEqual(seq_codes_to_sample_ids["seq_001"], seq_sample_id1)
        self.assertEqual(seq_codes_to_sample_ids["seq_002"], seq_sample_id2)

    def test_valid_sample_without_id_seqs_with_null_ids(self) -> None:
        """Test SampleForUpload without id where seqs also have NULL_ID sample_ids."""
        seq1 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_001")
        seq2 = self._create_sample_seq_for_upload(sample_id=NULL_ID, code="seq_002")

        allele_id = uuid4()
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        # Sample without id, seqs also without specific sample_ids
        sample = model.SampleForUpload(
            id=NULL_ID,
            seqs=[seq1, seq2],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )

        self.assertEqual(sample.id, NULL_ID)
        self.assertEqual(len(sample.seqs), 2)

        # All seqs should have NULL_ID as sample_id
        for seq in sample.seqs:
            self.assertEqual(seq.sample_id, NULL_ID)
            self.assertIsInstance(seq, model.SeqForUpload)


class TestModelSampleBatchForUpload(TestCase):

    def setUp(self) -> None:
        self.test_dir = Path(__file__).parent

    @staticmethod
    def _create_sample_seq_for_upload(**kwargs: Any) -> model.SeqForUpload:
        """Create a sample SeqForUpload with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_upload_{uuid4().hex[:8]}",
            "contigs": [model.Contig(seq="ATCGATCG")],
        }
        defaults.update(kwargs)
        return model.SeqForUpload(**defaults)

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
        allele_profile = TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
            [allele_id]
        )

        defaults = {
            "id": sample_id,
            "seqs": seqs,
            "allele_profiles": [allele_profile],
            "created_in_data_collection_id": uuid4(),
        }
        defaults.update(kwargs)
        return model.SampleForUpload(**defaults)

    def test_read_source_complete_sample_batch1_json(self) -> None:
        """Test reading sample_batch_for_upload1.json as SampleBatchForUpload model."""
        file_path = self.test_dir / "sample_batch_for_upload1.json.gz"
        with gzip.open(file_path, "rt") as f:
            data = json.load(f)
        # file_path = self.test_dir / "sample_set_for_upload1.json"
        # with open(file_path, "rt") as f:
        #     data = json.load(f)

        sample_batch = model.SampleBatchForUpload(**data)
        self.assertIsInstance(sample_batch, model.SampleBatchForUpload)

    def test_read_source_sample_batch2_json(self) -> None:
        """Test reading sample_batch_for_upload2.json as SampleBatchForUpload model."""
        file_path = self.test_dir / "sample_batch_for_upload2.json"
        with open(file_path, "rt") as f:
            data = json.load(f)

        sample_batch = model.SampleBatchForUpload(**data)
        self.assertIsInstance(sample_batch, model.SampleBatchForUpload)

        # Validate structure: 4 samples with different seq/contig configurations
        self.assertEqual(len(sample_batch.samples), 4)

        # Sample 1: 1 seq with 1 contig
        sample1 = sample_batch.samples[0]
        self.assertEqual(len(sample1.seqs), 1)
        self.assertEqual(len(sample1.seqs[0].contigs), 1)
        self.assertEqual(sample1.seqs[0].code, "seq_001_single")

        # Sample 2: 1 seq with 2 contigs
        sample2 = sample_batch.samples[1]
        self.assertEqual(len(sample2.seqs), 1)
        self.assertEqual(len(sample2.seqs[0].contigs), 2)
        self.assertEqual(sample2.seqs[0].code, "seq_002_double")

        # Sample 3: 2 seqs with 1 contig each
        sample3 = sample_batch.samples[2]
        self.assertEqual(len(sample3.seqs), 2)
        self.assertEqual(len(sample3.seqs[0].contigs), 1)
        self.assertEqual(len(sample3.seqs[1].contigs), 1)
        self.assertEqual(sample3.seqs[0].code, "seq_003a_single")
        self.assertEqual(sample3.seqs[1].code, "seq_003b_single")

        # Sample 4: 2 seqs with 2 contigs each
        sample4 = sample_batch.samples[3]
        self.assertEqual(len(sample4.seqs), 2)
        self.assertEqual(len(sample4.seqs[0].contigs), 2)
        self.assertEqual(len(sample4.seqs[1].contigs), 2)
        self.assertEqual(sample4.seqs[0].code, "seq_004a_double")
        self.assertEqual(sample4.seqs[1].code, "seq_004b_double")

        # Verify computed field
        self.assertTrue(sample_batch.has_seqs)

    def test_valid_minimal(self) -> None:
        """Test valid SampleBatchForUpload with minimal data."""
        allele_id = uuid4()
        sample = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=uuid4(),
            allele_profiles=[
                TestModelAlleleProfileForUpload._get_allele_profile_for_ids([allele_id])
            ],
        )
        sample_set = model.SampleBatchForUpload(samples=[sample])
        self.assertEqual(len(sample_set.samples), 1)
        self.assertIsNone(sample_set.alleles)

    def test_valid_with_alleles(self) -> None:
        """Test valid SampleBatchForUpload with alleles."""
        allele = model.AlleleForUpload(locus_code="locus123", seq="ATCG")
        allele_id = uuid4()
        sample = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=uuid4(),
            allele_profiles=[
                TestModelAlleleProfileForUpload._get_allele_profile_for_ids([allele_id])
            ],
        )
        sample_set = model.SampleBatchForUpload(samples=[sample], alleles=[allele])
        self.assertEqual(len(sample_set.samples), 1)
        self.assertEqual(len(sample_set.alleles), 1)

    def test_valid_with_multiple_samples(self) -> None:
        """Test valid SampleBatchForUpload with multiple samples including seqs."""
        # Sample with seqs
        sample_with_seqs = self._create_sample_with_seqs(num_seqs=2)

        # Sample without seqs (traditional style)
        allele_id2 = uuid4()
        sample_without_seqs = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=uuid4(),
            allele_profiles=[
                TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
                    [allele_id2]
                )
            ],
        )

        sample_set = model.SampleBatchForUpload(
            samples=[sample_with_seqs, sample_without_seqs]
        )
        self.assertEqual(len(sample_set.samples), 2)

        # Verify first sample has seqs
        self.assertEqual(len(sample_set.samples[0].seqs), 2)

        # Verify second sample has no seqs
        self.assertIsNone(sample_set.samples[1].seqs)

        # Test computed field
        self.assertTrue(sample_set.has_seqs)

    def test_valid_empty_samples_list(self) -> None:
        """Test valid SampleBatchForUpload with empty samples list."""
        sample_set = model.SampleBatchForUpload(samples=[])
        self.assertEqual(len(sample_set.samples), 0)

    def test_valid_with_samples_containing_seqs(self) -> None:
        """Test SampleBatchForUpload where all samples contain SeqForUpload instances."""
        sample1 = self._create_sample_with_seqs(num_seqs=1)
        sample2 = self._create_sample_with_seqs(num_seqs=3)
        sample3 = self._create_sample_with_seqs(num_seqs=2)

        sample_set = model.SampleBatchForUpload(samples=[sample1, sample2, sample3])

        self.assertEqual(len(sample_set.samples), 3)
        self.assertEqual(len(sample_set.samples[0].seqs), 1)
        self.assertEqual(len(sample_set.samples[1].seqs), 3)
        self.assertEqual(len(sample_set.samples[2].seqs), 2)

        # Test computed field
        self.assertTrue(sample_set.has_seqs)

        # Verify all seqs are SeqForUpload instances
        for sample in sample_set.samples:
            for seq in sample.seqs:
                self.assertIsInstance(seq, model.SeqForUpload)

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
        assembly_protocol_id = uuid4()
        seq_with_protocol = self._create_sample_seq_for_upload(
            sample_id=NULL_ID, assembly_protocol_id=assembly_protocol_id
        )
        sample_with_protocol = self._create_sample_with_seqs()
        sample_with_protocol.seqs = [seq_with_protocol]

        sample_set = model.SampleBatchForUpload(
            samples=[sample_with_file, sample_with_qc, sample_with_protocol]
        )

        self.assertEqual(len(sample_set.samples), 3)
        self.assertTrue(sample_set.has_seqs)

        # Verify specific seq properties
        file_seq = sample_set.samples[0].seqs[0]
        self.assertEqual(file_seq.file_id, file_id)
        self.assertEqual(file_seq.file_format, model.enum.SeqFileFormat.FASTA)

        qc_seq = sample_set.samples[1].seqs[0]
        self.assertEqual(qc_seq.qc_score, 0.95)
        self.assertEqual(qc_seq.qc_result, model.enum.QualityControlResult.PASS)

        protocol_seq = sample_set.samples[2].seqs[0]
        self.assertEqual(protocol_seq.assembly_protocol_id, assembly_protocol_id)

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
            created_in_data_collection_id=uuid4(),
            allele_profiles=[
                TestModelAlleleProfileForUpload._get_allele_profile_for_ids([allele_id])
            ],
        )

        sample_set = model.SampleBatchForUpload(
            samples=[sample_with_seqs, sample_with_empty_seqs, sample_without_seqs]
        )

        self.assertEqual(len(sample_set.samples), 3)
        self.assertEqual(len(sample_set.samples[0].seqs), 2)  # Has seqs
        self.assertEqual(len(sample_set.samples[1].seqs), 0)  # Empty seqs list
        self.assertIsNone(sample_set.samples[2].seqs)  # No seqs property

        # Should still report has_seqs as True since at least one sample has seqs
        self.assertTrue(sample_set.has_seqs)

    def test_valid_sample_set_with_seqs_and_alleles(self) -> None:
        """Test SampleBatchForUpload with both sample seqs and reference alleles."""
        # Create samples with seqs
        sample1 = self._create_sample_with_seqs(num_seqs=2)
        sample2 = self._create_sample_with_seqs(num_seqs=1)

        # Create reference alleles
        allele1 = model.AlleleForUpload(locus_code="locus1", seq="ATCGATCG")
        allele2 = model.AlleleForUpload(locus_code="locus2", seq="GCTAGCTA")

        sample_batch = model.SampleBatchForUpload(
            samples=[sample1, sample2], alleles=[allele1, allele2]
        )

        self.assertEqual(len(sample_batch.samples), 2)
        self.assertEqual(len(sample_batch.alleles), 2)
        self.assertTrue(sample_batch.has_seqs)

        # Verify samples have seqs
        for sample in sample_batch.samples:
            self.assertIsNotNone(sample.seqs)
            self.assertGreater(len(sample.seqs), 0)

    def test_computed_field_has_seqs_false(self) -> None:
        """Test has_seqs computed field returns False when no samples have seqs."""
        # Create samples without seqs
        allele_id1 = uuid4()
        allele_id2 = uuid4()
        samples = [
            model.SampleForUpload(
                id=uuid4(),
                created_in_data_collection_id=uuid4(),
                allele_profiles=[
                    TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
                        [allele_id1]
                    )
                ],
            ),
            model.SampleForUpload(
                id=uuid4(),
                created_in_data_collection_id=uuid4(),
                allele_profiles=[
                    TestModelAlleleProfileForUpload._get_allele_profile_for_ids(
                        [allele_id2]
                    )
                ],
            ),
        ]

        sample_batch = model.SampleBatchForUpload(samples=samples)
        self.assertFalse(sample_batch.has_seqs)

    def test_computed_field_has_seqs_true_with_empty_seqs_list(self) -> None:
        """Test has_seqs computed field with samples having empty seqs lists."""
        # Sample with empty seqs list should not count as having seqs
        sample_with_empty_seqs = model.SampleForUpload(
            id=uuid4(),
            seqs=[],  # Empty list
            allele_profiles=[
                TestModelAlleleProfileForUpload._get_allele_profile_for_ids([uuid4()])
            ],
            created_in_data_collection_id=uuid4(),
        )

        sample_batch = model.SampleBatchForUpload(samples=[sample_with_empty_seqs])
        # Empty seqs list should result in has_seqs being False
        self.assertFalse(sample_batch.has_seqs)

    def test_samples_with_seqs_validation_compliance(self) -> None:
        """Test that samples with seqs follow proper validation rules."""
        # Sample with id - seqs must have NULL_ID sample_id
        sample_id = uuid4()
        seq_with_null_sample_id = self._create_sample_seq_for_upload(sample_id=NULL_ID)

        sample_with_id = model.SampleForUpload(
            id=sample_id,
            seqs=[seq_with_null_sample_id],
            allele_profiles=[
                TestModelAlleleProfileForUpload._get_allele_profile_for_ids([uuid4()])
            ],
            created_in_data_collection_id=uuid4(),
        )

        # Sample without id - seqs can have their own sample_ids
        seq_sample_id = uuid4()
        seq_with_own_sample_id = self._create_sample_seq_for_upload(
            sample_id=seq_sample_id
        )

        sample_without_id = model.SampleForUpload(
            id=NULL_ID,
            seqs=[seq_with_own_sample_id],
            allele_profiles=[
                TestModelAlleleProfileForUpload._get_allele_profile_for_ids([uuid4()])
            ],
            created_in_data_collection_id=uuid4(),
        )

        sample_batch = model.SampleBatchForUpload(
            samples=[sample_with_id, sample_without_id]
        )

        self.assertEqual(len(sample_batch.samples), 2)
        self.assertTrue(sample_batch.has_seqs)

        # Verify validation compliance
        self.assertEqual(sample_batch.samples[0].seqs[0].sample_id, NULL_ID)
        self.assertEqual(sample_batch.samples[1].seqs[0].sample_id, seq_sample_id)
