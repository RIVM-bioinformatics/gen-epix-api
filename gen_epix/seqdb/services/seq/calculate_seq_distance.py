from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_calculate_seq_distances_for_new_profiles(
    self: BaseSeqService,
    cmd: command.CalculateSeqDistancesForNewProfilesCommand,
) -> list[model.CalculateSeqDistancesResult]:
    """
    TODO: Implement the actual distance calculation logic here.
    """

    user_id = cmd.user.id if cmd.user else None
    allele_profiles = list(cmd.allele_profiles or [])
    snp_profiles = list(cmd.snp_profiles or [])
    mlva_profiles = list(cmd.mlva_profiles or [])
    kmer_profiles = list(cmd.kmer_profiles or [])

    if kmer_profiles:
        raise NotImplementedError(
            "Seq distance calculation for k-mer profiles is not yet implemented"
        )

    raise NotImplementedError()
