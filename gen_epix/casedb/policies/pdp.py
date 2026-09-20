from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, enum
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.casedb.domain.service import BaseAbacService


class PolicyDecisionPoint(BasePolicyDecisionPoint):
    """Encapsulates a concrete implementation of a Policy Decision Point (PDP)
    for Casedb ABAC policies.
    """

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any) -> None:
        """Initialize the PDP with necessary configurations."""
        super().__init__(abac_service, **kwargs)
        self.abac_service: BaseAbacService

    def is_allowed(self, cmd: command.Command) -> bool:
        """Check if the command is allowed based on the ABAC policies.

        Args:
            cmd: The command to check for allowance.

        Returns:
            bool: True if the command is allowed, False otherwise.
        """
        user = cmd.user
        if user is None:
            return False
        is_allowed = False
        if isinstance(cmd, command.CreateCaseSetCommand):
            case_type_id = cmd.case_set.case_type_id
            created_in_data_collection_id = cmd.case_set.created_in_data_collection_id
            case_abac = self.abac_service.get_case_abac(cmd)
            is_allowed = case_abac.is_allowed(
                case_type_id,
                created_in_data_collection_id,
                enum.CaseRight.ADD_CASE_SET,
                True,
                tgt_data_collection_ids=cmd.data_collection_ids,
            )
        else:
            raise NotImplementedError(
                f"Allowance check for command type {type(cmd)} is not implemented."
            )
        return is_allowed

    def get_readable_cols_by_data_collection(
        self, case_type_id: UUID
    ) -> dict[str, set[str] | None]:
        """Get the readable columns for a particular CaseType.

        Returns:
            dict[data_collection_id_str, set[col_id_str] | None]: readable column IDs
              as string, per data collection ID as str for the given case type. The IDs
              are given as strings to enable performance optimizations. If None, all
              columns are considered readable.
        """
        raise NotImplementedError()

    def get_readable_cols_for_data_collections(
        self, case_type_id: UUID, data_collection_ids: str
    ) -> set[UUID] | None:
        """Retrieve the set of readable column IDs for the specified data collections
        within a case type.

        Args:
            case_type_id: The ID of the case type.
            data_collection_ids: The concatenated hex-encoded sorted data collection
            IDs excluding dashes.

        Returns:
            set[UUID]|None: The set of readable column IDs, or None if all columns are readable.
        """
        raise NotImplementedError()

    def get_writable_cols_by_data_collection(
        self, case_type_id: UUID
    ) -> dict[str, set[str] | None]:
        """Get the writable columns for a particular CaseType.

        Returns:
            dict[data_collection_id_str, set[col_id_str] | None]: writable column IDs
              as string, per data collection ID as str for the given case type. The IDs
              are given as strings to enable performance optimizations. If None, all
              columns are considered writable.
        """
        raise NotImplementedError()

    def get_writable_cols_for_data_collections(
        self, case_type_id: UUID, data_collection_ids: str
    ) -> set[UUID] | None:
        """Retrieve the set of writable column IDs for the specified data collections within a case type.

        Args:
            case_type_id: The ID of the case type.
            data_collection_ids: The concatenated hex-encoded sorted data collection IDs excluding dashes.

        Returns:
            set[UUID]|None: The set of writable column IDs, or None if all columns are writable.
        """
        raise NotImplementedError()
