from typing import Any

from gen_epix.commondb.policies import \
    ReadOrganizationResultsOnlyPolicy as \
    CommonReadOrganizationResultsOnlyPolicy
from gen_epix.seqdb.domain.service import BaseAbacService


class ReadOrganizationResultsOnlyPolicy(CommonReadOrganizationResultsOnlyPolicy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            **kwargs,
        )
        self.has_organization_id_attr_command_classes.update(set())
        self.has_user_id_attr_command_classes.update(set())
