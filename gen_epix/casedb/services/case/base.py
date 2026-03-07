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
    """
    Abstract base class for case services defining the interface contract.
    This additional base class allows splitting the implementation into
    multiple modules while maintaining linter support.
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
        """Read association entities with ID validation."""
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
        """Retrieve case sets that the user has specific content rights for."""
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
        extra_access_case_col_ids: set[UUID] | None = None,
        apply_max_n_cases: bool = True,
    ) -> list[model.Case]:
        """Retrieve cases that the user has specific content rights for."""
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_case_data_collections_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_ids: Iterable[UUID] | None = None,
        data_collection_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve mapping of cases to their data collections."""
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_case_set_data_collections_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_set_ids: Iterable[UUID] | None = None,
        data_collection_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve mapping of case sets to their data collections."""
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_case_case_sets_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_ids: Iterable[UUID] | None = None,
        case_set_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve mapping of cases to their case sets."""
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
        """
        Get a dict[obj_id1, set[obj_ids]] based on the association stored in the association_class objs.
        """
        raise NotImplementedError()

    @abstractmethod
    def _retrieve_seq_column_data(
        self, uow: BaseUnitOfWork, user: model.User, seq_col_id: UUID
    ) -> tuple[model.Col, model.RefCol]:
        """Retrieve sequence column data and validate it's a genetic sequence column."""
        raise NotImplementedError()

    @abstractmethod
    def _verify_case_set_member_case_type(
        self, user: model.User, case_set_members: list[model.CaseSetMember]
    ) -> None:
        """Verify that case set members have matching CaseTypes with their case sets."""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def _compose_id_filter(*key_and_ids: tuple[str, set[UUID]]) -> Filter:
        """Compose filter for ID-based filtering."""
        pass
