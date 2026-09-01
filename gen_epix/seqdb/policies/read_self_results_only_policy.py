"""Implement seqdb authorization policy behavior for policies.read_self_results_only_policy."""

from typing import Any

from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)


class ReadSelfResultsOnlyPolicy(CommonReadSelfResultsOnlyPolicy):
    """Restrict eligible result reads to resources owned by the caller."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Initialize the shared policy with seqdb identifier-attribute mappings."""
        super().__init__(
            abac_service,
            **kwargs,
        )
        self.id_attr_by_command_class.update(set())
