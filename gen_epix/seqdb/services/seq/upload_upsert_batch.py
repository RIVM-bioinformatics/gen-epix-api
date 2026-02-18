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
    """
    success = True
    user = cmd.user if cmd.user else None
    allele_profiles: list[model.AlleleProfileForUpload] = []
    snp_profiles: list[model.SnpProfileForUpload] = []
    mlva_profiles: list[model.MlvaProfileForUpload] = []

    # Collect all profiles from all samples in the batch
    for sample in cmd.sample_batch.samples:
        if sample.allele_profiles:
            allele_profiles.extend(sample.allele_profiles)
        if sample.snp_profiles:
            snp_profiles.extend(sample.snp_profiles)
        if sample.mlva_profiles:
            mlva_profiles.extend(sample.mlva_profiles)

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
