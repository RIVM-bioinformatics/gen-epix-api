from typing import Iterable, Literal
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.fastapp.enum import OnException


class PolicyDecisionPoint(BasePolicyDecisionPoint):
    """Encapsulates a concrete implementation of a Policy Decision Point (PDP)
    for Casedb ABAC policies.
    """

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

    def is_readable_columns_for_data_collections(
        self,
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
    ) -> bool:
        """See parent class."""
        __doc__ = (
            BasePolicyDecisionPoint.is_readable_columns_for_data_collections.__doc__
        )

        # Special case: no data collection IDs provided, content is not readable
        if not data_collection_ids:
            return False

        # Special case: no column IDs provided, content is readable
        if not col_ids:
            return True

        # Check readability for each column in the context of the provided data collections
        is_readable: dict[UUID, bool] = {col_id: False for col_id in col_ids}
        for data_collection_id in data_collection_ids:
            case_type_access_abac = complete_case_type.case_type_access_abacs.get(
                data_collection_id
            )
            if case_type_access_abac is None:
                continue
            for col_id in col_ids & case_type_access_abac.read_col_ids:
                is_readable[col_id] = True

        return all(is_readable.values())

    def filter_readable_case_sets(
        self,
        user: model.User,
        case_sets: Iterable[model.CaseSet],
        case_set_data_collection_ids: Iterable[frozenset[UUID]],
        on_filtered: Literal[OnException.IGNORE, OnException.RAISE] = OnException.RAISE,
    ) -> Iterable[model.CaseSet]:
        """See parent class."""
        __doc__ = BasePolicyDecisionPoint.filter_readable_case_sets.__doc__

        case_abac = self.get_case_abac
        for case_set, data_collection_ids in zip(
            case_sets, case_set_data_collection_ids
        ):
            if self.is_readable_columns_for_data_collections(
                complete_case_type=case_set.complete_case_type,
                data_collection_ids=data_collection_ids,
                col_ids=frozenset(case_set.col_ids),
            ):
                filtered_case_sets.append(case_set)
            elif on_filtered == OnException.RAISE:
                raise UnauthorizedAuthError(
                    f"User {user} is not authorized to access case set {case_set.id}"
                )

        return filtered_case_sets

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
