from gen_epix.commondb.domain.enum import EtlStatus, UploadAction
from gen_epix.commondb.services import BatchUploader
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.exc import ConcurrentModificationError
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, model


def _create_sample_refdata(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Upsert reference data as part of creating or updating the sample data.
    """
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Add any new alleles. Alleles are content-addressed and immutable, so
    # UPSERT_SOME is safe for both UPDATE and SKIP (re-writing identical data is
    # a no-op). Only ERROR mode keeps the strict CREATE_SOME that rejects duplicates.
    alleles = cmd.sample_batch.alleles
    if alleles:
        allele_operation = (
            CrudOperation.CREATE_SOME
            if cmd.on_exists == UploadAction.ERROR
            else CrudOperation.UPSERT_SOME
        )
        self.service.repository.crud(
            uow,
            user_id,
            model.Allele,
            allele_operation,
            objs=alleles,
        )
    return success


def _update_profile_distances(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Update distances for any profiles that are affected by the sample batch upload.

    The ForUpload objects in cmd do not carry the IDs assigned during storage.
    Those IDs are available in the UploadResult entries of batch_result, which are in
    the same positional order as the upload objects.  We zip the two to patch the
    correct ID onto each profile before dispatching the distance command.
    """
    success = True
    user = cmd.user if cmd.user else None
    seq_profiles: list[model.SeqProfileForUpload] = []

    # Collect only profiles that were actually written (created or updated).
    # batch_result.samples is positionally aligned with cmd.sample_batch.samples.
    for sample_for_upload, sample_result in zip(
        cmd.sample_batch.samples, batch_result.samples
    ):
        for seq_profile, seq_profile_result in zip(
            sample_for_upload.seq_profiles or [], sample_result.seq_profiles or []
        ):
            if seq_profile_result.status not in (EtlStatus.CREATED, EtlStatus.UPDATED):
                continue
            seq_profiles.append(
                seq_profile.model_copy(update={"id": seq_profile_result.id})
            )

    if not seq_profiles:
        return success

    try:
        calculate_seq_distance_result: list[model.CalculateSeqDistancesResult] = (
            self.service.app.handle(
                command.CalculateSeqDistancesForNewProfilesCommand(
                    user=user,
                    # TODO: the models current being passed here are ForUpload models rather than regular models. They should be converted first.
                    seq_profiles=seq_profiles,
                    seq_distance_last_modified_at=(cmd.seq_distance_last_modified_at),
                )
            )
        )
        batch_result.seq_distances = calculate_seq_distance_result
    except ConcurrentModificationError as e:
        batch_result.add_warning(
            "b3e1f49a",
            f"Seq distance calculation skipped due to concurrent modification: {e}. "
            "Re-run UpdateSeqDistancesCommand to recalculate.",
        )

    return success
