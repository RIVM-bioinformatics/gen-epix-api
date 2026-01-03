from gen_epix.commondb.domain.enum import IdentifierType
from gen_epix.commondb.services.upload import (
    create_children,
    create_external_identifiers,
    create_parents,
    update_children,
    update_parents,
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
    """Create samples."""
    return create_parents(
        self,
        cmd,
        uow,
        model.Sample,
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )


def _upsert_batch_update_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """Update samples."""
    return update_parents(
        self,
        cmd,
        uow,
        model.STORED_MODEL_FIELD_PROPS[model.Sample],
        model.Sample,
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )


def _upsert_batch_create_sample_children(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Create child models as part of creating or updating the sample data.
    """
    return create_children(
        self,
        cmd,
        uow,
        model.SampleForUpload,
        "sample_id",
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
    return update_children(
        self,
        cmd,
        uow,
        model.STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
        model.SampleForUpload,
        "sample_id",
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )


def _upsert_batch_create_sample_external_identifiers(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """Create external identifiers for samples."""
    return create_external_identifiers(
        self,
        cmd,
        IdentifierType.SAMPLE,
        cmd.sample_batch.samples,  # type: ignore[arg-type]
        retval.samples,  # type: ignore[arg-type]
    )
