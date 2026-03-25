import abc
from collections.abc import Iterable
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.fastapp import BaseService


class BaseSeqdbService(BaseService):
    SERVICE_TYPE = ServiceType.SEQDB

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(
            command.RetrievePhylogeneticTreeBySequencesCommand,
            self.retrieve_phylogenetic_tree,
        )
        f(
            command.RetrieveGeneticSequenceFastaByIdCommand,
            self.retrieve_genetic_sequence_fasta_by_id,
        )
        f(seqdb_command.UploadSamplesCommand, self.upload_samples)
        f(seqdb_command.CreateFileCommand, self.create_file)
        f(seqdb_command.ReadSetCrudCommand, self.crud)
        f(seqdb_command.FileCrudCommand, self.crud)
        f(seqdb_command.SeqCrudCommand, self.crud)
        f(seqdb_command.RetrieveSimilarProfilesCommand, self.retrieve_similar_profiles)

    @abc.abstractmethod
    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeBySequencesCommand
    ) -> model.PhylogeneticTree | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_genetic_sequence_fasta_by_id(
        self,
        cmd: command.RetrieveGeneticSequenceFastaByIdCommand,
    ) -> Iterable[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_samples(
        self,
        cmd: seqdb_command.UploadSamplesCommand,
    ) -> seqdb_model.SampleBatchUploadResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_file(
        self,
        cmd: seqdb_command.CreateFileCommand,
    ) -> UUID:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_similar_profiles(
        self,
        cmd: seqdb_command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        raise NotImplementedError()
