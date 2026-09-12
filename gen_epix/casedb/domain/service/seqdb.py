"""Define the Casedb-facing Seqdb service contract and command dispatch."""

import abc
from collections.abc import Iterable
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.fastapp import BaseService


class BaseSeqdbService(BaseService):
    """Encapsulates sequence command dispatch used through Casedb.

    The service combines default Seqdb CRUD handling with Casedb-facing tree,
    similarity, upload, file, and FASTA operations. Concrete implementations
    may delegate those operations to a remote Seqdb service.
    """

    SERVICE_TYPE = ServiceType.SEQDB

    def register_handlers(self) -> None:
        """Register Casedb-facing sequence and default CRUD handlers.

        This mutates the application dispatch table during service
        initialization.
        """
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(
            command.RetrievePhylogeneticTreeByProfilesCommand,
            self.retrieve_phylogenetic_tree,
        )
        f(
            command.RetrieveGeneticSequenceFastaByIdCommand,
            self.retrieve_genetic_sequence_fasta_by_id,
        )
        f(seqdb_command.UploadSamplesCommand, self.upload_samples)
        f(seqdb_command.CreateFileCommand, self.create_file)
        f(seqdb_command.ProtocolCrudCommand, self.crud)
        f(seqdb_command.ReadSetCrudCommand, self.crud)
        f(seqdb_command.FileCrudCommand, self.crud)
        f(seqdb_command.SeqCrudCommand, self.crud)
        f(seqdb_command.RetrieveSimilarProfilesCommand, self.retrieve_similar_profiles)

    @abc.abstractmethod
    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeByProfilesCommand
    ) -> model.PhylogeneticTree | None:
        """Retrieve a phylogenetic tree for specified profiles.

        Args:
            cmd: Tree command containing profile identifiers and parameters.

        Returns:
            The generated tree, or ``None`` when no tree can be produced.

        Raises:
            NotImplementedError: Always, until a concrete service implements
                the operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_genetic_sequence_fasta_by_id(
        self,
        cmd: command.RetrieveGeneticSequenceFastaByIdCommand,
    ) -> Iterable[str]:
        """Retrieve genetic sequence data in FASTA format by identifier.

        Args:
            cmd: FASTA retrieval command containing sequence identifiers.

        Returns:
            An iterable of FASTA-formatted text fragments.

        Raises:
            NotImplementedError: Always, until a concrete service implements
                the operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_samples(
        self,
        cmd: seqdb_command.UploadSamplesCommand,
    ) -> seqdb_model.SampleBatchUploadResult:
        """Upload a batch of sequence samples.

        Implementations may persist samples and related sequence objects.

        Args:
            cmd: Upload command containing the sample batch.

        Returns:
            The per-sample upload result.

        Raises:
            NotImplementedError: Always, until a concrete service implements
                the upload.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def create_file(
        self,
        cmd: seqdb_command.CreateFileCommand,
    ) -> UUID:
        """Create a sequence file and return its identifier.

        Implementations persist file metadata or delegate creation to Seqdb.

        Args:
            cmd: File-creation command to execute.

        Returns:
            The identifier of the created file.

        Raises:
            NotImplementedError: Always, until a concrete service implements
                file creation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_similar_profiles(
        self,
        cmd: seqdb_command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        """Retrieve profiles similar to a specified profile.

        Args:
            cmd: Similarity command containing the reference profile and
                matching parameters.

        Returns:
            Identifiers of matching profiles.

        Raises:
            NotImplementedError: Always, until a concrete service implements
                the query.
        """
        raise NotImplementedError()
