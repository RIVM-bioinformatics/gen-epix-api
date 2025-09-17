from abc import abstractmethod
from typing import Any, Callable, Iterable, Type
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.fastapp import BaseUnitOfWork
from gen_epix.filter import DatetimeRangeFilter, Filter


class BaseCaseService(DomainBaseCaseService):
    """
    Abstract base class for case services defining the interface contract.
    This additional base class allows splitting the implementation into
    multiple modules while maintaining linter support.
    """

    _VALUE_TO_STR = {
        enum.ColType.TIME_DAY: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_WEEK: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_MONTH: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_QUARTER: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_YEAR: lambda x: None if not x else f"{x}",
        enum.ColType.GEO_LATLON: lambda x: None if not x else f"{x}",
        enum.ColType.TEXT: lambda x: None if not x else f"{x}",
        enum.ColType.ID_DIRECT: lambda x: None if not x else f"{x}",
        enum.ColType.ID_PSEUDONYMISED: lambda x: None if not x else f"{x}",
        enum.ColType.OTHER: lambda x: None if not x else f"{x}",
        enum.ColType.DECIMAL_0: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.0f}")
        ),
        enum.ColType.DECIMAL_1: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.1f}")
        ),
        enum.ColType.DECIMAL_2: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.2f}")
        ),
        enum.ColType.DECIMAL_3: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.3f}")
        ),
        enum.ColType.DECIMAL_4: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.4f}")
        ),
        enum.ColType.DECIMAL_5: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.5f}")
        ),
        enum.ColType.DECIMAL_6: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.6f}")
        ),
    }

    @abstractmethod
    def crud(  # type:ignore[override]
        self, cmd: command.CrudCommand
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        """
        Override the base crud method to apply ABAC restrictions and cascade delete
        where necessary
        """
        pass

    @abstractmethod
    def validate_cases(
        self, cmd: command.ValidateCasesCommand
    ) -> model.CaseValidationReport:
        """Validate cases according to case type rules."""
        pass

    @abstractmethod
    def create_cases(self, cmd: command.CreateCasesCommand) -> list[model.Case] | None:
        """Create new cases with validation and authorization checks."""
        pass

    @abstractmethod
    def create_case_set(
        self, cmd: command.CreateCaseSetCommand
    ) -> model.CaseSet | None:
        """Create a new case set with associated data collection links."""
        pass

    @abstractmethod
    def retrieve_complete_case_type(
        self,
        cmd: command.RetrieveCompleteCaseTypeCommand,
    ) -> model.CompleteCaseType:
        """Retrieve complete case type information including all related metadata."""
        pass

    @abstractmethod
    def retrieve_case_type_stats(
        self,
        cmd: command.RetrieveCaseTypeStatsCommand,
    ) -> list[model.CaseTypeStat]:
        """Retrieve statistical information about case types."""
        pass

    @abstractmethod
    def retrieve_case_set_stats(
        self,
        cmd: command.RetrieveCaseSetStatsCommand,
    ) -> list[model.CaseSetStat]:
        """Retrieve statistical information about case sets."""
        pass

    @abstractmethod
    def retrieve_cases_by_query(
        self, cmd: command.RetrieveCasesByQueryCommand
    ) -> list[UUID]:
        """Retrieve case IDs based on query criteria with ABAC filtering."""
        pass

    @abstractmethod
    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        """Retrieve cases by their IDs with content filtering."""
        pass

    @abstractmethod
    def retrieve_case_or_set_rights(
        self,
        cmd: command.RetrieveCaseRightsCommand | command.RetrieveCaseSetRightsCommand,
    ) -> list[model.CaseRights] | list[model.CaseSetRights]:
        """Retrieve access rights for cases or case sets."""
        pass

    @abstractmethod
    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeByCasesCommand
    ) -> model.PhylogeneticTree:
        """Retrieve phylogenetic tree for a set of cases."""
        pass

    @abstractmethod
    def retrieve_genetic_sequence_by_case(
        self,
        cmd: command.RetrieveGeneticSequenceByCaseCommand,
    ) -> list[model.GeneticSequence]:
        """Retrieve genetic sequences associated with cases."""
        pass

    @abstractmethod
    def retrieve_genetic_sequence_fasta_by_case(
        self, cmd: command.RetrieveGeneticSequenceFastaByCaseCommand
    ) -> Iterable[str]:
        """Return a streaming iterable of FASTA formatted lines for genetic sequences."""
        pass

    @abstractmethod
    def fasta_file_generator(
        self,
        sequences: Iterable[model.GeneticSequence],
        wrap: int | None = 80,
    ) -> Iterable[str]:
        """Generate FASTA format strings from genetic sequences."""
        pass

    @abstractmethod
    def _read_association_with_valid_ids(
        self,
        command_class: Type[command.CrudCommand],
        field_name1: str,
        field_name2: str,
        valid_ids1: set[UUID] | frozenset[UUID] | None = None,
        valid_ids2: set[UUID] | frozenset[UUID] | None = None,
        match_all1: bool = False,
        match_all2: bool = False,
        return_type: str = "objects",
        uow: BaseUnitOfWork | None = None,
        user: model.User | None = None,
    ) -> list[model.Model] | list[UUID] | dict[UUID, set[UUID]]:
        """Read association entities with ID validation."""
        pass

    @abstractmethod
    def _retrieve_case_sets_with_content_right(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_set_ids: list[UUID] | None = None,
        case_type_ids: set[UUID] | None = None,
        filter: Filter | None = None,
        on_invalid_case_set_id: str = "raise",
    ) -> list[model.CaseSet]:
        """Retrieve case sets that the user has specific content rights for."""
        pass

    @abstractmethod
    def _retrieve_cases_with_content_right(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_ids: list[UUID] | None = None,
        case_type_ids: set[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
        on_invalid_case_id: str = "raise",
        filter_content: bool = True,
        extra_access_case_type_col_ids: set[UUID] | None = None,
    ) -> list[model.Case]:
        """Retrieve cases that the user has specific content rights for."""
        pass

    @abstractmethod
    def _retrieve_case_data_collections_map(
        self, uow: BaseUnitOfWork, user_id: UUID, **kwargs: Any
    ) -> dict[UUID, set[UUID]]:
        """Retrieve mapping of cases to their data collections."""
        pass

    @abstractmethod
    def _retrieve_case_set_data_collections_map(
        self, uow: BaseUnitOfWork, user_id: UUID, **kwargs: Any
    ) -> dict[UUID, set[UUID]]:
        """Retrieve mapping of case sets to their data collections."""
        pass

    @abstractmethod
    def _retrieve_case_case_sets_map(
        self, uow: BaseUnitOfWork, user_id: UUID, **kwargs: Any
    ) -> dict[UUID, set[UUID]]:
        """Retrieve mapping of cases to their case sets."""
        pass

    @abstractmethod
    def _retrieve_association_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        association_class: Type[model.Model],
        link_field_name1: str,
        link_field_name2: str,
        **kwargs: Any,
    ) -> dict[UUID, set[UUID]]:
        """
        Get a dict[obj_id1, set[obj_ids]] based on the association stored in the association_class objs.
        """
        pass

    @abstractmethod
    def _retrieve_sequence_column_data(
        self, uow: BaseUnitOfWork, user: model.User, seq_case_type_col_id: UUID
    ) -> tuple[model.CaseTypeCol, model.Col]:
        """Retrieve sequence column data and validate it's a genetic sequence column."""
        pass

    @abstractmethod
    def _verify_case_filter(
        self, uow: BaseUnitOfWork, user: model.User, filter: Filter
    ) -> list[model.Col]:
        """Verify case filter validity and return associated columns."""
        pass

    @abstractmethod
    def _verify_case_set_member_case_type(
        self, user: model.User, case_set_members: list[model.CaseSetMember]
    ) -> None:
        """Verify that case set members have matching case types with their case sets."""
        pass

    @staticmethod
    @abstractmethod
    def _get_map_functions_for_filters(
        cols: Iterable[model.Col],
    ) -> list[Callable[[Any], Any]]:
        """Get mapping functions for filter processing based on column types."""
        pass

    @staticmethod
    @abstractmethod
    def _compose_id_filter(*key_and_ids: tuple[str, set[UUID]]) -> Filter:
        """Compose filter for ID-based filtering."""
        pass
