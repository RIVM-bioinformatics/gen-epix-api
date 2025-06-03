from gen_epix.fastapp.model import Policy
from gen_epix.seqdb.domain.service.organization import BaseOrganizationService
from gen_epix.seqdb.domain.service.rbac import BaseRbacService


class BaseUpdateUserPolicy(Policy):
    def __init__(
        self,
        rbac_service: BaseRbacService,
        organization_service: BaseOrganizationService,
        **kwargs: dict,
    ):
        self.rbac_service = rbac_service
        self.organization_service = organization_service
        self.props = kwargs
