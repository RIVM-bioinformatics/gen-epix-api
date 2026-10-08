"""Implement Casedb policy decisions and case-level ABAC checks."""

from collections.abc import Iterable
from typing import Literal
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import OnException


class PolicyDecisionPoint(BasePolicyDecisionPoint):
    """Encapsulate the concrete Casedb Policy Decision Point (PDP).

    This implementation evaluates Casedb-specific ABAC policies.
    """

    def is_allowed(self, cmd: command.Command) -> bool:
        """Check if the command is allowed based on the ABAC policies.

        Args:
            cmd: The command to check for allowance.

        Returns:
            bool: True if the command is allowed, False otherwise.

        Raises:
            NotImplementedError: If allowance is requested for an unsupported command.
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

    def is_readable_columns_for_data_collections(
        self,
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
    ) -> bool:
        """Check whether each requested column is readable in a supplied collection."""
        return self._are_columns_accessible_for_data_collections(
            complete_case_type, data_collection_ids, col_ids, enum.CaseRight.READ_CASE
        )

    def is_writable_columns_for_data_collections(
        self,
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
    ) -> bool:
        """Check whether each requested column is writable in a supplied collection."""
        return self._are_columns_accessible_for_data_collections(
            complete_case_type, data_collection_ids, col_ids, enum.CaseRight.WRITE_CASE
        )

    @staticmethod
    def _are_columns_accessible_for_data_collections(
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
        access_right: Literal[enum.CaseRight.READ_CASE, enum.CaseRight.WRITE_CASE],
    ) -> bool:
        """Check that each requested column is allowed by a supplied collection."""
        access_attr = {
            enum.CaseRight.READ_CASE: "read_col_ids",
            enum.CaseRight.WRITE_CASE: "write_col_ids",
        }[access_right]

        # Special case: no data collection IDs provided, content is not readable
        if not data_collection_ids:
            return False

        # Special case: no column IDs provided, content is accessible
        if not col_ids:
            return True

        is_accessible: dict[UUID, bool] = {col_id: False for col_id in col_ids}
        for data_collection_id in data_collection_ids:
            case_type_access_abac = complete_case_type.case_type_access_abacs.get(
                data_collection_id
            )
            if case_type_access_abac is None:
                continue
            accessible_col_ids = getattr(case_type_access_abac, access_attr)
            for col_id in col_ids & accessible_col_ids:
                is_accessible[col_id] = True

        return all(is_accessible.values())

    def filter_case_set_ids(
        self,
        cmd: command.CaseSetCrudCommand,
        case_set_data_collection_ids: Iterable[tuple[UUID, UUID, frozenset[UUID]]],
        right: enum.CaseRight,
        on_filtered: Literal[OnException.SKIP, OnException.RAISE] = OnException.RAISE,
    ) -> Iterable[UUID]:
        """Yield case-set IDs accessible with the requested right.

        Raises:
            UnauthorizedAuthError: If an inaccessible case set is encountered and
                `on_filtered` is `OnException.RAISE`.
        """
        # Parse input
        if right not in enum.CaseRightSet.CASE_SET.value:
            raise ValueError(f"Invalid case right for case set: {right}")

        case_abac = self.get_case_abac(cmd)

        # Special case: full access
        if case_abac.is_full_access:
            for case_set_id, _, _ in case_set_data_collection_ids:
                yield case_set_id
            return

        # Loop over each (case_set_id, case_type_id, data_collection_ids) and determine if the CaseSet is readable
        cache: dict[tuple[UUID, frozenset[UUID]], bool] = {}
        for (
            case_set_id,
            case_type_id,
            data_collection_ids,
        ) in case_set_data_collection_ids:
            is_accessible = cache.get((case_type_id, data_collection_ids))
            if is_accessible is None:
                # Not cached
                # Determine if the case set is accessible from at least one of the data collections
                cache[(case_type_id, data_collection_ids)] = False
                is_accessible = False
                if case_type_id in case_abac.case_type_access_abacs:
                    case_abac_for_case_type = case_abac.case_type_access_abacs[
                        case_type_id
                    ]
                    for data_collection_id in data_collection_ids:
                        if data_collection_id not in case_abac_for_case_type:
                            continue
                        is_accessible = case_abac_for_case_type[
                            data_collection_id
                        ].is_allowed(right)
                        if is_accessible:
                            cache[(case_type_id, data_collection_ids)] = is_accessible
                            break
            # If the case set is not accessible, handle according to the on_filtered policy
            if not is_accessible:
                if on_filtered == OnException.SKIP:
                    continue
                if on_filtered == OnException.RAISE:
                    user_id = self.get_command_user_id(cmd)
                    raise exc.UnauthorizedAuthError(
                        "dad1bec1",
                        f"User {user_id} is not authorized to access case set {case_set_id}",
                    )
            # Yield the case set ID since accessible
            yield case_set_id

    # def get_readable_cols_by_data_collection(
    #     self, case_type_id: UUID
    # ) -> dict[str, set[str] | None]:
    #     """Get the readable columns for a particular CaseType.

    #     Returns:
    #         dict[data_collection_id_str, set[col_id_str] | None]: readable column IDs
    #           as string, per data collection ID as str for the given case type. The IDs
    #           are given as strings to enable performance optimizations. If None, all
    #           columns are considered readable.
    #     """
    #     raise NotImplementedError()

    # def get_readable_cols_for_data_collections(
    #     self, case_type_id: UUID, data_collection_ids: str
    # ) -> set[UUID] | None:
    #     """Retrieve the set of readable column IDs for the specified data collections
    #     within a case type.

    #     Args:
    #         case_type_id: The ID of the case type.
    #         data_collection_ids: The concatenated hex-encoded sorted data collection
    #         IDs excluding dashes.

    #     Returns:
    #         set[UUID]|None: The set of readable column IDs, or None if all columns are readable.
    #     """
    #     raise NotImplementedError()

    # def get_writable_cols_by_data_collection(
    #     self, case_type_id: UUID
    # ) -> dict[str, set[str] | None]:
    #     """Get the writable columns for a particular CaseType.

    #     Returns:
    #         dict[data_collection_id_str, set[col_id_str] | None]: writable column IDs
    #           as string, per data collection ID as str for the given case type. The IDs
    #           are given as strings to enable performance optimizations. If None, all
    #           columns are considered writable.
    #     """
    #     raise NotImplementedError()

    # def get_writable_cols_for_data_collections(
    #     self, case_type_id: UUID, data_collection_ids: str
    # ) -> set[UUID] | None:
    #     """Retrieve the set of writable column IDs for the specified data collections within a case type.

    #     Args:
    #         case_type_id: The ID of the case type.
    #         data_collection_ids: The concatenated hex-encoded sorted data collection IDs excluding dashes.

    #     Returns:
    #         set[UUID]|None: The set of writable column IDs, or None if all columns are writable.
    #     """
    #     raise NotImplementedError()
