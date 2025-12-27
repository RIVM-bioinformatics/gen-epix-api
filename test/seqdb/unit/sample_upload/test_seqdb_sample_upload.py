"""
Unit tests for SeqDB sample upload functionality.

Tests the seq_service_upload_samples function and its component steps.
"""

from unittest import TestCase
from uuid import uuid4

from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import UploadResult
from gen_epix.commondb.domain.model.organization import (
    ExternalIdentifierForUpload,
    User,
)
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import Role
from gen_epix.seqdb.services.seq.upload import _initialize_upload_result


class TestSeqServiceUploadSamples(TestCase):
    """Test the main seq_service_upload_samples function."""

    pass


class TestCheckUserRights(TestCase):
    """Test the _check_user_rights function."""

    pass


class TestInitializeUploadResult(TestCase):
    """Test the _initialize_upload_result function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.data_collection_id = uuid4()
        self.test_user = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.APP_ADMIN.value},
            organization_id=uuid4(),
            is_active=True,
        )

    def test_empty_sample_batch(self) -> None:
        """Test initializing upload result with empty sample batch."""
        batch_id = uuid4()
        sample_batch = model.SampleBatchForUpload(id=batch_id, samples=[])
        cmd = command.UploadSamplesCommand(
            user=self.test_user, sample_batch=sample_batch
        )

        result = _initialize_upload_result(cmd)

        # Verify batch-level result
        self.assertIsInstance(result, model.SampleBatchUploadResult)
        self.assertEqual(result.batch_id, batch_id)
        self.assertEqual(result.status, UploadStatus.SKIPPED)
        self.assertEqual(len(result.sample_results), 0)

    def test_single_minimal_sample(self) -> None:
        """Test initializing upload result with a single minimal sample."""
        batch_id = uuid4()
        sample_id = uuid4()

        # Create minimal sample with required fields
        sample = model.SampleForUpload(
            id=sample_id,
            created_in_data_collection_id=self.data_collection_id,
        )

        sample_batch = model.SampleBatchForUpload(id=batch_id, samples=[sample])
        cmd = command.UploadSamplesCommand(
            user=self.test_user, sample_batch=sample_batch
        )

        result = _initialize_upload_result(cmd)

        # Verify batch-level result
        self.assertEqual(result.batch_id, batch_id)
        self.assertEqual(result.status, UploadStatus.SKIPPED)
        self.assertEqual(len(result.sample_results), 1)

        # Verify sample-level result
        sample_result = result.sample_results[0]
        self.assertIsInstance(sample_result, model.SampleUploadResult)
        self.assertEqual(sample_result.status, UploadStatus.SKIPPED)

        # For minimal sample: props exists but is empty dict, so sample_result should be UploadResult
        self.assertIsNotNone(sample_result.sample_result)
        self.assertIsInstance(sample_result.sample_result, UploadResult)
        # Type guard: sample_result.sample_result is not None after the assertion above
        assert sample_result.sample_result is not None
        self.assertEqual(sample_result.sample_result.status, UploadStatus.SKIPPED)

        # All list fields should be None (no data provided)
        self.assertIsNone(sample_result.external_id_results)
        self.assertIsNone(sample_result.read_set_results)
        self.assertIsNone(sample_result.seq_results)
        self.assertIsNone(sample_result.seq_taxonomy_results)
        self.assertIsNone(sample_result.seq_classification_results)
        self.assertIsNone(sample_result.locus_profile_results)
        self.assertIsNone(sample_result.allele_profile_results)
        self.assertIsNone(sample_result.snp_profile_results)
        self.assertIsNone(sample_result.mlva_profile_results)
        self.assertIsNone(sample_result.kmer_profile_results)
        self.assertIsNone(sample_result.distance_results)
        self.assertIsNone(sample_result.pcr_measurement_results)
        self.assertIsNone(sample_result.ast_measurement_results)

    def test_sample_with_all_data_types(self) -> None:
        """Test initializing upload result with a sample containing all data types."""
        batch_id = uuid4()
        sample_id = uuid4()

        # Create sample with all associated data types
        sample = model.SampleForUpload(
            id=sample_id,
            created_in_data_collection_id=self.data_collection_id,
            props={"key": "value"},  # Sample has props
            external_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_code="TEST_ISSUER", identifier="TEST_ID_1"
                ),
                ExternalIdentifierForUpload(
                    identifier_issuer_code="TEST_ISSUER", identifier="TEST_ID_2"
                ),
            ],
            read_sets=[
                model.ReadSetForUpload(
                    sample_id=sample_id,
                    sequencing_protocol_id=uuid4(),
                ),
                model.ReadSetForUpload(
                    sample_id=sample_id,
                    sequencing_protocol_id=uuid4(),
                ),
                model.ReadSetForUpload(
                    sample_id=sample_id,
                    sequencing_protocol_id=uuid4(),
                ),
            ],
            seqs=[
                model.SeqForUpload(
                    sample_id=sample_id,
                    code="seq_1",
                    contigs=[model.Contig(seq="ATCGATCG")],
                ),
                model.SeqForUpload(
                    sample_id=sample_id,
                    code="seq_2",
                    contigs=[model.Contig(seq="GCTAGCTA")],
                ),
            ],
            allele_profiles=[
                model.AlleleProfileForUpload(
                    sample_id=sample_id,
                    locus_detection_protocol_id=uuid4(),
                    locus_set_id=uuid4(),
                    locus_code_map_id=uuid4(),
                    locus_allele_id_map={
                        "locus1": uuid4(),
                        "locus2": uuid4(),
                    },
                )
            ],
            # Add other data types as needed for comprehensive testing
            pcr_measurements=[
                model.PcrMeasurement(
                    sample_id=sample_id, pcr_protocol_id=uuid4(), pcr_result="positive"
                ),
                model.PcrMeasurement(
                    sample_id=sample_id, pcr_protocol_id=uuid4(), pcr_result="negative"
                ),
            ],
            ast_measurements=[
                model.AstMeasurement(
                    sample_id=sample_id, ast_protocol_id=uuid4(), ast_result="resistant"
                )
            ],
        )

        sample_batch = model.SampleBatchForUpload(id=batch_id, samples=[sample])
        cmd = command.UploadSamplesCommand(
            user=self.test_user, sample_batch=sample_batch
        )

        result = _initialize_upload_result(cmd)

        # Verify sample-level result
        sample_result = result.sample_results[0]

        # Verify that results are created for provided data
        self.assertIsNotNone(sample_result.sample_result)  # Props provided
        self.assertIsInstance(sample_result.sample_result, UploadResult)
        # Type guard: sample_result.sample_result is not None after the assertion above
        assert sample_result.sample_result is not None
        self.assertEqual(sample_result.sample_result.status, UploadStatus.SKIPPED)

        # Verify external ID results (2 items)
        self.assertIsNotNone(sample_result.external_id_results)
        # Type guard: external_id_results is not None after the assertion above
        assert sample_result.external_id_results is not None
        self.assertEqual(len(sample_result.external_id_results), 2)
        for ext_id_result in sample_result.external_id_results:
            self.assertIsInstance(ext_id_result, UploadResult)
            self.assertEqual(ext_id_result.status, UploadStatus.SKIPPED)

        # Verify read set results (3 items)
        self.assertIsNotNone(sample_result.read_set_results)
        # Type guard: read_set_results is not None after the assertion above
        assert sample_result.read_set_results is not None
        self.assertEqual(len(sample_result.read_set_results), 3)
        for read_set_result in sample_result.read_set_results:
            self.assertIsInstance(read_set_result, UploadResult)
            self.assertEqual(read_set_result.status, UploadStatus.SKIPPED)

        # Verify seq results (2 items)
        self.assertIsNotNone(sample_result.seq_results)
        # Type guard: seq_results is not None after the assertion above
        assert sample_result.seq_results is not None
        self.assertEqual(len(sample_result.seq_results), 2)
        for seq_result in sample_result.seq_results:
            self.assertIsInstance(seq_result, UploadResult)
            self.assertEqual(seq_result.status, UploadStatus.SKIPPED)

        # Verify allele profile results (1 item)
        self.assertIsNotNone(sample_result.allele_profile_results)
        # Type guard: allele_profile_results is not None after the assertion above
        assert sample_result.allele_profile_results is not None
        self.assertEqual(len(sample_result.allele_profile_results), 1)
        self.assertIsInstance(sample_result.allele_profile_results[0], UploadResult)
        self.assertEqual(
            sample_result.allele_profile_results[0].status, UploadStatus.SKIPPED
        )

        # Verify PCR measurement results (2 items)
        self.assertIsNotNone(sample_result.pcr_measurement_results)
        # Type guard: pcr_measurement_results is not None after the assertion above
        assert sample_result.pcr_measurement_results is not None
        self.assertEqual(len(sample_result.pcr_measurement_results), 2)
        for pcr_result in sample_result.pcr_measurement_results:
            self.assertIsInstance(pcr_result, UploadResult)
            self.assertEqual(pcr_result.status, UploadStatus.SKIPPED)

        # Verify AST measurement results (1 item)
        self.assertIsNotNone(sample_result.ast_measurement_results)
        # Type guard: ast_measurement_results is not None after the assertion above
        assert sample_result.ast_measurement_results is not None
        self.assertEqual(len(sample_result.ast_measurement_results), 1)
        self.assertIsInstance(sample_result.ast_measurement_results[0], UploadResult)
        self.assertEqual(
            sample_result.ast_measurement_results[0].status, UploadStatus.SKIPPED
        )

        # Verify that data types not provided remain None
        self.assertIsNone(sample_result.seq_taxonomy_results)
        self.assertIsNone(sample_result.seq_classification_results)
        self.assertIsNone(sample_result.locus_profile_results)
        self.assertIsNone(sample_result.snp_profile_results)
        self.assertIsNone(sample_result.mlva_profile_results)
        self.assertIsNone(sample_result.kmer_profile_results)
        self.assertIsNone(sample_result.distance_results)

    def test_multiple_samples(self) -> None:
        """Test initializing upload result with multiple samples."""
        batch_id = uuid4()

        # Create multiple samples with different data configurations
        sample1 = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=self.data_collection_id,
            external_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_code="TEST", identifier="SAMPLE_1"
                )
            ],
        )

        sample2 = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=self.data_collection_id,
            seqs=[
                model.SeqForUpload(
                    sample_id=NULL_ID,
                    code="seq_for_sample2",
                    contigs=[model.Contig(seq="ATCGATCG")],
                )
            ],
        )

        sample3 = model.SampleForUpload(
            id=uuid4(),
            created_in_data_collection_id=self.data_collection_id,
            props={"metadata": "sample3"},
        )

        sample_batch = model.SampleBatchForUpload(
            id=batch_id, samples=[sample1, sample2, sample3]
        )
        cmd = command.UploadSamplesCommand(
            user=self.test_user, sample_batch=sample_batch
        )

        result = _initialize_upload_result(cmd)

        # Verify batch-level result
        self.assertEqual(result.batch_id, batch_id)
        self.assertEqual(result.status, UploadStatus.SKIPPED)
        self.assertEqual(len(result.sample_results), 3)

        # Verify sample1 results (has external_ids)
        sample1_result = result.sample_results[0]
        self.assertIsInstance(
            sample1_result.sample_result, UploadResult
        )  # Props exist as empty dict
        self.assertIsNotNone(sample1_result.external_id_results)
        # Type guard: external_id_results is not None after the assertion above
        assert sample1_result.external_id_results is not None
        self.assertEqual(len(sample1_result.external_id_results), 1)
        self.assertIsNone(sample1_result.seq_results)

        # Verify sample2 results (has seqs)
        sample2_result = result.sample_results[1]
        self.assertIsInstance(
            sample2_result.sample_result, UploadResult
        )  # Props exist as empty dict
        self.assertIsNone(sample2_result.external_id_results)
        self.assertIsNotNone(sample2_result.seq_results)
        # Type guard: seq_results is not None after the assertion above
        assert sample2_result.seq_results is not None
        self.assertEqual(len(sample2_result.seq_results), 1)

        # Verify sample3 results (has props)
        sample3_result = result.sample_results[2]
        self.assertIsInstance(sample3_result.sample_result, UploadResult)  # Has props
        self.assertIsNone(sample3_result.external_id_results)
        self.assertIsNone(sample3_result.seq_results)

    def test_empty_lists_vs_none_distinction(self) -> None:
        """Test that empty lists and None are handled correctly."""
        batch_id = uuid4()
        sample_id = uuid4()

        # Create sample with empty lists (not None)
        sample = model.SampleForUpload(
            id=sample_id,
            created_in_data_collection_id=self.data_collection_id,
            external_ids=[],  # Empty list
            read_sets=[],  # Empty list
            seqs=None,  # Explicitly None
        )

        sample_batch = model.SampleBatchForUpload(id=batch_id, samples=[sample])
        cmd = command.UploadSamplesCommand(
            user=self.test_user, sample_batch=sample_batch
        )

        result = _initialize_upload_result(cmd)
        sample_result = result.sample_results[0]

        # Empty lists should result in empty result lists
        self.assertIsNotNone(sample_result.external_id_results)
        # Type guard: external_id_results is not None after the assertion above
        assert sample_result.external_id_results is not None
        self.assertEqual(len(sample_result.external_id_results), 0)

        self.assertIsNotNone(sample_result.read_set_results)
        # Type guard: read_set_results is not None after the assertion above
        assert sample_result.read_set_results is not None
        self.assertEqual(len(sample_result.read_set_results), 0)

        # None should result in None
        self.assertIsNone(sample_result.seq_results)

    def test_upload_result_object_independence(self) -> None:
        """Test that each UploadResult object is independent (no shared references)."""
        batch_id = uuid4()
        sample_id = uuid4()

        sample = model.SampleForUpload(
            id=sample_id,
            created_in_data_collection_id=self.data_collection_id,
            external_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_code="TEST", identifier="ID1"
                ),
                ExternalIdentifierForUpload(
                    identifier_issuer_code="TEST", identifier="ID2"
                ),
            ],
        )

        sample_batch = model.SampleBatchForUpload(id=batch_id, samples=[sample])
        cmd = command.UploadSamplesCommand(
            user=self.test_user, sample_batch=sample_batch
        )

        result = _initialize_upload_result(cmd)
        sample_result = result.sample_results[0]

        # Verify that each UploadResult reflects the source object's ID
        self.assertIsNotNone(sample_result.external_id_results)
        # Type guard: external_id_results is not None after the assertion above
        assert sample_result.external_id_results is not None
        upload_result1 = sample_result.external_id_results[0]
        upload_result2 = sample_result.external_id_results[1]

        # ExternalIdentifierForUpload objects don't have an id field, so UploadResult id should be None
        self.assertIsNone(upload_result1.id)
        self.assertIsNone(upload_result2.id)

        # Verify they have the same status but are different objects
        self.assertEqual(upload_result1.status, UploadStatus.SKIPPED)
        self.assertEqual(upload_result2.status, UploadStatus.SKIPPED)
        self.assertIsNot(upload_result1, upload_result2)

    def test_upload_result_reflects_source_object_ids(self) -> None:
        """Test that UploadResult objects properly reflect the ID of their source objects."""
        batch_id = uuid4()
        sample_id = uuid4()
        seq_id_1 = uuid4()
        seq_id_2 = uuid4()

        sample = model.SampleForUpload(
            id=sample_id,
            created_in_data_collection_id=self.data_collection_id,
            seqs=[
                model.SeqForUpload(
                    id=seq_id_1,
                    sample_id=sample_id,
                    code="seq_1",
                    contigs=[model.Contig(seq="ATCGATCG")],
                ),
                model.SeqForUpload(
                    id=seq_id_2,
                    sample_id=sample_id,
                    code="seq_2",
                    contigs=[model.Contig(seq="GCTAGCTA")],
                ),
            ],
        )

        sample_batch = model.SampleBatchForUpload(id=batch_id, samples=[sample])
        cmd = command.UploadSamplesCommand(
            user=self.test_user, sample_batch=sample_batch
        )

        result = _initialize_upload_result(cmd)
        sample_result = result.sample_results[0]

        # Verify that UploadResult objects have the correct IDs from their source objects
        self.assertIsNotNone(sample_result.seq_results)
        # Type guard: seq_results is not None after the assertion above
        assert sample_result.seq_results is not None
        seq_result_1 = sample_result.seq_results[0]
        seq_result_2 = sample_result.seq_results[1]

        self.assertEqual(seq_result_1.id, seq_id_1)
        self.assertEqual(seq_result_2.id, seq_id_2)
        self.assertEqual(seq_result_1.status, UploadStatus.SKIPPED)
        self.assertEqual(seq_result_2.status, UploadStatus.SKIPPED)

        # Verify sample_result has None id because sample.props doesn't have an id
        self.assertIsNotNone(sample_result.sample_result)
        # Type guard: sample_result is not None after the assertion above
        assert sample_result.sample_result is not None
        self.assertIsNone(sample_result.sample_result.id)


class TestVerifyUploadDataExistence(TestCase):
    """Test the _verify_upload_data_existence function."""

    pass


class TestRetrieveAndVerifyReferenceData(TestCase):
    """Test the _retrieve_and_verify_reference_data function."""

    pass


class TestCreateOrUpdateData(TestCase):
    """Test the _create_or_update_data function."""

    pass
