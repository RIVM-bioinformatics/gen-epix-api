import abc
from collections.abc import Iterable
from uuid import UUID

from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ServiceType


class BaseSeqService(BaseService):
    SERVICE_TYPE = ServiceType.SEQ

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveCompleteAlleleProfileCommand, self.retrieve_allele_profile)
        f(command.RetrieveCompleteSamplesCommand, self.retrieve_complete_samples)
        f(
            command.RetrieveCompleteSnpProfileCommand,
            self.retrieve_snp_profile,
        )
        f(
            command.RetrievePhylogeneticTreeCommand,
            self.retrieve_phylogenetic_tree,
        )
        f(
            command.RetrieveMultipleAlignmentCommand,
            self.retrieve_multiple_alignment,
        )
        f(
            command.RetrieveSeqFastaCommand,
            self.retrieve_seq_fasta,
        )
        f(
            command.UpsertCompleteSamplesCommand,
            self.upsert_complete_samples,
        )

    @abc.abstractmethod
    def retrieve_allele_profile(
        self,
        cmd: command.RetrieveCompleteAlleleProfileCommand,
    ) -> model.CompleteAlleleProfile | list[model.CompleteAlleleProfile]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_complete_samples(
        self,
        cmd: command.RetrieveCompleteSamplesCommand,
    ) -> list[model.CompleteSample]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_snp_profile(
        self,
        cmd: command.RetrieveCompleteSnpProfileCommand,
    ) -> model.CompleteSnpProfile | list[model.CompleteSnpProfile]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeCommand
    ) -> model.PhylogeneticTree | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_multiple_alignment(
        self,
        cmd: command.RetrieveMultipleAlignmentCommand,
    ) -> model.MultipleAlignment | list[model.MultipleAlignment]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_seq_fasta(self, cmd: command.RetrieveSeqFastaCommand) -> Iterable[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def upsert_complete_samples(
        self,
        cmd: command.UpsertCompleteSamplesCommand,
    ) -> list[UUID]:
        raise NotImplementedError()
