from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.services import BatchUploader
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService
from gen_epix.seqdb.services.seq.upload_upsert_batch import _create_sample_refdata
from gen_epix.seqdb.services.seq.upload_verify_batch import (
    _verify_sample_children,
    _verify_sample_refdata,
)


class SampleBatchUploader(BatchUploader):

    def __init__(
        self,
        service: BaseSeqService,
    ):
        super().__init__(
            command.UploadSamplesCommand,
            model.STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
            service,
        )

    def verify_user_rights(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> None:
        """
        Verify if the user has the necessary rights to upload samples.
        """
        user_roles = cmd.user.roles if cmd.user else set()

        # If user has any of the roles in the GE_APP_ADMIN role set, they are authorized
        if user_roles & enum.RoleSet.GE_APP_ADMIN.value:
            return  # User is authorized

        # If user does not have any of the roles in the GE_APP_ADMIN role set, ABAC must be applied
        # TODO: Implement ABAC rights retrieval when policies are available

        # TODO: Check if user has WRITE access to all created in data collections
        # TODO: For each sample in the batch, verify user has WRITE access to sample.created_in_data_collection_id
        is_authorized = True
        if not is_authorized:
            data_collection_id = NULL_ID
            sample_id = NULL_ID
            raise exc.UnauthorizedAuthError(
                f"User {cmd.user.email if cmd.user else 'anonymous'} lacks WRITE access to data collection {data_collection_id} for sample {sample_id if sample_id else 'new sample'}"
            )

    def verify_batch(
        self,
        cmd: command.UploadSamplesCommand,
        batch_result: model.SampleBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Check existence of parent model and child models.
        """
        success = True

        success &= self.verify_parents_external_identifiers(cmd, batch_result, uow)
        success &= self.verify_parents(cmd, batch_result, uow)
        # Verify existence and consistency of child models as needed
        success &= _verify_sample_children(self, cmd, batch_result, uow)
        # Verify reference data
        success &= _verify_sample_refdata(self, cmd, batch_result, uow)

        return success

    def upsert_batch(
        self,
        cmd: command.UploadSamplesCommand,
        batch_result: model.SampleBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Create or update the sample and any reference data.
        """
        success = True

        # Add any new reference data
        success &= _create_sample_refdata(self, cmd, batch_result, uow)
        # Upsert sample data
        success &= self.create_parents(cmd, batch_result, uow)
        success &= self.update_parents(cmd, batch_result, uow)
        # Upsert child models
        success &= self.create_children(cmd, batch_result, uow)
        success &= self.update_children(cmd, batch_result, uow)
        # Create external identifiers
        success &= self.create_external_identifiers(cmd, batch_result, uow)

        return success


def seq_service_upload_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> model.SampleBatchUploadResult:
    """
    See command.UploadSamplesCommand for details.
    """
    sample_batch_uploader = SampleBatchUploader(self)
    batch_result: model.SampleBatchUploadResult = sample_batch_uploader.upload_batch(
        cmd
    )
    return batch_result
