"""Implement seqdb sequence service behavior for services.seq.upload."""

from gen_epix.commondb.services import BatchUploader
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService
from gen_epix.seqdb.services.seq.upload_upsert_batch import (
    _create_sample_refdata,
    _update_profile_distances,
)
from gen_epix.seqdb.services.seq.upload_verify_batch import (
    _verify_sample_children,
    _verify_sample_refdata,
)


class SampleBatchUploader(BatchUploader):
    """Encapsulates validation and persistence of seqdb sample upload batches."""

    def __init__(
        self,
        service: BaseSeqService,
    ):
        """Configure upload processing for seqdb stored model fields."""
        super().__init__(
            command.UploadSamplesCommand,
            model.STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
            service,
        )

    def verify_batch(
        self,
        cmd: command.UploadSamplesCommand,
        batch_result: model.SampleBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """Check existence of parent model and child models."""
        success = True

        success &= self.verify_parents_identifiers(cmd, batch_result, uow)
        success &= self.verify_children_identifiers(cmd, batch_result, uow)
        success &= self.verify_parents(cmd, batch_result, uow)
        # Verify existence and consistency of child models as needed
        success &= _verify_sample_children(self, cmd, batch_result, uow)
        # Verify reference data
        success &= _verify_sample_refdata(self, cmd, batch_result, uow)
        # Verify immutable fields last: it needs the final status per item
        success &= self.verify_immutable_fields(cmd, batch_result, uow)

        return success

    def upsert_batch(
        self,
        cmd: command.UploadSamplesCommand,
        batch_result: model.SampleBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """Create or update the sample and any reference data."""
        success = True

        # Add any new reference data
        success &= _create_sample_refdata(self, cmd, batch_result, uow)
        # Upsert sample data
        success &= self.create_parents(cmd, batch_result, uow)
        success &= self.update_parents(cmd, batch_result, uow)
        # Upsert child models
        success &= self.create_children(cmd, batch_result, uow)
        success &= self.update_children(cmd, batch_result, uow)
        success &= _update_profile_distances(self, cmd, batch_result, uow)
        # Create parent and child Identifiers last since all parents and children with
        # identifiers first have to exist before a link can be created to them
        success &= self.create_parent_identifiers(cmd, batch_result, uow)
        success &= self.create_child_identifiers(cmd, batch_result, uow)

        return success


def seq_service_upload_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> model.SampleBatchUploadResult:
    """See command.UploadSamplesCommand for details."""
    sample_batch_uploader = SampleBatchUploader(self)
    batch_result: model.SampleBatchUploadResult = sample_batch_uploader.upload_batch(
        cmd
    )
    return batch_result
