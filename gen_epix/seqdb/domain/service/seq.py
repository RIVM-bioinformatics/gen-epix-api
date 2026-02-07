import abc
from collections.abc import Iterable

from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ServiceType


class BaseSeqService(BaseService):
    SERVICE_TYPE = ServiceType.SEQ

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(
            command.RetrievePhylogeneticTreeCommand,
            self.retrieve_phylogenetic_tree,
        )
        f(
            command.RetrieveMultipleAlignmentCommand,
            self.retrieve_multiple_alignment,
        )
        f(command.RetrieveSamplesCommand, self.retrieve_samples)
        f(
            command.RetrieveSeqFastaCommand,
            self.retrieve_seq_fasta,
        )
        f(
            command.UploadSamplesCommand,
            self.upload_samples,
        )

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
    def retrieve_samples(
        self,
        cmd: command.RetrieveSamplesCommand,
    ) -> list[model.SampleForUpload]:
        raise NotImplementedError()
        
    @abc.abstractmethod
    def retrieve_seq_fasta(self, cmd: command.RetrieveSeqFastaCommand) -> Iterable[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        raise NotImplementedError()
