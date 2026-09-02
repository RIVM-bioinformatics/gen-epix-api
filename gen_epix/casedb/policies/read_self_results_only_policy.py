"""Extend self-only result filtering to casedb user case policies."""

from typing import Any

from gen_epix.casedb.domain import command
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)


class ReadSelfResultsOnlyPolicy(CommonReadSelfResultsOnlyPolicy):
    """Filter casedb user case-policy reads to the current user's records."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Register ownership attributes for casedb user case-policy commands.

        Args:
            abac_service: Service used by the shared self-only filter.
            **kwargs: Additional shared policy configuration.
        """
        super().__init__(
            abac_service,
            **kwargs,
        )
        self.id_attr_by_command_class.update(
            {
                command.UserAccessCasePolicyCrudCommand: "user_id",
                command.UserShareCasePolicyCrudCommand: "user_id",
            }
        )
