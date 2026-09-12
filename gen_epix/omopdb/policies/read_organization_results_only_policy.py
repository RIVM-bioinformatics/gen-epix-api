"""Configure organization-scoped result reads for OmopDB commands."""

from typing import Any

from gen_epix.commondb.policies import (
    ReadOrganizationResultsOnlyPolicy as CommonReadOrganizationResultsOnlyPolicy,
)
from gen_epix.omopdb.domain.service import BaseAbacService


class ReadOrganizationResultsOnlyPolicy(CommonReadOrganizationResultsOnlyPolicy):
    """Encapsulates restrictions on shared organization results according to OmopDB command metadata."""

    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        """Initialize organization-scoped command metadata for OmopDB."""
        super().__init__(
            abac_service,
            **kwargs,
        )
        self.has_organization_id_attr_command_classes.update(set())
        self.has_user_id_attr_command_classes.update(set())
