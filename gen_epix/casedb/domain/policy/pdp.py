from abc import abstractmethod
from uuid import UUID

from gen_epix.commondb.policies import PolicyDecisionPoint as CommonPolicyDecisionPoint


class BasePolicyDecisionPoint(CommonPolicyDecisionPoint):
    """Encapsulates the Policy Decision Point (PDP) logic for casedb.

    This class defines the interface and must be subclassed by concrete PDP
    implementations.
    """

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
