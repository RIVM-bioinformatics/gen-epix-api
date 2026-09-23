from abc import abstractmethod
from typing import Any, Iterable, Literal
from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.commondb.policies import PolicyDecisionPoint as CommonPolicyDecisionPoint
from gen_epix.fastapp import OnException


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
        """
        raise NotImplementedError()

    @abstractmethod
    def filter_readable_case_sets(
        self,
        user: model.User,
        case_sets: Iterable[model.CaseSet],
        case_set_data_collection_ids: Iterable[frozenset[UUID]],
        on_filtered: Literal[OnException.IGNORE, OnException.RAISE] = OnException.RAISE,
    ) -> Iterable[model.CaseSet]:
        """Check if the case set is readable for the specified data collections.

        Args:
            user: The user for whom readability is being checked.
            case_sets: The list of case sets to check for readability.
            case_set_data_collection_ids: The list of sets of data collection IDs corresponding to each case set.
            on_filtered: The action to take when a case set is filtered out (ignored or raised as an exception).

        Returns:
            Iterable[model.CaseSet]: The subset of case sets that are readable for the specified data collections.

        Raises:
            UnauthorizedAuthError: If on_filtered is set to RAISE and a case set is not readable.
        """
        raise NotImplementedError()

    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        """Retrieve the ABAC object associated with the given command."""
        return self.abac_service.get_case_abac(cmd)

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
