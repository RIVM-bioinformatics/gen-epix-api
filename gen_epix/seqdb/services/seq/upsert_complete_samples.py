from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def seq_service_upsert_complete_samples(
    self: BaseSeqService,
    cmd: command.UpsertCompleteSamplesCommand,
) -> list[model.CompleteSample]:

    raise NotImplementedError()
