from typing import Any

from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService
from gen_epix.seqdb.services.seq.upload_upsert_batch import (
    _upsert_batch_create_associated_data,
    _upsert_batch_create_samples,
    _upsert_batch_refdata,
    _upsert_batch_update_associated_data,
    _upsert_batch_update_samples,
)
from gen_epix.seqdb.services.seq.upload_verify_batch import (
    _verify_batch_associated_data,
    _verify_batch_external_ids,
    _verify_batch_refdata,
    _verify_batch_sample_existence,
)


def seq_service_upload_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> model.SampleBatchUploadResult:
    """
    See command.UploadSamplesCommand for details.
    """
    #  Check user rights
    _verify_user_rights(self, cmd)

    # Initialize the upload result
    retval = _init_retval(cmd)
    retval.add_info(
        code="f1e2d3c4",
        message="Upload started",
    )

    with self.repository.uow() as uow:
        # Verify batch
        retval.add_info(
            code="8b4c2f91",
            message="Verification started",
        )
        success = _verify_batch(self, cmd, retval, uow)
        retval.add_info(
            code="a3f7e9d2",
            message="Verification ended",
        )
        if not success:
            # Do not proceed with upsert due to errors
            retval.add_info(
                code="d6e5c3b4",
                message="Verification found errors, upsert will not proceed",
            )
            return retval

        # Upsert the batch data
        retval.add_info(
            code="c1a2b3d4",
            message="Upsert started",
        )
        success = _upsert_batch(self, cmd, retval, uow)
        retval.add_info(
            code="e4f5a6b7",
            message="Upsert ended",
        )
        if not success:
            # Rollback due to errors, but do not raise an exception since those will be reported in retval
            retval.add_info(
                code="f8e7d6c5",
                message="Upsert found errors, rolling back changes",
            )
            uow.rollback()
            retval.add_info(
                code="b2c3d4e5",
                message="Upsert found errors, changes have been rolled back",
            )
    retval.add_info(
        code="a1b2c3d4",
        message="Upload ended",
    )

    # TODO: update any distances

    return retval


def _verify_user_rights(
    self: BaseSeqService,
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
    data_collection_ids = {
        x.created_in_data_collection_id for x in cmd.sample_batch.samples
    }
    is_authorized = True
    if not is_authorized:
        raise exc.UnauthorizedAuthError(
            f"User {cmd.user.email if cmd.user else 'anonymous'} lacks WRITE access to data collection {data_collection_id} for sample {sample.id if sample.id else 'new sample'}"
        )


def _init_retval(
    cmd: command.UploadSamplesCommand,
) -> model.SampleBatchUploadResult:
    """
    Initialize the upload result that will be the return value.
    """
    # Initialize some
    sample_results = []

    def _create_sub_result(obj: Any | None) -> UploadResult | None:
        if obj is None:
            return None
        return UploadResult(id=getattr(obj, "id", None))

    def _create_sub_results(objs: list | None) -> list[UploadResult] | None:
        if objs is None:
            return None
        return [UploadResult(id=getattr(x, "id", None)) for x in objs]

    # Create a result for each sample with subresults for associated data
    for sample in cmd.sample_batch.samples:
        sample_result = model.SampleUploadResult(
            sample=_create_sub_result(sample.props),
            external_ids=_create_sub_results(sample.external_ids),
            read_sets=_create_sub_results(sample.read_sets),
            seqs=_create_sub_results(sample.seqs),
            seq_taxonomies=_create_sub_results(sample.seq_taxonomies),
            seq_classifications=_create_sub_results(sample.seq_classifications),
            locus_profiles=_create_sub_results(sample.locus_profiles),
            allele_profiles=_create_sub_results(sample.allele_profiles),
            snp_profiles=_create_sub_results(sample.snp_profiles),
            mlva_profiles=_create_sub_results(sample.mlva_profiles),
            kmer_profiles=_create_sub_results(sample.kmer_profiles),
            seq_distances=_create_sub_results(sample.seq_distances),
            pcr_measurements=_create_sub_results(sample.pcr_measurements),
            ast_measurements=_create_sub_results(sample.ast_measurements),
        )
        sample_results.append(sample_result)

    return model.SampleBatchUploadResult(
        batch_id=cmd.sample_batch.id,
        samples=sample_results,
    )


def _verify_batch(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Check existence of samples and associated data.
    """
    success = True

    # Verify existence of samples by ID
    success &= _verify_batch_sample_existence(self, cmd, retval, uow)
    # Verify existence and consistency of external IDs
    success &= _verify_batch_external_ids(self, cmd, retval, uow)
    # Verify existence and consistency of associated data as needed
    success &= _verify_batch_associated_data(self, cmd, retval, uow)
    # Verify reference data
    success &= _verify_batch_refdata(self, cmd, retval, uow)

    return success


def _upsert_batch(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Create or update the sample and any reference data.
    """
    success = True

    # Add any new reference data
    success &= _upsert_batch_refdata(self, cmd, retval, uow)
    # Upsert sample data
    success &= _upsert_batch_create_samples(self, cmd, retval, uow)
    success &= _upsert_batch_update_samples(self, cmd, retval, uow)
    # Upsert associated data
    success &= _upsert_batch_create_associated_data(self, cmd, retval, uow)
    success &= _upsert_batch_update_associated_data(self, cmd, retval, uow)

    return success
