from abc import abstractmethod
from uuid import UUID

from gen_epix.casedb.domain import model
from gen_epix.commondb.policies import PolicyDecisionPoint as CommonPolicyDecisionPoint


class BasePolicyDecisionPoint(CommonPolicyDecisionPoint):
    """Encapsulates the Policy Decision Point (PDP) logic for casedb.

    This class defines the interface and must be subclassed by concrete PDP
    implementations.
    """

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
    def get_readable_cols_by_data_collection(
        self, case_type_id: UUID
    ) -> dict[str, set[str] | None]:
        raise NotImplementedError()

    @abstractmethod
    def get_readable_cols_for_data_collections(
        self, case_type_id: UUID, data_collection_ids: str
    ) -> set[UUID] | None:
        raise NotImplementedError()

    @abstractmethod
    def get_writable_cols_by_data_collection(
        self, case_type_id: UUID
    ) -> dict[str, set[str] | None]:
        raise NotImplementedError()

    @abstractmethod
    def get_writable_cols_for_data_collections(
        self, case_type_id: UUID, data_collection_ids: str
    ) -> set[UUID] | None:
        raise NotImplementedError()
