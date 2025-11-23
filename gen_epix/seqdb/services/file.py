import base64
import binascii
import re
from collections.abc import Iterable
from io import StringIO
from uuid import UUID

from Bio import SeqIO

from gen_epix.fastapp import CrudOperationSet
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.service.file import BaseFileService


class FileService(BaseFileService):

    VALID_NUCLEOTIDES_PATTERN = re.compile(r"^[ACGTURYSWKMBDHVN\-.]+$", re.IGNORECASE)

    def crud(  # type: ignore
        self, cmd: command.CrudCommand
    ) -> list[model.Model] | model.Model | list[UUID] | UUID:
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
            raw_content = getattr(file_obj, "content", None)
            if (
                raw_content is None
                or (
                    isinstance(raw_content, (bytes, bytearray))
                    and len(raw_content) == 0
                )
                or (isinstance(raw_content, str) and raw_content.strip() == "")
            ):
                raise exc.InvalidArgumentsError("File content is empty")

            if isinstance(raw_content, str):
                content_bytes: bytes = raw_content.encode("utf-8")
            else:
                content_bytes = bytes(raw_content)

            # If the file doesn't start with '>' or '@' try base64-decoding it
            # (many clients embed binary files as base64 inside JSON).
            header = content_bytes.lstrip()[:1]
            if header not in (b">", b"@"):
                try:
                    decoded = base64.b64decode(content_bytes, validate=True)
                    if not decoded:
                        raise exc.InvalidArgumentsError(
                            "File content is empty after base64 decoding"
                        )
                    # replace content_bytes with decoded bytes if it looks like a FASTA/FASTQ
                    header_decoded = decoded.lstrip()[:1]
                    if header_decoded in (b">", b"@"):
                        content_bytes = decoded
                        header = header_decoded
                    else:
                        raise exc.InvalidArgumentsError(
                            "Unsupported file format: expected FASTA (lines start with >) or FASTQ (records start with @)"
                        )
                except binascii.Error as e:
                    raise exc.InvalidArgumentsError(
                        "Unsupported file format: expected FASTA (lines start with >) or FASTQ (records start with @), or a Base64-encoded representation of those."
                    ) from e

            # Determine sequence format from header byte
            match header:
                case b">":
                    sequence_format: enum.FileFormat = enum.FileFormat.FASTA
                case b"@":
                    sequence_format = enum.FileFormat.FASTQ
                case _:
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
                sequence_records: Iterable = SeqIO.parse(text_stream, sequence_format.value.lower())  # type: ignore[no-untyped-call]
            except Exception as e:
                raise exc.InvalidArgumentsError(
                    f"Invalid {sequence_format.value} content: {e}"
                ) from e

            found_records: bool = False
            for record in sequence_records:
                found_records = True
                if sequence_format == enum.FileFormat.FASTQ:
                    phred_quality_scores: list[int] | None = (
                        record.letter_annotations.get("phred_quality")
                    )
                    if phred_quality_scores is None or len(phred_quality_scores) != len(
                        record.seq
                    ):
                        raise exc.InvalidArgumentsError(
                            "Invalid FASTQ: quality scores missing or length mismatch with sequence"
                        )
                sequence_string: str = str(record.seq)  # type: ignore[assignment]
                if not self.VALID_NUCLEOTIDES_PATTERN.match(sequence_string):
                    raise exc.InvalidArgumentsError(
                        f"Invalid {sequence_format.value}: sequence contains invalid characters"
                    )
                if sequence_format == enum.FileFormat.FASTA:
                    # SequnceFormat.FASTA doesn't need more than one record to validate
                    break

            if not found_records:
                raise exc.InvalidArgumentsError(
                    f"No sequence records found in {sequence_format.value} file"
                )
