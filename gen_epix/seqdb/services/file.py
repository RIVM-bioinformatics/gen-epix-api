from collections.abc import Iterable
from io import StringIO
from uuid import UUID

from Bio import SeqIO

from gen_epix.fastapp import CrudOperationSet
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.service.file import BaseFileService


class FileService(BaseFileService):

    def crud(  # type: ignore
        self, cmd: command.CrudCommand
    ) -> list[model.Model] | model.Model | list[UUID] | UUID:
        """
        Override the base crud method to side effects and cascade delete
        where necessary
        """
        if isinstance(cmd, command.FileCrudCommand):
            self.validate_file(cmd)

        return super().crud(cmd)

    def validate_file(
        self,
        cmd: command.FileCrudCommand,
    ) -> None:
        is_create = cmd.operation in CrudOperationSet.CREATE.value
        if is_create:
            file_obj = cmd.get_objs()[0]
            content_bytes: bytes = getattr(file_obj, "content", None)
            if not content_bytes:
                raise exc.InvalidArgumentsError("File content is empty")

            header_byte = content_bytes.lstrip()[:1]
            if not header_byte:
                raise exc.InvalidArgumentsError("File content is empty")
            if header_byte == b">":
                sequence_format: enum.SequenceFormat = enum.SequenceFormat.FASTA
            elif header_byte == b"@":
                sequence_format = enum.SequenceFormat.FASTQ
            else:
                raise exc.InvalidArgumentsError(
                    "Unsupported file format: expected FASTA (lines start with >) or FASTQ (records start with @)"
                )
            try:
                text_stream: StringIO = StringIO(content_bytes.decode("utf-8"))
            except Exception as e:
                raise exc.InvalidArgumentsError(
                    "Unable to decode file content as UTF-8"
                ) from e
            try:
                sequence_records: Iterable = SeqIO.parse(text_stream, sequence_format.value.lower())  # type: ignore
            except Exception as e:
                raise exc.InvalidArgumentsError(
                    f"Invalid {sequence_format.value} content: {e}"
                ) from e

            if not sequence_records:
                raise exc.InvalidArgumentsError(
                    f"No records found in {sequence_format.value} file"
                )

            for record in sequence_records:
                if sequence_format == enum.SequenceFormat.FASTQ:
                    phred_quality_scores: list[int] | None = record.letter_annotations.get("phred_quality")  # type: ignore[attr-defined]
                    if phred_quality_scores is None or len(phred_quality_scores) != len(record.seq):  # type: ignore[arg-type]
                        raise exc.InvalidArgumentsError(
                            "Invalid FASTQ: quality scores missing or length mismatch with sequence"
                        )
                # TODO: Add nucleotide validation here?
                # if not all(nucl in "ACGTNacgtn-.*" for nucl in record.seq):
                #     raise exc.InvalidArgumentsError(
                #         "Invalid nucleotide characters found in sequence"
                #     )
