"""Define case command handlers implemented by Casedb case services."""

import abc
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseCaseRepository
from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain import model as seqdb_model


class BaseCaseService(BaseService[BaseCaseRepository]):
    """Encapsulates case command dispatch, limits, and persistence operations.

    The service classifies commands by their ABAC requirements, registers CRUD
    and specialized handlers, and defines the backend-independent interface
    implemented by concrete case services. Cascade-delete metadata identifies
    dependent association models removed with their parent objects.

    Attributes:
        NO_ABAC_COMMAND_CLASSES: Commands that do not require case ABAC data.
        ABAC_REFDATA_COMMAND_CLASSES: Commands governed by reference-data access.
        ABAC_DATA_COMMAND_CLASSES: Commands governed by case-data access.
        CASCADE_DELETE_MODEL_CLASSES: Dependent models removed with each parent.
    """

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
        """Initialize the service and its default case-type limits.

        Args:
            *args: Positional arguments forwarded to the base service.
            default_props: Default limits for case create, read, update, delete,
                and tree operations. Built-in limits are used when omitted.
            **kwargs: Keyword arguments forwarded to the base service.
        """
        super().__init__(*args, **kwargs)

        self._default_props = default_props or model.CaseTypeProps(
            create_max_n_cases=self.DEFAULT_CREATE_MAX_N_CASES,
            read_max_n_cases=self.DEFAULT_READ_MAX_N_CASES,
            read_max_tree_size=self.DEFAULT_READ_MAX_TREE_SIZE,
            update_max_n_cases=self.DEFAULT_UPDATE_MAX_N_CASES,
            delete_max_n_cases=self.DEFAULT_DELETE_MAX_N_CASES,
        )

    def register_handlers(self) -> None:
        """Register case CRUD, association, retrieval, and file handlers.

        This mutates the application dispatch table during service
        initialization. Association commands use the shared association handler;
        all other commands are bound to their specialized service methods.
        """
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
        f(
            command.CaseTypeSetCaseTypeUpdateAssociationCommand,
            self.update_association,
        )
        f(command.ColSetColUpdateAssociationCommand, self.update_association)
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
        f(command.RetrieveCaseSetStatsCommand, self.retrieve_case_stats)
        f(command.RetrieveCaseTypeStatsCommand, self.retrieve_case_stats)
        f(command.RetrieveCasesByQueryCommand, self.retrieve_cases_by_query)
        f(
            command.RetrieveCaseCohortLinksByCaseTypeCommand,
            self.retrieve_case_cohort_links_by_case_type,
        )
        f(command.RetrieveCasesByIdCommand, self.retrieve_cases_by_id)
        f(command.RetrieveCaseRightsCommand, self.retrieve_case_or_set_rights)
        f(command.RetrieveCaseSetRightsCommand, self.retrieve_case_or_set_rights)
        f(
            command.RetrievePhylogeneticTreeByCasesCommand,
            self.retrieve_phylogenetic_tree,
        )
        f(command.RetrieveSimilarCasesCommand, self.retrieve_similar_cases)
        f(command.RetrieveIsOwnCasesCommand, self.retrieve_is_own_cases)
        f(
            command.RetrieveGeneticSequenceFastaByCaseCommand,
            self.retrieve_genetic_sequence_fasta_by_case,
        )
        f(command.CreateFileForReadSetCommand, self.create_file_for_read_set)
        f(command.CreateFileForSeqCommand, self.create_file_for_seq)
        f(
            command.RetrieveProtocolsCommand,
            self.retrieve_protocols,
        )

    @abc.abstractmethod
    def crud_case(
        self, cmd: command.CaseCrudCommand
    ) -> list[model.Case] | model.Case | list[UUID] | UUID | list[bool] | bool | None:
        """Handle a CRUD command for case entities.

        Args:
            cmd: Case CRUD command to execute.

        Returns:
            Cases, identifiers, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case identifiers.

        Args:
            cmd: Case-identifier CRUD command to execute.

        Returns:
            Case identifiers, UUIDs, booleans, or ``None`` according to the
            operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case data-collection links.

        Args:
            cmd: Case data-collection link CRUD command to execute.

        Returns:
            Link objects, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case-set categories.

        Args:
            cmd: Case-set category CRUD command to execute.

        Returns:
            Categories, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case sets.

        Args:
            cmd: Case-set CRUD command to execute.

        Returns:
            Case sets, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case-set data-collection links.

        Args:
            cmd: Case-set data-collection link CRUD command to execute.

        Returns:
            Link objects, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case-set members.

        Args:
            cmd: Case-set member CRUD command to execute.

        Returns:
            Members, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case-set statuses.

        Args:
            cmd: Case-set status CRUD command to execute.

        Returns:
            Statuses, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_col(
        self, cmd: command.ColCrudCommand
    ) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
        """Handle a CRUD command for case-type columns.

        Args:
            cmd: Column CRUD command to execute.

        Returns:
            Columns, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_col_set(
        self, cmd: command.ColSetCrudCommand
    ) -> (
        list[model.ColSet] | model.ColSet | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle a CRUD command for column sets.

        Args:
            cmd: Column-set CRUD command to execute.

        Returns:
            Column sets, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for column-set members.

        Args:
            cmd: Column-set member CRUD command to execute.

        Returns:
            Members, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case types.

        Args:
            cmd: Case-type CRUD command to execute.

        Returns:
            Case types, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case-type-set categories.

        Args:
            cmd: Case-type-set category CRUD command to execute.

        Returns:
            Categories, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case-type sets.

        Args:
            cmd: Case-type-set CRUD command to execute.

        Returns:
            Case-type sets, UUIDs, booleans, or ``None`` according to the
            operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for case-type-set members.

        Args:
            cmd: Case-type-set member CRUD command to execute.

        Returns:
            Members, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_dim(
        self, cmd: command.DimCrudCommand
    ) -> list[model.Dim] | model.Dim | list[UUID] | UUID | list[bool] | bool | None:
        """Handle a CRUD command for case-type dimensions.

        Args:
            cmd: Dimension CRUD command to execute.

        Returns:
            Dimensions, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_ref_col(
        self, cmd: command.RefColCrudCommand
    ) -> (
        list[model.RefCol] | model.RefCol | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle a CRUD command for reference columns.

        Args:
            cmd: Reference-column CRUD command to execute.

        Returns:
            Reference columns, UUIDs, booleans, or ``None`` according to the
            operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_ref_dim(
        self, cmd: command.RefDimCrudCommand
    ) -> (
        list[model.RefDim] | model.RefDim | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle a CRUD command for reference dimensions.

        Args:
            cmd: Reference-dimension CRUD command to execute.

        Returns:
            Reference dimensions, UUIDs, booleans, or ``None`` according to the
            operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for genetic-distance protocols.

        Args:
            cmd: Genetic-distance protocol CRUD command to execute.

        Returns:
            Protocols, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for tree-algorithm classes.

        Args:
            cmd: Tree-algorithm class CRUD command to execute.

        Returns:
            Algorithm classes, UUIDs, booleans, or ``None`` according to the
            operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
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
        """Handle a CRUD command for tree algorithms.

        Args:
            cmd: Tree-algorithm CRUD command to execute.

        Returns:
            Algorithms, UUIDs, booleans, or ``None`` according to the operation.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_cases(
        self, cmd: command.UploadCasesCommand
    ) -> model.CaseBatchUploadResult | None:
        """Upload a batch of cases and related data.

        Implementations may persist cases, identifiers, and associations.

        Args:
            cmd: Case-upload command containing the batch.

        Returns:
            The batch upload result, or ``None`` when no result is produced.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                upload.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def create_case_set(
        self, cmd: command.CreateCaseSetCommand
    ) -> model.CaseSet | None:
        """Create a case set from the command selection.

        Implementations persist the case set and its requested memberships.

        Args:
            cmd: Case-set creation command to execute.

        Returns:
            The created case set, or ``None`` when no set is created.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                creation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_complete_case_type(
        self,
        cmd: command.RetrieveCompleteCaseTypeCommand,
    ) -> model.CompleteCaseType:
        """Retrieve a case type with its associated schema data.

        Args:
            cmd: Command identifying the case type to retrieve.

        Returns:
            The complete case-type definition visible to the command user.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_case_stats(
        self,
        cmd: command.RetrieveCaseTypeStatsCommand | command.RetrieveCaseSetStatsCommand,
    ) -> list[model.CaseStats]:
        """Retrieve access-filtered statistics by case type or case set.

        Args:
            cmd: Case-type or case-set statistics command to execute.

        Returns:
            Statistics for each accessible requested case type or case set.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_cases_by_query(
        self, cmd: command.RetrieveCasesByQueryCommand
    ) -> model.CaseQueryResult:
        """Retrieve access-filtered cases matching query criteria.

        Args:
            cmd: Case query containing filters and result options.

        Returns:
            Matching cases and query result metadata.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_case_cohort_links_by_case_type(
        self, cmd: command.RetrieveCaseCohortLinksByCaseTypeCommand
    ) -> list[model.CaseCohortLink]:
        """Retrieve case-cohort links for a case type.

        Args:
            cmd: Command identifying the case type.

        Returns:
            Case-cohort links belonging to the requested case type.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        """Retrieve access-filtered cases by identifier.

        Args:
            cmd: Command containing the case identifiers to retrieve.

        Returns:
            Requested cases visible to the command user.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_case_or_set_rights(
        self,
        cmd: command.RetrieveCaseRightsCommand | command.RetrieveCaseSetRightsCommand,
    ) -> list[model.CaseRights] | list[model.CaseSetRights]:
        """Retrieve the command user's rights for cases or case sets.

        Args:
            cmd: Case-rights or case-set-rights command to execute.

        Returns:
            Rights aligned with the requested case or case-set identifiers.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_phylogenetic_tree(
        self,
        cmd: command.RetrievePhylogeneticTreeByCasesCommand,
    ) -> model.PhylogeneticTree:
        """Retrieve a phylogenetic tree for specified cases.

        Args:
            cmd: Tree command containing case identifiers and parameters.

        Returns:
            The phylogenetic tree generated from accessible case sequences.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                operation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_similar_cases(
        self,
        cmd: command.RetrieveSimilarCasesCommand,
    ) -> command.RetrieveSimilarCasesReturnValue:
        """Retrieve cases genetically similar to a specified case.

        Args:
            cmd: Similarity command containing the reference case and parameters.

        Returns:
            Similar case identifiers and command-defined similarity metadata.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_genetic_sequence_fasta_by_case(
        self,
        cmd: command.RetrieveGeneticSequenceFastaByCaseCommand,
    ) -> Iterable[str]:
        """Retrieve genetic sequence data in FASTA format for cases.

        Args:
            cmd: FASTA retrieval command containing case identifiers.

        Returns:
            An iterable of FASTA-formatted text fragments.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def create_file_for_read_set(
        self,
        cmd: command.CreateFileForReadSetCommand,
    ) -> UUID:
        """Create a file for a case-linked read set.

        Implementations persist file metadata or delegate creation to Seqdb.

        Args:
            cmd: Command identifying the case-linked read set.

        Returns:
            The identifier of the created file.

        Raises:
            NotImplementedError: Always, until a concrete service implements file
                creation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def create_file_for_seq(
        self,
        cmd: command.CreateFileForSeqCommand,
    ) -> UUID:
        """Create a file for a case-linked sequence.

        Implementations persist file metadata or delegate creation to Seqdb.

        Args:
            cmd: Command identifying the case-linked sequence.

        Returns:
            The identifier of the created file.

        Raises:
            NotImplementedError: Always, until a concrete service implements file
                creation.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_protocols(
        self,
        cmd: command.RetrieveProtocolsCommand,
    ) -> list[seqdb_model.Protocol]:
        """Retrieve sequence protocols available to Casedb.

        Args:
            cmd: Protocol retrieval command to execute.

        Returns:
            Available sequence protocols.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_is_own_cases(
        self,
        cmd: command.RetrieveIsOwnCasesCommand,
    ) -> dict[UUID, bool]:
        """Determine whether the command user owns specified cases.

        Args:
            cmd: Ownership command containing case identifiers.

        Returns:
            A mapping from each requested case identifier to its ownership flag.

        Raises:
            NotImplementedError: Always, until a concrete service implements the
                query.
        """
        raise NotImplementedError()
