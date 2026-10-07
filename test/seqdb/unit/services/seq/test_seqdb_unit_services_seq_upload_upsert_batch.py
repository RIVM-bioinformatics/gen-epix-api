"""Tests for sequence batch upsert behavior."""

from test.seqdb.unit.services.seq.test_seqdb_unit_services_seq_upload_verify_batch import (
    BaseUploadTestCase,
)
from uuid import uuid4

import pytest

from gen_epix.etl.enum import EtlStatus
from gen_epix.seqdb.domain import model


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
        assert success
        assert batch_result.seq_distances is None
        assert batch_result.has_log_code("b3e1f49a")
        # Sample result must not be FAILED.
        assert profile_result.status != EtlStatus.FAILED

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

        assert success
        assert batch_result.seq_distances is None
        self.service.app.handle.assert_not_called()
