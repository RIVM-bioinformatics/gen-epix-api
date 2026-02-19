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
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Update distances for any profiles that are affected by the sample batch upload.

    The ForUpload objects in cmd do not carry the IDs assigned during storage.
    Those IDs are available in the UploadResult entries of retval, which are in
    the same positional order as the upload objects.  We zip the two to patch the
    correct ID onto each profile before dispatching the distance command.
    """
    success = True
    user = cmd.user if cmd.user else None
    allele_profiles: list[model.AlleleProfileForUpload] = []
    snp_profiles: list[model.SnpProfileForUpload] = []
    mlva_profiles: list[model.MlvaProfileForUpload] = []

    # Collect profiles with their assigned IDs from the upload result.
    # retval.samples is positionally aligned with cmd.sample_batch.samples.
    for sample_input, sample_result in zip(cmd.sample_batch.samples, retval.samples):
        if sample_input.allele_profiles and sample_result.allele_profiles:
            for profile, profile_result in zip(
                sample_input.allele_profiles, sample_result.allele_profiles
            ):
                allele_profiles.append(
                    profile.model_copy(update={"id": profile_result.id})
                )
        if sample_input.snp_profiles and sample_result.snp_profiles:
            for profile, profile_result in zip(
                sample_input.snp_profiles, sample_result.snp_profiles
            ):
                snp_profiles.append(
                    profile.model_copy(update={"id": profile_result.id})  # type: ignore[arg-type]
                )
        if sample_input.mlva_profiles and sample_result.mlva_profiles:
            for profile, profile_result in zip(
                sample_input.mlva_profiles, sample_result.mlva_profiles
            ):
                mlva_profiles.append(
                    profile.model_copy(update={"id": profile_result.id})  # type: ignore[arg-type]
                )

    calculate_seq_distance_result: list[model.CalculateSeqDistancesResult] = (
        self.service.app.handle(
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=user,
                allele_profiles=allele_profiles if allele_profiles else None,  # type: ignore[arg-type]
                snp_profiles=snp_profiles if snp_profiles else None,  # type: ignore[arg-type]
                mlva_profiles=mlva_profiles if mlva_profiles else None,  # type: ignore[arg-type]
            )
        )
    )

    retval.seq_distances = calculate_seq_distance_result

    return success
