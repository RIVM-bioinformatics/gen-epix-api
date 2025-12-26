from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def seq_service_upload_samplea(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> model.SampleBatchUploadResult:
    enum.RoleSet
    raise NotImplementedError()
