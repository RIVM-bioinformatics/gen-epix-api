from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.commondb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp.user_manager import BaseUserManager as ServiceUserManager


class BaseUserManager(ServiceUserManager):
    DEFAULT_KEY_CLAIM = "__key__"

    DEFAULT_NAME_CLAIMS: list[str | list[str]] = [
        "name",
        ["first_name", "last_name"],
        "preferred_username",
        "preferredUsername",
        "username",
    ]

    def __init__(
        self,
        organization_service: BaseOrganizationService,
        rbac_service: BaseRbacService,
        root_cfg: dict[str, dict[str, str]],
        automatic_new_user_cfg: dict[str, dict[str, str]] | None = None,
        key_claim: str | None = None,
        name_claims: list[str | list[str]] | None = None,
    ):
        # Assign input properties
        self._organization_service = organization_service
        self._rbac_service = rbac_service
        self._key_claim = key_claim or self.DEFAULT_KEY_CLAIM
        self._name_claims = name_claims or self.DEFAULT_NAME_CLAIMS
