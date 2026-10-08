"""Define Casedb's base policy decision point and ABAC filter helpers."""

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, Literal
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.commondb.policies import PolicyDecisionPoint as CommonPolicyDecisionPoint
from gen_epix.fastapp import OnException
from gen_epix.filter.base import Filter


class BasePolicyDecisionPoint(CommonPolicyDecisionPoint):
    """Encapsulates the Policy Decision Point (PDP) logic for casedb.

    This class defines the interface and must be subclassed by concrete PDP
    implementations.
    """

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any) -> None:
        """Initialize the PDP with necessary configurations."""
        super().__init__(abac_service, **kwargs)
        self.abac_service: BaseAbacService

    @abstractmethod
    def is_readable_columns_for_data_collections(
        self,
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
    ) -> bool:
        """Check if the case content is readable for the specified data collections and columns.

        Args:
            complete_case_type: The complete case type associated with the case.
            data_collection_ids: The set of data collection IDs to check for readability.
            col_ids: The set of column IDs to check for readability.

        Returns:
            bool: True if the case content is readable for the specified data collections and columns, False otherwise.

        Raises:
            NotImplementedError: If a concrete PDP does not implement the check.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_writable_columns_for_data_collections(
        self,
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
    ) -> bool:
        """Check if the specified columns are writable for the data collections.

        Args:
            complete_case_type: The complete case type associated with the case.
            data_collection_ids: The data collections associated with the case.
            col_ids: The column IDs to check for write access.

        Returns:
            True if every requested column is writable in at least one supplied
            data collection, or if no columns were requested and collections exist.
        """
        raise NotImplementedError()

    @abstractmethod
    def filter_case_set_ids(
        self,
        cmd: command.CaseSetCrudCommand,
        case_set_data_collection_ids: Iterable[tuple[UUID, UUID, frozenset[UUID]]],
        right: enum.CaseRight,
        on_filtered: Literal[OnException.SKIP, OnException.RAISE] = OnException.RAISE,
    ) -> Iterable[UUID]:
        """Check if the case set is accessible for the specified data collections with the given right.

        Args:
            cmd: The command containing the user and operation for which accessibility is being checked.
            case_set_data_collection_ids: An iterable of tuple[case_set_id, case_type_id, frozenset[data_collection_ids]]
            right: The specific case right to check for each case set.
            on_filtered: The action to take when a case set is filtered out (skipped or raised as an exception).

        Yields:
            UUID: The next case_set_id in the iterable that is accessible with the given right

        Raises:
            UnauthorizedAuthError: If on_filtered is set to RAISE and a case set is not accessible with the given right.
            NotImplementedError: If a concrete PDP does not implement the filter.
        """
        raise NotImplementedError()

    def get_case_type_id_filter(
        self, cmd: command.Command, case_type_id_field_name: str = "case_type_id"
    ) -> Filter | None:
        """Retrieve an access filter for CaseTypes.

        The filter keeps only CaseTypes the user can access. If None is returned,
        the user can access all CaseTypes.
        """
        if self.is_exempted(cmd):
            return None
        ref_data_access = self.get_ref_data_access(cmd)
        retval = ref_data_access.get_case_type_filter(case_type_id_field_name)
        return retval

    def get_col_id_filter(
        self, cmd: command.Command, col_id_field_name: str = "col_id"
    ) -> Filter | None:
        """Retrieve an access filter for columns.

        The filter keeps only columns the user can access. If None is returned, the
        user can access all columns.
        """
        if self.is_exempted(cmd):
            return None
        ref_data_access = self.get_ref_data_access(cmd)
        retval = ref_data_access.get_col_filter(col_id_field_name)
        return retval

    def get_col_set_id_filter(
        self, cmd: command.Command, col_set_id_field_name: str = "col_set_id"
    ) -> Filter | None:
        """Retrieve an access filter for column sets.

        The filter keeps only column sets the user can access. If None is returned,
        the user can access all column sets.
        """
        if self.is_exempted(cmd):
            return None
        ref_data_access = self.get_ref_data_access(cmd)
        retval = ref_data_access.get_col_set_filter(col_set_id_field_name)
        return retval

    def get_dim_id_filter(
        self, cmd: command.Command, dim_id_field_name: str = "dim_id"
    ) -> Filter | None:
        """Retrieve an access filter for dimensions.

        The filter keeps only dimensions the user can access. If None is returned,
        the user can access all dimensions.
        """
        if self.is_exempted(cmd):
            return None
        ref_data_access = self.get_ref_data_access(cmd)
        retval = ref_data_access.get_dim_filter(dim_id_field_name)
        return retval

    def get_ref_col_id_filter(
        self, cmd: command.Command, ref_col_id_field_name: str = "ref_col_id"
    ) -> Filter | None:
        """Retrieve an access filter for reference columns.

        The filter keeps only reference columns the user can access. If None is
        returned, the user can access all reference columns.
        """
        if self.is_exempted(cmd):
            return None
        ref_data_access = self.get_ref_data_access(cmd)
        retval = ref_data_access.get_ref_col_filter(ref_col_id_field_name)
        return retval

    def get_ref_dim_id_filter(
        self, cmd: command.Command, ref_dim_id_field_name: str = "ref_dim_id"
    ) -> Filter | None:
        """Retrieve an access filter for reference dimensions.

        The filter keeps only reference dimensions the user can access. If None is
        returned, the user can access all reference dimensions.
        """
        if self.is_exempted(cmd):
            return None
        ref_data_access = self.get_ref_data_access(cmd)
        retval = ref_data_access.get_ref_dim_filter(ref_dim_id_field_name)
        return retval

    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        """Retrieve the CaseAbac object associated with the given command."""
        return self.abac_service.get_case_abac(cmd)

    def get_ref_data_access(self, cmd: command.Command) -> model.RefDataAccess:
        """Retrieve the RefDataAccess object associated with the given command."""
        return self.abac_service.get_ref_data_access(cmd)

    # @abstractmethod
    # def get_readable_cols_by_data_collection(
    #     self, case_type_id: UUID
    # ) -> dict[str, set[str] | None]:
    #     raise NotImplementedError()

    # @abstractmethod
    # def get_readable_cols_for_data_collections(
    #     self, case_type_id: UUID, data_collection_ids: str
    # ) -> set[UUID] | None:
    #     raise NotImplementedError()

    # @abstractmethod
    # def get_writable_cols_by_data_collection(
    #     self, case_type_id: UUID
    # ) -> dict[str, set[str] | None]:
    #     raise NotImplementedError()

    # @abstractmethod
    # def get_writable_cols_for_data_collections(
    #     self, case_type_id: UUID, data_collection_ids: str
    # ) -> set[UUID] | None:
    #     raise NotImplementedError()
