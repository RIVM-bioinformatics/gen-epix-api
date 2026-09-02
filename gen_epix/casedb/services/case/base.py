"""Define the shared interface and helpers required by case service handlers.

The module exposes :class:`BaseCaseService`, which supplies shared conversion
metadata and declares the retrieval, association, and validation operations used
by the case service implementation modules.
"""

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, ClassVar
from uuid import UUID

from cachetools import TTLCache

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import BaseUnitOfWork
from gen_epix.filter import DatetimeRangeFilter, Filter


class BaseCaseService(DomainBaseCaseService):
    """Encapsulates the interface contract shared by case service handlers.

    This additional base class allows splitting the implementation into
    multiple modules while maintaining linter support.

    Attributes:
        role_map: Mapping of application roles by identifier.
        role_set_map: Mapping of application role sets by identifier.
    """

    _RETRIEVE_COMPLETE_CASE_TYPE_CACHE: ClassVar[TTLCache] = TTLCache(
        maxsize=1024, ttl=300
    )

    _VALUE_TO_STR = {
        enum.ColType.TIME_DAY: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_WEEK: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_MONTH: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_QUARTER: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_YEAR: lambda x: None if not x else f"{x}",
        enum.ColType.GEO_LATLON: lambda x: None if not x else f"{x}",
        enum.ColType.TEXT: lambda x: None if not x else f"{x}",
        enum.ColType.ID_PERSON: lambda x: None if not x else f"{x}",
        enum.ColType.ID_SAMPLE: lambda x: None if not x else f"{x}",
        enum.ColType.ID_CASE: lambda x: None if not x else f"{x}",
        enum.ColType.ID_EVENT: lambda x: None if not x else f"{x}",
        enum.ColType.ID_GENETIC_SEQUENCE: lambda x: None if not x else f"{x}",
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the domain service and cache application role metadata.

        Args:
            *args: Positional arguments forwarded to the domain base service.
            **kwargs: Keyword arguments forwarded to the domain base service.
        """
        super().__init__(*args, **kwargs)
        app_impl: AppImplDetails = self.app.impl
        self.role_map = app_impl.role_map
        self.role_set_map = app_impl.role_set_map

    @abstractmethod
    def _read_association_with_valid_ids(
        self,
        command_class: type[command.CrudCommand],
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
        """Read association entities constrained by valid endpoint identifiers.

        Args:
            command_class: CRUD command used to read the association model.
            field_name1: Name of the first association endpoint field.
            field_name2: Name of the second association endpoint field.
            valid_ids1: Valid identifiers for the first endpoint, if constrained.
            valid_ids2: Valid identifiers for the second endpoint, if constrained.
            match_all1: Whether every first-endpoint identifier must be present.
            match_all2: Whether every second-endpoint identifier must be present.
            return_type: Requested objects, endpoint IDs, or association mapping.
            uow: Existing unit of work to use, if supplied.
            user: User on whose behalf the command is handled, if supplied.

        Returns:
            Association objects, endpoint identifiers, or an endpoint mapping.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_case_sets_with_content_right(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_type_id: UUID | None = None,
        case_set_ids: list[UUID] | None = None,
        filter: Filter | None = None,
        on_invalid_case_set_id: str = "raise",
    ) -> list[model.CaseSet]:
        """Retrieve case sets for which a user has a content right.

        Args:
            uow: Unit of work used for repository access.
            user_id: Identifier of the user whose access is evaluated.
            case_abac: Case access policy data for the user.
            right: Required case-set content right.
            case_type_id: Optional case type restriction.
            case_set_ids: Optional identifiers of requested case sets.
            filter: Optional repository query filter.
            on_invalid_case_set_id: Whether invalid requested IDs raise or are ignored.

        Returns:
            Case sets that satisfy the request and access constraints.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_cases_with_content_right(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_type_id: UUID,
        case_ids: list[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
        on_invalid_case_id: str = "raise",
        filter_content: bool = True,
        calculate_case_date: bool = False,
        extra_access_col_ids: set[UUID] | None = None,
        apply_max_n_cases: bool = True,
    ) -> tuple[list[model.Case], bool]:
        """Retrieve cases for which a user has a content right.

        Args:
            uow: Unit of work used for repository access.
            user_id: Identifier of the user whose access is evaluated.
            case_abac: Case access policy data for the user.
            right: Required case content right.
            case_type_id: Identifier of the requested case type.
            case_ids: Optional identifiers of requested cases.
            datetime_range_filter: Optional case-date range restriction.
            on_invalid_case_id: Whether invalid requested IDs raise or are ignored.
            filter_content: Whether inaccessible content columns are removed.
            calculate_case_date: Whether the derived case date is populated.
            extra_access_col_ids: Additional column identifiers retained in content.
            apply_max_n_cases: Whether the configured result limit is applied.

        Returns:
            A pair containing accessible cases and whether the result limit was
            exceeded.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_case_data_collections_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_ids: Iterable[UUID] | None = None,
        data_collection_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve the data collections linked to cases.

        Args:
            uow: Unit of work used for repository access.
            user_id: Identifier of the user performing the retrieval.
            case_ids: Optional case identifiers to constrain the mapping.
            data_collection_ids: Optional collection identifiers to constrain it.

        Returns:
            Data collection identifiers grouped by case identifier.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_case_set_data_collections_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_set_ids: Iterable[UUID] | None = None,
        data_collection_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve the data collections linked to case sets.

        Args:
            uow: Unit of work used for repository access.
            user_id: Identifier of the user performing the retrieval.
            case_set_ids: Optional case-set identifiers to constrain the mapping.
            data_collection_ids: Optional collection identifiers to constrain it.

        Returns:
            Data collection identifiers grouped by case-set identifier.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_case_case_sets_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_ids: Iterable[UUID] | None = None,
        case_set_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve the case sets linked to cases.

        Args:
            uow: Unit of work used for repository access.
            user_id: Identifier of the user performing the retrieval.
            case_ids: Optional case identifiers to constrain the mapping.
            case_set_ids: Optional case-set identifiers to constrain the mapping.

        Returns:
            Case-set identifiers grouped by case identifier.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_association_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        association_class: type[model.Model],
        link_field_name1: str,
        link_field_name2: str,
        obj_ids1: frozenset[UUID] | None = None,
        obj_ids2: frozenset[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve linked identifiers grouped by the first association endpoint.

        Args:
            uow: Unit of work used for repository access.
            user_id: Optional identifier of the user performing the retrieval.
            association_class: Association model to query.
            link_field_name1: Name of the first endpoint field.
            link_field_name2: Name of the second endpoint field.
            obj_ids1: Optional first-endpoint identifiers to constrain the mapping.
            obj_ids2: Optional second-endpoint identifiers to constrain the mapping.

        Returns:
            Second-endpoint identifiers grouped by first-endpoint identifier.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_seq_column_data(
        self, uow: BaseUnitOfWork, user: model.User, seq_col_id: UUID
    ) -> tuple[model.Col, model.RefCol]:
        """Retrieve and validate genetic-sequence column metadata.

        Args:
            uow: Unit of work used for repository access.
            user: User performing the retrieval.
            seq_col_id: Identifier of the sequence column.

        Returns:
            The column and its reference-column metadata.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _verify_case_set_member_case_type(
        self, user: model.User, case_set_members: list[model.CaseSetMember]
    ) -> None:
        """Verify that members and their case sets have matching case types.

        Args:
            user: User performing the operation.
            case_set_members: Membership records to verify.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def _compose_id_filter(*key_and_ids: tuple[str, set[UUID]]) -> Filter:
        """Compose a filter from field names and accepted identifiers.

        Args:
            *key_and_ids: Field-name and accepted-identifier pairs.

        Returns:
            A filter matching the supplied identifier constraints.

        Raises:
            NotImplementedError: Always; subclasses must implement this operation.
        """
        raise NotImplementedError()
