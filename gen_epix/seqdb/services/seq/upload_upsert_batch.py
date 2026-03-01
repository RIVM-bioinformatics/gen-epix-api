from gen_epix.commondb.services import BatchUploader
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, model


def _create_sample_refdata(
    self: BatchUploader,
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
        created_alleles = self.service.repository.crud(
            uow,
            user_id,
            model.Allele,
            alleles,
            None,
            operation=CrudOperation.CREATE_SOME,
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
    allele_profiles: list[model.AlleleProfileForUpload] = []
    snp_profiles: list[model.SnpProfileForUpload] = []
    mlva_profiles: list[model.MlvaProfileForUpload] = []
    kmer_profiles: list[model.KmerProfileForUpload] = []

    # Collect profiles with their assigned IDs from the upload result.
    # batch_result.samples is positionally aligned with cmd.sample_batch.samples.
    for sample_for_upload, sample_result in zip(
        cmd.sample_batch.samples, batch_result.samples
    ):
        for allele_profile, allele_profile_result in zip(
            sample_for_upload.allele_profiles or [], sample_result.allele_profiles or []
        ):
            allele_profiles.append(
                allele_profile.model_copy(update={"id": allele_profile_result.id})
            )
        for snp_profile, snp_profile_result in zip(
            sample_for_upload.snp_profiles or [], sample_result.snp_profiles or []
        ):
            snp_profiles.append(
                snp_profile.model_copy(update={"id": snp_profile_result.id})  # type: ignore[arg-type]
            )
        for mlva_profile, mlva_profile_result in zip(
            sample_for_upload.mlva_profiles or [], sample_result.mlva_profiles or []
        ):
            mlva_profiles.append(
                mlva_profile.model_copy(update={"id": mlva_profile_result.id})  # type: ignore[arg-type]
            )
        for kmer_profile, kmer_profile_result in zip(
            sample_for_upload.kmer_profiles or [], sample_result.kmer_profiles or []
        ):
            kmer_profiles.append(
                kmer_profile.model_copy(update={"id": kmer_profile_result.id})  # type: ignore[arg-type]
            )

    calculate_seq_distance_result: list[model.CalculateSeqDistancesResult] = (
        self.service.app.handle(
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=user,
                # TODO: the models current being passed here are ForUpload models rather than regular models. They should be converted first.
                allele_profiles=allele_profiles if allele_profiles else None,  # type: ignore[arg-type]
                snp_profiles=snp_profiles if snp_profiles else None,  # type: ignore[arg-type]
                mlva_profiles=mlva_profiles if mlva_profiles else None,  # type: ignore[arg-type]
                kmer_profiles=kmer_profiles if kmer_profiles else None,  # type: ignore[arg-type]
            )
        )
    )

    batch_result.seq_distances = calculate_seq_distance_result

    return success
