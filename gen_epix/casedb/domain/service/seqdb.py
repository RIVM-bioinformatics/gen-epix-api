import abc
from typing import Iterable
from uuid import UUID

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
        f(command.RetrieveGeneticSequenceByIdCommand, self.retrieve_genetic_sequences)
        f(
            command.RetrieveGeneticSequenceFastaByIdCommand,
            self.retrieve_genetic_sequence_fasta_by_id,
        )
        f(command.ReadSetCrudCommand, self.create_read_set)
        # f(command.RetrieveAlleleProfileCommand, self.retrieve_allele_profile)

    @abc.abstractmethod
    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeBySequencesCommand
    ) -> model.PhylogeneticTree | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_genetic_sequences(
        self,
        cmd: command.RetrieveGeneticSequenceByIdCommand,
    ) -> list[model.GeneticSequence]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_genetic_sequence_fasta_by_id(
        self,
        cmd: command.RetrieveGeneticSequenceFastaByIdCommand,
    ) -> Iterable[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_read_set(self, cmd: command.ReadSetCrudCommand) -> list[model.ReadSet]:
        raise NotImplementedError()


    # @abc.abstractmethod
    # def retrieve_allele_profile(
    #     self,
    #     cmd: command.RetrieveAlleleProfileCommand,
    # ) -> model.SeqDbAlleleProfile | list[model.SeqDbAlleleProfile]:
    #     raise NotImplementedError()
