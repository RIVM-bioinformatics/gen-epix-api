from uuid import UUID

from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def seq_service_upsert_complete_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> list[UUID]:

    # TODO:
    # 1 If any alleles are provided in the command, create them first.
    # 2 Determine if each sample already exist based on their internal identifier or list of external identifiers, and create as needed:
    #    1 If CompleteSample.id provided, then the sample should exist.
    #       1 If not existing, raise error.
    #       2 If any external identifiers provided:
    #           1 Match against SampleIdentifier using READ_ALL plus filter (identifier IN identifiers AND identifier_issuer_id in identifier_issuer_ids)
    #           2 Check if any matches are for the same sample_id. If not raise error.
    #           3 Create the remaining SampleIdentifiers
    #    2 Else:
    #       1 If no external identifiers provided, raise error.
    #       2 Match against SampleIdentifier using READ_ALL plus filter (identifier IN identifiers AND identifier_issuer_id in identifier_issuer_ids)
    #       3 If any matches found they must be for the same sample_id, otherwise raise error. Create the remaining SampleIdentifiers.
    #       4 If no matches found, create new Sample and SampleIdentifiers.
    # 3 Upsert the CompleteSample data (Sample plus related data).
    #    TO DO

    raise NotImplementedError()
