from uuid import UUID

from gen_epix import fastapp
from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.fastapp import exc

# Shorthands for readability
_PTS = fastapp.PermissionTypeSet
_RS = enum.RoleSet


class AbacPolicyDecisionPoint:
    """Encapsulates Policy Decision Point (PDP) logic for ABAC policies.

    This centralizes the decision-making logic for ABAC policies that are intended
    to be applied during command execution either for performance reasons or because
    there is no good alternative to implement them otherwise. Policies intended to be
    applied before or after command execution can be handled by the App's own policy
    decision and enforcement points.

    The PDP determines and applies access rights based on user roles, permissions, and
    other attributes. It mainly forms a wrapper around the ABAC service's functionality
    that can easily be injected into other code.

    The Policy Enforcement Points (PEPs) that make use of this PDP are located within
    the handler for the command on which ABAC needs to be applied. As such, the handler
    needs to obtain the PDP instance itself.
    """

    def __init__(self, abac_service: BaseAbacService, user: model.User | None):
        """Initialize the PDP with necessary configurations."""
        self.abac_service = abac_service
        self.user = user
        if user and user.id is None:
            raise exc.ServiceException("d3a74f81", message="User must have an ID.")
        self.user_id = None if user is None else user.id

    def get_command_user_id(self, cmd: command.Command) -> UUID | None:
        """Retrieve the user ID associated with the command.

        Raises:
            exc.ServiceException: If the command has a user without an ID.

        Returns:
            UUID|None: The user ID if available, otherwise None.
        """
        if cmd.user is None:
            return None
        if cmd.user.id is None:
            raise exc.ServiceException(
                "e61b3c09", message="Command user must have an ID."
            )
        return cmd.user.id

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

    def is_exempted(self, cmd: command.Command) -> bool:
        """Check if the command is exempted from ABAC policies based on the user's roles.

        Args:
            cmd: The command to check for exemption.

        Returns:
            bool: True if the command is exempted, False otherwise.
        """
        user = self._verify_user(cmd)
        if user is None:
            return True
        exempted_role_set = self.abac_service.ABAC_EXEMPTED_ROLE_SET_MAP.get(type(cmd))
        if exempted_role_set is None:
            return False
        has_exempted_role = bool(
            user.roles & {x.value for x in exempted_role_set.value}
        )
        return has_exempted_role

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

    def _verify_user(self, cmd: command.Command) -> model.User | None:
        """Verify that the user associated with the command is the same one as this PDP
        is initialized with.

        Raises:
            exc.ServiceException: If the user associated with the command does not
            match the PDP's user.

        Returns:
            UUID|None: The user ID if available, otherwise None.
        """
        user_id = self.get_command_user_id(cmd)
        if self.user_id != user_id:
            raise exc.ServiceException(
                "4a90f257",
                message=f"Different user expected: {self.user_id}, but command has user ID: {user_id}.",
            )
        return cmd.user
