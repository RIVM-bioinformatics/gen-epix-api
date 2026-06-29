import gzip
from collections.abc import Iterable
from io import BytesIO, StringIO
from uuid import UUID

from Bio import SeqIO

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.service.file import BaseFileService
from gen_epix.seqdb.services.seq.crud_file import file_service_crud_file


class FileService(BaseFileService):

    def create_file(
        self,
        cmd: command.CreateFileCommand,
    ) -> UUID:
        # Validate file content based on format
        if cmd.format == enum.FileFormat.FASTA:
            self._verify_fasta_content(cmd.file.content, cmd.compression)
        elif cmd.format == enum.FileFormat.FASTQ:
            self._verify_fastq_content(cmd.file.content, cmd.compression)
        else:
            raise exc.InvalidArgumentsError(
                "76692bc2", f"Unsupported file format: {cmd.format}"
            )
        # Add file identifier
        file = cmd.file
        file.id: UUID = self.generate_id()  # type: ignore[assignment]
        # Store the file
        assert cmd.user is not None and cmd.user.id is not None
        with self.repository.uow() as uow:
            file_id: UUID = self.repository.crud(
                uow,
                cmd.user.id,
                model.File,
                operation=CrudOperation.CREATE_ONE,
                objs=cmd.file,
                return_id=True,
            )
        return file_id

    def _get_file_text_stream(
        self, content: bytes, compression: enum.FileCompression
    ) -> StringIO:
        try:
            if compression == enum.FileCompression.NONE:
                text_stream = StringIO(content.decode("utf-8"))
            elif compression == enum.FileCompression.GZIP:
                with gzip.GzipFile(fileobj=BytesIO(content)) as gz:
                    text_stream = StringIO(gz.read().decode("utf-8"))
        except Exception as e:
            raise exc.InvalidArgumentsError(
                "ce8d8ba6", "Unable to decode file content as UTF-8"
            ) from e
        return text_stream

    def _verify_fasta_content(
        self, content: bytes, compression: enum.FileCompression
    ) -> None:
        text_stream: StringIO = self._get_file_text_stream(content, compression)
        try:
            seq_records: Iterable = SeqIO.parse(text_stream, "fasta")  # type: ignore[no-untyped-call]
        except Exception as e:
            raise exc.InvalidArgumentsError(
                "10001d1e", f"Invalid FASTA content: {e}"
            ) from e

        found_records: bool = False
        for seq_record in seq_records:
            found_records = True
            seq = str(seq_record.seq)
            invalid_chars = (
                set(seq.lower()) - enum.SeqAlphabet.DNA_INCL_AMBIGUOUS_AND_GAP.value
            )
            if invalid_chars:
                raise exc.InvalidArgumentsError(
                    "104a177c",
                    f"Invalid FASTA: sequence contains at least the following invalid characters: {', '.join(sorted(invalid_chars))}",
                )
        if not found_records:
            raise exc.InvalidArgumentsError(
                "95f24d58", "No sequence records found in FASTA file"
            )

    def _verify_fastq_content(
        self, content: bytes, compression: enum.FileCompression
    ) -> None:
        text_stream: StringIO = self._get_file_text_stream(content, compression)
        try:
            seq_records: Iterable = SeqIO.parse(text_stream, "fastq")  # type: ignore[no-untyped-call]
        except Exception as e:
            raise exc.InvalidArgumentsError(
                "aba687d6", f"Invalid FASTQ content: {e}"
            ) from e

        found_records: bool = False
        for seq_record in seq_records:
            found_records = True
            phred_quality_scores: list[int] | None = seq_record.letter_annotations.get(
                "phred_quality"
            )
            if phred_quality_scores is None or len(phred_quality_scores) != len(
                seq_record.seq
            ):
                raise exc.InvalidArgumentsError(
                    "12a07187",
                    "Invalid FASTQ: quality scores missing or length mismatch with sequence",
                )
            seq = str(seq_record.seq)
            invalid_chars = (
                set(seq.lower()) - enum.SeqAlphabet.DNA_INCL_AMBIGUOUS_AND_GAP.value
            )
            if invalid_chars:
                raise exc.InvalidArgumentsError(
                    "1018ec3c",
                    f"Invalid FASTQ: sequence contains at least the following invalid characters: {', '.join(sorted(invalid_chars))}",
                )
        if not found_records:
            raise exc.InvalidArgumentsError(
                "d2110d13", "No sequence records found in FASTQ file"
            )

    def crud_file(
        self,
        cmd: command.FileCrudCommand,
    ) -> model.File | list[model.File] | UUID | list[UUID] | bool | list[bool] | None:
        return file_service_crud_file(self, cmd)
