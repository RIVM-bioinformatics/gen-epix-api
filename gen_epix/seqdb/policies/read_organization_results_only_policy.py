"""Implement seqdb authorization policy behavior for policies.read_organization_results_only_policy."""

from typing import Any

from gen_epix.commondb.policies import (
    ReadOrganizationResultsOnlyPolicy as CommonReadOrganizationResultsOnlyPolicy,
)
from gen_epix.seqdb.domain.service import BaseAbacService


class ReadOrganizationResultsOnlyPolicy(CommonReadOrganizationResultsOnlyPolicy):
    """Encapsulates restricting result reads to the caller's authorized organization scope."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Initialize the shared policy with seqdb command-attribute mappings."""
        super().__init__(
            abac_service,
            **kwargs,
        )
        self.has_organization_id_attr_command_classes.update(set())
        self.has_user_id_attr_command_classes.update(set())
