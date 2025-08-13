import abc
from typing import Type
from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.fastapp import BaseService


class BaseCaseService(BaseService):
    SERVICE_TYPE = ServiceType.CASE

    NO_ABAC_COMMAND_CLASSES: set[Type[command.Command]] = {
        command.TreeAlgorithmClassCrudCommand,
        command.TreeAlgorithmCrudCommand,
        command.GeneticDistanceProtocolCrudCommand,
        command.DimCrudCommand,
        command.ColCrudCommand,
        command.CaseTypeSetCategoryCrudCommand,
        command.CaseSetCategoryCrudCommand,
        command.CaseSetStatusCrudCommand,
    }
    ABAC_METADATA_COMMAND_CLASSES: set[Type[command.Command]] = {
        command.CaseTypeCrudCommand,
        command.CaseTypeSetMemberCrudCommand,
        command.CaseTypeSetCrudCommand,
        command.CaseTypeColCrudCommand,
        command.CaseTypeColSetMemberCrudCommand,
        command.CaseTypeColSetCrudCommand,
    }
    ABAC_DATA_COMMAND_CLASSES: set[Type[command.Command]] = {
        command.CaseCrudCommand,
        command.CaseSetCrudCommand,
        command.CaseSetMemberCrudCommand,
        command.CaseDataCollectionLinkCrudCommand,
        command.CaseSetDataCollectionLinkCrudCommand,
    }
    CASCADE_DELETE_MODEL_CLASSES: dict[
        Type[model.Model], tuple[Type[model.Model], ...]
    ] = {
        model.CaseTypeSet: (model.CaseTypeSetMember,),
        model.CaseType: (model.CaseTypeSetMember,),
        model.CaseTypeColSet: (model.CaseTypeColSetMember,),
        model.CaseTypeCol: (model.CaseTypeColSetMember,),
        model.CaseSet: (
            model.CaseSetDataCollectionLink,
            model.CaseSetMember,
        ),
        model.Case: (
            model.CaseDataCollectionLink,
            model.CaseSetMember,
        ),
    }

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseCaseRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.CaseSetCreateCommand, self.create_cases_or_set)
        f(command.CasesCreateCommand, self.create_cases_or_set)
        f(command.RetrieveCompleteCaseTypeCommand, self.retrieve_complete_case_type)
        f(command.RetrieveCaseTypeStatsCommand, self.retrieve_case_type_stats)
        f(command.RetrieveCaseSetStatsCommand, self.retrieve_case_set_stats)
        f(command.RetrieveCasesByQueryCommand, self.retrieve_cases_by_query)
        f(command.RetrieveCasesByIdCommand, self.retrieve_cases_by_id)
        f(command.RetrieveCaseRightsCommand, self.retrieve_case_or_set_rights)
        f(command.RetrieveCaseSetRightsCommand, self.retrieve_case_or_set_rights)
        f(command.RetrieveGeneticSequenceByCaseCommand, self.retrieve_genetic_sequence)
        f(
            command.RetrievePhylogeneticTreeByCasesCommand,
            self.retrieve_phylogenetic_tree,
        )
        f(command.RetrieveGeneticSequenceByCaseCommand, self.retrieve_genetic_sequence)

    @abc.abstractmethod
    def create_cases_or_set(
        self, cmd: command.CaseSetCreateCommand | command.CasesCreateCommand
    ) -> model.CaseSet | list[model.Case] | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_complete_case_type(
        self,
        cmd: command.RetrieveCompleteCaseTypeCommand,
    ) -> model.CompleteCaseType:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_case_set_stats(
        self,
        cmd: command.RetrieveCaseSetStatsCommand,
    ) -> list[model.CaseSetStat]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_case_type_stats(
        self,
        cmd: command.RetrieveCaseTypeStatsCommand,
    ) -> list[model.CaseTypeStat]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_cases_by_query(
        self, cmd: command.RetrieveCasesByQueryCommand
    ) -> list[UUID]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_case_or_set_rights(
        self,
        cmd: command.RetrieveCaseRightsCommand | command.RetrieveCaseSetRightsCommand,
    ) -> list[model.CaseRights] | list[model.CaseSetRights]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_phylogenetic_tree(
        self,
        cmd: command.RetrievePhylogeneticTreeByCasesCommand,
    ) -> model.PhylogeneticTree:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_genetic_sequence(
        self,
        cmd: command.RetrieveGeneticSequenceByCaseCommand,
    ) -> list[model.GeneticSequence]:
        raise NotImplementedError()
