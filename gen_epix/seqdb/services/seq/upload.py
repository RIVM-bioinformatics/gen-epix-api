from uuid import UUID

from gen_epix.seqdb.domain import command, enum
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def seq_service_upload_samplea(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> list[UUID]:
    enum.RoleSet
    raise NotImplementedError()
