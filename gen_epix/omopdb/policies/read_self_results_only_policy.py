"""Configure self-scoped result reads for OmopDB commands."""

from typing import Any

from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)


class ReadSelfResultsOnlyPolicy(CommonReadSelfResultsOnlyPolicy):
    """Encapsulates restrictions on shared self-result reads according to OmopDB command metadata."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Initialize self-scoped command metadata for OmopDB."""
        super().__init__(
            abac_service,
            **kwargs,
        )
        self.id_attr_by_command_class.update(set())
