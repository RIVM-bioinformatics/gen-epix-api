"""
Unit tests for IDSDB ETL model classes.

Tests the ExternalIdentifier, AlleleForUpload, AlleleProfileForUpload,
and SampleSetForUpload models with various validation scenarios.
"""

import gzip
import json
from pathlib import Path
from unittest import TestCase
from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.seqdb.domain import model


class TestModelExternalIdentifier(TestCase):

    def test_valid_with_identifier_issuer_code(self) -> None:
        """Test valid ExternalIdentifier with identifier_issuer_code."""
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER", identifier="SAMPLE123"
        )
        self.assertEqual(identifier.identifier_issuer_code, "TEST_ISSUER")
        self.assertIsNone(identifier.identifier_issuer_id)
        self.assertEqual(identifier.identifier, "SAMPLE123")

    def test_valid_with_identifier_issuer_id(self) -> None:
        """Test valid ExternalIdentifier with identifier_issuer_id."""
        issuer_id = uuid4()
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_id=issuer_id, identifier="SAMPLE123"
        )
        self.assertIsNone(identifier.identifier_issuer_code)
        self.assertEqual(identifier.identifier_issuer_id, issuer_id)
        self.assertEqual(identifier.identifier, "SAMPLE123")

    def test_valid_with_both_issuer_fields(self) -> None:
        """Test valid ExternalIdentifier with both issuer fields."""
        issuer_id = uuid4()
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER",
            identifier_issuer_id=issuer_id,
            identifier="SAMPLE123",
        )
        self.assertEqual(identifier.identifier_issuer_code, "TEST_ISSUER")
        self.assertEqual(identifier.identifier_issuer_id, issuer_id)

    def test_invalid_missing_both_issuer_fields(self) -> None:
        """Test ValidationError when both issuer fields are missing."""
        with pytest.raises(ValidationError):
            model.ExternalIdentifierForUpload(identifier="SAMPLE123")

    def test_max_length_validation(self) -> None:
        """Test field length validation."""
        # Valid lengths
        identifier = model.ExternalIdentifierForUpload(
            identifier_issuer_code="A" * 255, identifier="B" * 255
        )
        self.assertEqual(len(identifier.identifier_issuer_code or []), 255)
        self.assertEqual(len(identifier.identifier), 255)
        # Exceeding max lengths
        with pytest.raises(ValidationError):
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="A" * 256, identifier="B" * 255
            )
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="A" * 255, identifier="B" * 256
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
        # Verify id is set to seq_hash
        self.assertEqual(allele.id, allele.seq_hash)

    def test_valid_with_locus_code_only(self) -> None:
        """Test valid AlleleForUpload with only locus_code."""
        allele = model.AlleleForUpload(locus_code="locus123", seq="ATCG")
        self.assertEqual(allele.locus_id, NULL_ID)
        self.assertEqual(allele.locus_code, "locus123")
        # Verify id is set to seq_hash
        self.assertEqual(allele.id, allele.seq_hash)

    def test_valid_with_both_locus_fields(self) -> None:
        """Test valid AlleleForUpload with both locus fields."""
        locus_id = uuid4()
        allele = model.AlleleForUpload(
            locus_id=locus_id, locus_code="locus123", seq="ATCG"
        )
        self.assertEqual(allele.locus_id, locus_id)
        self.assertEqual(allele.locus_code, "locus123")
        # Verify id is set to seq_hash
        self.assertEqual(allele.id, allele.seq_hash)

    def test_invalid_missing_both_locus_fields(self) -> None:
        """Test ValidationError when both locus fields are missing."""
        with pytest.raises(ValidationError):
            model.AlleleForUpload(seq="ATCG")

    def test_inheritance_from_seqdb_allele(self) -> None:
        """Test that AlleleForUpload inherits seqdb.Allele properties."""
        allele = model.AlleleForUpload(locus_code="locus123", seq="ATCG", length=4)
        # Verify id is set to seq_hash
        self.assertEqual(allele.id, allele.seq_hash)
        self.assertEqual(allele.seq, "atcg")  # seq is normalized to lowercase
        self.assertEqual(allele.length, 4)

    def test_id_seq_hash_constraint(self) -> None:
        """Test that id must equal seq_hash when both are provided."""
        # This should work - providing matching id and seq_hash
        import hashlib
        from uuid import UUID

        sequence = "ATCG"
        expected_hash = UUID(
            hashlib.sha256(sequence.lower().encode("ascii")).digest()[:16].hex()
        )

        allele = model.AlleleForUpload(
            locus_code="locus123", seq=sequence, id=expected_hash
        )
        self.assertEqual(allele.id, expected_hash)
        self.assertEqual(allele.seq_hash, expected_hash)

    def test_invalid_mismatched_id_seq_hash(self) -> None:
        """Test ValidationError when id doesn't match computed seq_hash."""
        with pytest.raises(ValidationError):
            model.AlleleForUpload(
                locus_code="locus123",
                seq="ATCG",
                id=uuid4(),  # Random id that won't match computed seq_hash
            )


class TestModelAlleleProfileForUpload(TestCase):

    def test_valid_with_protocol_code_and_locus_set_code(self) -> None:
        """Test valid AlleleProfileForUpload with codes."""
        allele_id1, allele_id2 = uuid4(), uuid4()
        profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id1, allele_id2],
            n_loci=2,
            allele_profile=f"{allele_id1},{allele_id2}",
            allele_profile_hash=uuid4(),
        )
        self.assertEqual(profile.locus_detection_protocol_code, "PROTOCOL123")
        self.assertEqual(profile.locus_set_code, "LOCUSSET123")
        self.assertEqual(profile.locus_detection_protocol_id, NULL_ID)
        self.assertEqual(profile.locus_set_id, NULL_ID)

    def test_valid_with_protocol_id_and_locus_set_id(self) -> None:
        """Test valid AlleleProfileForUpload with IDs."""
        protocol_id = uuid4()
        locus_set_id = uuid4()
        allele_id1, allele_id2 = uuid4(), uuid4()
        profile = model.AlleleProfileForUpload(
            locus_detection_protocol_id=protocol_id,
            locus_set_id=locus_set_id,
            allele_ids=[allele_id1, allele_id2],
            n_loci=2,
            allele_profile=f"{allele_id1},{allele_id2}",
            allele_profile_hash=uuid4(),
        )
        self.assertEqual(profile.locus_detection_protocol_id, protocol_id)
        self.assertEqual(profile.locus_set_id, locus_set_id)
        self.assertIsNone(profile.locus_detection_protocol_code)
        self.assertIsNone(profile.locus_set_code)

    def test_valid_with_alleles(self) -> None:
        """Test valid AlleleProfileForUpload with alleles."""
        alleles = [
            model.AlleleForUpload(locus_code="locus1", seq="ATCG"),
            model.AlleleForUpload(locus_code="locus2", seq="GCTA"),
        ]
        allele_ids = [alleles[0].id, alleles[1].id]
        profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            locus_code_map_code="MAP123",
            alleles=alleles,
            n_loci=2,
            allele_profile=f"{allele_ids[0]},{allele_ids[1]}",
            allele_profile_hash=uuid4(),
        )
        self.assertEqual(len(profile.alleles), 2)
        self.assertIsNone(profile.allele_ids)

    def test_valid_with_locus_allele_id_map(self) -> None:
        """Test valid AlleleProfileForUpload with locus_allele_id_map."""
        allele_map = {"locus1": uuid4(), "locus2": uuid4()}
        allele_ids = list(allele_map.values())
        profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            locus_allele_id_map=allele_map,
            n_loci=2,
            allele_profile=f"{allele_ids[0]},{allele_ids[1]}",
            allele_profile_hash=uuid4(),
        )
        self.assertEqual(profile.locus_allele_id_map, allele_map)
        self.assertIsNone(profile.allele_ids)
        self.assertIsNone(profile.alleles)

    def test_valid_with_locus_code_map_when_needed(self) -> None:
        """Test valid AlleleProfileForUpload with locus_code_map when alleles have locus_code."""
        alleles = [model.AlleleForUpload(locus_code="locus1", seq="ATCG")]
        profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            locus_code_map_code="MAP123",
            alleles=alleles,
            n_loci=1,
            allele_profile=str(alleles[0].id),
            allele_profile_hash=uuid4(),
        )
        self.assertEqual(profile.locus_code_map_code, "MAP123")

    def test_invalid_missing_protocol_fields(self) -> None:
        """Test ValidationError when both protocol fields are missing."""
        with pytest.raises(ValidationError):
            allele_id = uuid4()
            model.AlleleProfileForUpload(
                locus_set_code="LOCUSSET123",
                allele_ids=[allele_id],
                n_loci=1,
                allele_profile=[allele_id],
                allele_profile_hash=uuid4(),
            )

    def test_invalid_missing_locus_set_fields(self) -> None:
        """Test ValidationError when both locus_set fields are missing."""
        with pytest.raises(ValidationError):
            allele_id = uuid4()
            model.AlleleProfileForUpload(
                locus_detection_protocol_code="PROTOCOL123",
                allele_ids=[allele_id],
                n_loci=1,
                allele_profile=[allele_id],
                allele_profile_hash=uuid4(),
            )

    def test_invalid_missing_allele_data(self) -> None:
        """Test ValidationError when all allele data fields are missing."""
        with pytest.raises(ValidationError):
            model.AlleleProfileForUpload(
                locus_detection_protocol_code="PROTOCOL123",
                locus_set_code="LOCUSSET123",
                n_loci=1,
                allele_profile=[uuid4()],
                allele_profile_hash=uuid4(),
            )

    def test_invalid_missing_locus_code_map_when_needed(self) -> None:
        """Test ValidationError when locus_code_map is missing but alleles have locus_code."""
        alleles = [model.AlleleForUpload(locus_code="locus1", seq="ATCG")]
        with pytest.raises(ValidationError):
            model.AlleleProfileForUpload(
                locus_detection_protocol_code="PROTOCOL123",
                locus_set_code="LOCUSSET123",
                alleles=alleles,
                n_loci=1,
                allele_profile=[alleles[0].id],
                allele_profile_hash=uuid4(),
            )

    def test_valid_without_locus_code_map_when_not_needed(self) -> None:
        """Test valid AlleleProfileForUpload without locus_code_map when using allele_ids instead of alleles."""
        # Test using allele_ids instead of alleles to avoid locus_code_map requirement
        allele_id1, allele_id2 = uuid4(), uuid4()
        profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id1, allele_id2],
            n_loci=2,
            allele_profile=f"{allele_id1},{allele_id2}",
            allele_profile_hash=uuid4(),
        )
        self.assertIsNone(profile.locus_code_map_code)
        self.assertEqual(profile.locus_code_map_id, NULL_ID)
        self.assertIsNone(profile.alleles)

    def test_quality_mixin_inheritance(self) -> None:
        """Test that AlleleProfileForUpload inherits QualityMixin properties."""
        allele_id = uuid4()
        profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
            qc_score=0.95,
        )
        self.assertEqual(profile.qc_score, 0.95)


class TestModelSampleForUpload(TestCase):

    def test_valid_with_sample_id(self) -> None:
        """Test valid SampleForUpload with sample_id."""
        sample_id = uuid4()
        allele_id = uuid4()
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
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
        from gen_epix.commondb.domain.enum import IdentifierType
        from gen_epix.commondb.domain.model.organization import ExternalIdentifier

        external_id = ExternalIdentifier(
            identifier_type=IdentifierType.SAMPLE_ID,
            identifier_issuer_id=uuid4(),
            external_id="SAMPLE123",
            internal_id=uuid4(),
        )
        allele_id = uuid4()
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
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
            identifier_issuer_code="ISSUER123", identifier="SAMPLE123"
        )
        allele_id = uuid4()
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
        )
        sample = model.SampleForUpload(
            id=sample_id,
            external_ids=[external_id],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertEqual(sample.id, sample_id)
        self.assertEqual(len(sample.external_ids), 1)

    def test_valid_with_multiple_sample_ids(self) -> None:
        """Test valid SampleForUpload with multiple sample_ids."""
        sample_ids = [
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="ISSUER1", identifier="SAMPLE1"
            ),
            model.ExternalIdentifierForUpload(
                identifier_issuer_code="ISSUER2", identifier="SAMPLE2"
            ),
        ]
        allele_id = uuid4()
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
        )
        sample = model.SampleForUpload(
            sample_ids=sample_ids,
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertEqual(len(sample.external_ids), 2)

    def test_valid_with_optional_fields(self) -> None:
        """Test valid SampleForUpload with optional fields."""
        data_collection_id = uuid4()
        allele_id = uuid4()
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
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
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
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
        allele_profile = model.AlleleProfileForUpload(
            locus_detection_protocol_code="PROTOCOL123",
            locus_set_code="LOCUSSET123",
            allele_ids=[allele_id],
            n_loci=1,
            allele_profile=str(allele_id),
            allele_profile_hash=uuid4(),
        )
        # This should not raise ValidationError since empty list is valid
        sample = model.SampleForUpload(
            external_ids=[],
            allele_profiles=[allele_profile],
            created_in_data_collection_id=uuid4(),
        )
        self.assertEqual(len(sample.external_ids), 0)


class TestModelSampleSetForUpload(TestCase):

    def setUp(self) -> None:
        self.test_dir = Path(__file__).parent

    def test_read_source_complete_sample_set1_json(self) -> None:
        """Test reading sample_set_for_upload1.json as SampleSetForUpload model."""
        file_path = self.test_dir / "sample_set_for_upload1.json.gz"

        with gzip.open(file_path, "rt") as f:
            data = json.load(f)

        complete_sample_set = model.SampleSetForUpload(**data)
        self.assertIsInstance(complete_sample_set, model.SampleSetForUpload)

    def test_valid_minimal(self) -> None:
        """Test valid SampleSetForUpload with minimal data."""
        allele_id = uuid4()
        sample = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=uuid4(),
            allele_profiles=[
                model.AlleleProfileForUpload(
                    locus_detection_protocol_code="PROTOCOL123",
                    locus_set_code="LOCUSSET123",
                    allele_ids=[allele_id],
                    n_loci=1,
                    allele_profile=str(allele_id),
                    allele_profile_hash=uuid4(),
                )
            ],
        )
        sample_set = model.SampleSetForUpload(samples=[sample])
        self.assertEqual(len(sample_set.samples), 1)
        self.assertIsNone(sample_set.alleles)

    def test_valid_with_alleles(self) -> None:
        """Test valid SampleSetForUpload with alleles."""
        allele = model.AlleleForUpload(locus_code="locus123", seq="ATCG")
        allele_id = uuid4()
        sample = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=uuid4(),
            allele_profiles=[
                model.AlleleProfileForUpload(
                    locus_detection_protocol_code="PROTOCOL123",
                    locus_set_code="LOCUSSET123",
                    allele_ids=[allele_id],
                    n_loci=1,
                    allele_profile=str(allele_id),
                    allele_profile_hash=uuid4(),
                )
            ],
        )
        sample_set = model.SampleSetForUpload(samples=[sample], alleles=[allele])
        self.assertEqual(len(sample_set.samples), 1)
        self.assertEqual(len(sample_set.alleles), 1)

    def test_valid_with_multiple_samples(self) -> None:
        """Test valid SampleSetForUpload with multiple samples."""
        allele_id1 = uuid4()
        allele_id2 = uuid4()
        samples = [
            model.SampleForUpload(
                sample_id=uuid4(),
                created_in_data_collection_id=uuid4(),
                allele_profiles=[
                    model.AlleleProfileForUpload(
                        locus_detection_protocol_code="PROTOCOL123",
                        locus_set_code="LOCUSSET123",
                        allele_ids=[allele_id1],
                        n_loci=1,
                        allele_profile=str(allele_id1),
                        allele_profile_hash=uuid4(),
                    )
                ],
            ),
            model.SampleForUpload(
                sample_id=uuid4(),
                created_in_data_collection_id=uuid4(),
                allele_profiles=[
                    model.AlleleProfileForUpload(
                        locus_detection_protocol_code="PROTOCOL456",
                        locus_set_code="LOCUSSET456",
                        allele_ids=[allele_id2],
                        n_loci=1,
                        allele_profile=str(allele_id2),
                        allele_profile_hash=uuid4(),
                    )
                ],
            ),
        ]
        sample_set = model.SampleSetForUpload(samples=samples)
        self.assertEqual(len(sample_set.samples), 2)

    def test_valid_empty_samples_list(self) -> None:
        """Test valid SampleSetForUpload with empty samples list."""
        sample_set = model.SampleSetForUpload(samples=[])
        self.assertEqual(len(sample_set.samples), 0)
