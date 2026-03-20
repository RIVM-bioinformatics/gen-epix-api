import abc
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, exc, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain import model as seqdb_model


class BaseCaseService(BaseService):
    SERVICE_TYPE = ServiceType.CASE

    DEFAULT_CREATE_MAX_N_CASES = 1000
    DEFAULT_READ_MAX_N_CASES = 1000
    DEFAULT_READ_MAX_TREE_SIZE = 1000
    DEFAULT_UPDATE_MAX_N_CASES = 1000
    DEFAULT_DELETE_MAX_N_CASES = 1000

    NO_ABAC_COMMAND_CLASSES: set[type[command.Command]] = {
        command.TreeAlgorithmClassCrudCommand,
        command.TreeAlgorithmCrudCommand,
        command.GeneticDistanceProtocolCrudCommand,
        command.CaseTypeSetCategoryCrudCommand,
        command.CaseSetCategoryCrudCommand,
        command.CaseSetStatusCrudCommand,
        command.RefDimCrudCommand,
        command.RefColCrudCommand,
    }
    ABAC_REFDATA_COMMAND_CLASSES: set[type[command.Command]] = {
        command.CaseTypeCrudCommand,
        command.CaseTypeSetMemberCrudCommand,
        command.CaseTypeSetCrudCommand,
        command.ColCrudCommand,
        command.ColSetMemberCrudCommand,
        command.ColSetCrudCommand,
        command.DimCrudCommand,
    }
    ABAC_DATA_COMMAND_CLASSES: set[type[command.Command]] = {
        command.CaseCrudCommand,
        command.CaseIdentifierCrudCommand,
        command.CaseSetCrudCommand,
        command.CaseSetMemberCrudCommand,
        command.CaseDataCollectionLinkCrudCommand,
        command.CaseSetDataCollectionLinkCrudCommand,
        command.UploadCasesCommand,
    }
    CASCADE_DELETE_MODEL_CLASSES: dict[
        type[model.Model], tuple[type[model.Model], ...]
    ] = {
        model.CaseTypeSet: (model.CaseTypeSetMember,),
        model.CaseType: (model.CaseTypeSetMember,),
        model.ColSet: (model.ColSetMember,),
        model.Col: (model.ColSetMember,),
        model.CaseSet: (
            model.CaseSetDataCollectionLink,
            model.CaseSetMember,
        ),
        model.Case: (
            model.CaseDataCollectionLink,
            model.CaseSetMember,
        ),
    }

    def __init__(
        self,
        *args: Any,
        default_props: model.CaseTypeProps | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._default_props = default_props or model.CaseTypeProps(
            create_max_n_cases=self.DEFAULT_CREATE_MAX_N_CASES,
            read_max_n_cases=self.DEFAULT_READ_MAX_N_CASES,
            read_max_tree_size=self.DEFAULT_READ_MAX_TREE_SIZE,
            update_max_n_cases=self.DEFAULT_UPDATE_MAX_N_CASES,
            delete_max_n_cases=self.DEFAULT_DELETE_MAX_N_CASES,
        )

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseCaseRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        f(command.CaseCrudCommand, self.crud_case)
        f(command.CaseIdentifierCrudCommand, self.crud_case_identifier)
        f(
            command.CaseDataCollectionLinkCrudCommand,
            self.crud_case_data_collection_link,
        )
        f(command.CaseSetCategoryCrudCommand, self.crud_case_set_category)
        f(command.CaseSetCrudCommand, self.crud_case_set)
        f(
            command.CaseSetDataCollectionLinkCrudCommand,
            self.crud_case_set_data_collection_link,
        )
        f(command.CaseSetMemberCrudCommand, self.crud_case_set_member)
        f(command.CaseSetStatusCrudCommand, self.crud_case_set_status)
        f(command.CaseTypeCrudCommand, self.crud_case_type)
        f(command.CaseTypeSetCategoryCrudCommand, self.crud_case_type_set_category)
        f(command.CaseTypeSetCrudCommand, self.crud_case_type_set)
        f(command.CaseTypeSetMemberCrudCommand, self.crud_case_type_set_member)
        f(command.ColCrudCommand, self.crud_col)
        f(command.ColSetCrudCommand, self.crud_col_set)
        f(command.ColSetMemberCrudCommand, self.crud_col_set_member)
        f(command.DimCrudCommand, self.crud_dim)
        f(
            command.GeneticDistanceProtocolCrudCommand,
            self.crud_genetic_distance_protocol,
        )
        f(command.RefColCrudCommand, self.crud_ref_col)
        f(command.RefDimCrudCommand, self.crud_ref_dim)
        f(command.TreeAlgorithmClassCrudCommand, self.crud_tree_algorithm_class)
        f(command.TreeAlgorithmCrudCommand, self.crud_tree_algorithm)
        f(command.UploadCasesCommand, self.upload_cases)
        f(command.CreateCaseSetCommand, self.create_case_set)
        f(command.RetrieveCompleteCaseTypeCommand, self.retrieve_complete_case_type)
        f(command.RetrieveCaseStatsCommand, self.retrieve_case_stats)
        f(command.RetrieveCasesByQueryCommand, self.retrieve_cases_by_query)
        f(command.RetrieveCasesByIdCommand, self.retrieve_cases_by_id)
        f(command.RetrieveCaseRightsCommand, self.retrieve_case_or_set_rights)
        f(command.RetrieveCaseSetRightsCommand, self.retrieve_case_or_set_rights)
        f(
            command.RetrievePhylogeneticTreeByCasesCommand,
            self.retrieve_phylogenetic_tree,
        )
        f(command.RetrieveSimilarCasesCommand, self.retrieve_similar_cases)
        f(
            command.RetrieveGeneticSequenceFastaByCaseCommand,
            self.retrieve_genetic_sequence_fasta_by_case,
        )
        f(command.CreateFileForReadSetCommand, self.create_file_for_read_set)
        f(command.CreateFileForSeqCommand, self.create_file_for_seq)
        f(
            command.RetrieveSequencingProtocolsCommand,
            self.retrieve_sequencing_protocols,
        )
        f(
            command.RetrieveAssemblyProtocolsCommand,
            self.retrieve_assembly_protocols,
        )

    @abc.abstractmethod
    def crud_case(
        self, cmd: command.CaseCrudCommand
    ) -> list[model.Case] | model.Case | list[UUID] | UUID | list[bool] | bool | None:
        """Handle CRUD operations for Case entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_identifier(
        self, cmd: command.CaseIdentifierCrudCommand
    ) -> (
        list[model.CaseIdentifier]
        | model.CaseIdentifier
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseIdentifier entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_data_collection_link(
        self, cmd: command.CaseDataCollectionLinkCrudCommand
    ) -> (
        list[model.CaseDataCollectionLink]
        | model.CaseDataCollectionLink
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseDataCollectionLink entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_set_category(
        self, cmd: command.CaseSetCategoryCrudCommand
    ) -> (
        list[model.CaseSetCategory]
        | model.CaseSetCategory
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseSetCategory entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_set(
        self, cmd: command.CaseSetCrudCommand
    ) -> (
        list[model.CaseSet]
        | model.CaseSet
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseSet entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_set_data_collection_link(
        self, cmd: command.CaseSetDataCollectionLinkCrudCommand
    ) -> (
        list[model.CaseSetDataCollectionLink]
        | model.CaseSetDataCollectionLink
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseSetDataCollectionLink entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_set_member(
        self, cmd: command.CaseSetMemberCrudCommand
    ) -> (
        list[model.CaseSetMember]
        | model.CaseSetMember
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseSetMember entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_set_status(
        self, cmd: command.CaseSetStatusCrudCommand
    ) -> (
        list[model.CaseSetStatus]
        | model.CaseSetStatus
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseSetStatus entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_col(
        self, cmd: command.ColCrudCommand
    ) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
        """Handle CRUD operations for Col entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_col_set(
        self, cmd: command.ColSetCrudCommand
    ) -> (
        list[model.ColSet] | model.ColSet | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle CRUD operations for ColSet entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_col_set_member(
        self, cmd: command.ColSetMemberCrudCommand
    ) -> (
        list[model.ColSetMember]
        | model.ColSetMember
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for ColSetMember entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_type(
        self, cmd: command.CaseTypeCrudCommand
    ) -> (
        list[model.CaseType]
        | model.CaseType
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseType entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_type_set_category(
        self, cmd: command.CaseTypeSetCategoryCrudCommand
    ) -> (
        list[model.CaseTypeSetCategory]
        | model.CaseTypeSetCategory
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseTypeSetCategory entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_type_set(
        self, cmd: command.CaseTypeSetCrudCommand
    ) -> (
        list[model.CaseTypeSet]
        | model.CaseTypeSet
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseTypeSet entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_case_type_set_member(
        self, cmd: command.CaseTypeSetMemberCrudCommand
    ) -> (
        list[model.CaseTypeSetMember]
        | model.CaseTypeSetMember
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for CaseTypeSetMember entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_dim(
        self, cmd: command.DimCrudCommand
    ) -> list[model.Dim] | model.Dim | list[UUID] | UUID | list[bool] | bool | None:
        """Handle CRUD operations for Dim entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_ref_col(
        self, cmd: command.RefColCrudCommand
    ) -> (
        list[model.RefCol] | model.RefCol | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle CRUD operations for RefCol entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_ref_dim(
        self, cmd: command.RefDimCrudCommand
    ) -> (
        list[model.RefDim] | model.RefDim | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle CRUD operations for RefDim entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_genetic_distance_protocol(
        self, cmd: command.GeneticDistanceProtocolCrudCommand
    ) -> (
        list[model.GeneticDistanceProtocol]
        | model.GeneticDistanceProtocol
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for GeneticDistanceProtocol entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_tree_algorithm_class(
        self, cmd: command.TreeAlgorithmClassCrudCommand
    ) -> (
        list[model.TreeAlgorithmClass]
        | model.TreeAlgorithmClass
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for TreeAlgorithmClass entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_tree_algorithm(
        self, cmd: command.TreeAlgorithmCrudCommand
    ) -> (
        list[model.TreeAlgorithm]
        | model.TreeAlgorithm
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle CRUD operations for TreeAlgorithm entities."""
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_cases(
        self, cmd: command.UploadCasesCommand
    ) -> model.CaseBatchUploadResult | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_case_set(
        self, cmd: command.CreateCaseSetCommand
    ) -> model.CaseSet | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_complete_case_type(
        self,
        cmd: command.RetrieveCompleteCaseTypeCommand,
    ) -> model.CompleteCaseType:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_case_stats(
        self,
        cmd: command.RetrieveCaseStatsCommand,
    ) -> list[model.CaseStats]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_cases_by_query(
        self, cmd: command.RetrieveCasesByQueryCommand
    ) -> model.CaseQueryResult:
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
    def retrieve_similar_cases(
        self,
        cmd: command.RetrieveSimilarCasesCommand,
    ) -> list[UUID]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_genetic_sequence_fasta_by_case(
        self,
        cmd: command.RetrieveGeneticSequenceFastaByCaseCommand,
    ) -> Iterable[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_file_for_read_set(
        self,
        cmd: command.CreateFileForReadSetCommand,
    ) -> UUID:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_file_for_seq(
        self,
        cmd: command.CreateFileForSeqCommand,
    ) -> UUID:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_sequencing_protocols(
        self,
        cmd: command.RetrieveSequencingProtocolsCommand,
    ) -> list[seqdb_model.SequencingProtocol]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_assembly_protocols(
        self,
        cmd: command.RetrieveAssemblyProtocolsCommand,
    ) -> list[seqdb_model.AssemblyProtocol]:
        raise NotImplementedError()
