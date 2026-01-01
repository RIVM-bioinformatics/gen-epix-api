from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.commondb.services.upload import (
    _upsert_batch_create_children,
    _upsert_batch_create_objects,
    _upsert_batch_update_children,
    _upsert_batch_update_objects,
)
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def _upsert_batch_create_sample_refdata(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Upsert reference data as part of creating or updating the sample data.
    """
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Add any new alleles
    alleles = cmd.sample_batch.alleles
    if alleles:
        created_alleles = self.repository.crud(
            uow,
            user_id,
            model.Allele,
            alleles,
            None,
            operation=CrudOperation.CREATE_SOME,
        )
    return success


def _upsert_batch_create_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Upsert sample data as part of creating or updating the sample data.
    """
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples

    # Determine which samples need to be created
    to_create_sample_result_pairs = [
        (x, y)
        for x, y in zip(samples, sample_results)
        if x.id is None and y.status == UploadStatus.PENDING
    ]
    if not to_create_sample_result_pairs:
        return True

    # Create samples
    _upsert_batch_create_objects(
        self,
        uow,
        user_id,
        model.Sample,
        to_create_sample_result_pairs,  # type:ignore[arg-type]
    )

    return True


def _upsert_batch_update_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Update existing sample data as part of updating the sample data.
    This function only updates samples that already exist; it does not create new samples.
    It updates the props dictionary of each sample based on the provided updates,
    and adjusts the corresponding SampleUploadResult accordingly.
    """
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Determine which samples need to be updated
    to_update_sample_result_pairs = [
        (x, y)
        for x, y in zip(samples, sample_results)
        if x.id is not None and y.status == UploadStatus.PENDING
    ]
    if not to_update_sample_result_pairs:
        return success

    return _upsert_batch_update_objects(
        self,
        uow,
        user_id,
        model.Sample,
        model.STORED_MODEL_FIELD_PROPS[model.Sample],
        to_update_sample_result_pairs,  # type:ignore[arg-type]
    )

    return success


def _upsert_batch_create_sample_children(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Create child models as part of creating or updating the sample data.
    """
    return _upsert_batch_create_children(
        self,
        cmd,
        uow,
        model.SampleForUpload,
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )


def _upsert_batch_update_sample_children(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Update child models as part of creating or updating the sample data.
    """
    return _upsert_batch_update_children(
        self,
        cmd,
        uow,
        model.STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
        model.SampleForUpload,
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )
