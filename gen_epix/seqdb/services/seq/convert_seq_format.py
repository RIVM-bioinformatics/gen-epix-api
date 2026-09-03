"""Implement stored sequence representation conversion."""

from uuid import UUID

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.model.seq.base import encode_gzip_base64
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_convert_seq_format(
    self: BaseSeqService, cmd: command.ConvertSeqFormatCommand
) -> list[UUID]:
    """Convert all contigs in the requested sequences to a new representation."""
    user_id = cmd.user.id if cmd.user else None

    with self.repository.uow() as uow:
        seqs: list[model.Seq] = self.repository.crud(
            uow,
            user_id,
            model.Seq,
            CrudOperation.READ_SOME,
            obj_ids=cmd.seq_ids,
        )

        # validate all contigs before performing any conversion
        for seq in seqs:
            for contig in seq.contigs:
                if contig.seq_format != cmd.from_format:
                    raise ValueError(
                        f"Sequence {seq.id} contains a contig in "
                        f"{contig.seq_format.value} format, expected "
                        f"{cmd.from_format.value}"
                    )

                nucleotide_seq = contig.get_nucleotide_seq()
                if cmd.to_format in model.enum.SeqFormatSet.GZB64.value:
                    nucleotide_seq = encode_gzip_base64(nucleotide_seq)

                # modify the contig in place instead of creating a new contig object
                contig.seq = nucleotide_seq
                contig.seq_format = cmd.to_format

        updated_ids: list[UUID] = self.repository.crud(
            uow,
            user_id,
            model.Seq,
            CrudOperation.UPDATE_SOME,
            objs=seqs,
            return_id=True,
        )
    return updated_ids
