from typing import Any
from uuid import UUID

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.commondb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import exc
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
        user_class: type[model.User] = model.User,
        user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
        root_cfg: dict[str, dict[str, str]] | None = None,
        auto_created_user_cfg: dict[str, str] | None = None,
        key_claim: str | None = None,
        name_claims: list[str | list[str]] | None = None,
    ):
        # Assign input properties
        self._organization_service = organization_service
        self._rbac_service = rbac_service
        self._user_class = user_class
        self._user_invitation_class = user_invitation_class
        self._key_claim = key_claim or self.DEFAULT_KEY_CLAIM
        self._name_claims = name_claims or self.DEFAULT_NAME_CLAIMS

        # Initialize root config
        if root_cfg is None:
            raise exc.InitializationServiceError(
                "Root configuration for user manager is not provided"
            )
        self.init_root_cfg(root_cfg)

        # Initialize automatic new user config
        self.init_auto_created_user_cfg(auto_created_user_cfg)

    def init_root_cfg(self, root_cfg: dict[str, dict[str, str]]) -> None:
        # Check top level keys
        required_keys = {"organization", "user"}
        if not required_keys.issubset(root_cfg.keys()):
            missing_keys_str = ", ".join(sorted(required_keys - set(root_cfg.keys())))
            raise exc.InitializationServiceError(
                f"Root configuration is missing required keys: {missing_keys_str}"
            )
        # Create root organization instance
        self._root_organization = model.Organization(
            **root_cfg["organization"]  # type: ignore[arg-type]
        )
        if self._root_organization.id is None:
            raise exc.InitializationServiceError(
                "Root organization ID is not set in the configuration"
            )
        # Create root user instance
        self._root_user = self._user_class(
            is_active=True,
            organization_id=self._root_organization.id,
            roles={self._rbac_service.root_role},
            **root_cfg["user"],  # type: ignore[arg-type]
        )

    def init_auto_created_user_cfg(
        self, auto_created_user_cfg: dict[str, str] | None
    ) -> None:
        self._auto_created_user_cfg: dict[str, Any] | None = None
        if not auto_created_user_cfg:
            # No configuration provided, so automatic new user creation is disabled
            return

        self._auto_created_user_cfg = {}
        # Verify top level keys
        required_keys = {"roles", "organization_id"}
        if not required_keys.issubset(auto_created_user_cfg.keys()):
            missing_keys_str = ", ".join(
                sorted(required_keys - set(auto_created_user_cfg.keys()))
            )
            raise exc.InitializationServiceError(
                f"Auto-created new user configuration is missing required keys: {missing_keys_str}"
            )
        ## Verify roles
        roles = set(auto_created_user_cfg["roles"])
        all_roles: set[str] = self._rbac_service.get_roles()  # type: ignore[assignment]
        if not roles.issubset(all_roles):
            extra_roles_str = ", ".join(sorted(roles - all_roles))
            raise exc.InitializationServiceError(
                f"Auto-created new user configuration has extra roles not registered: {extra_roles_str}"
            )
        self._auto_created_user_cfg["roles"] = roles
        # Verify organization_id
        organization_id_str = auto_created_user_cfg["organization_id"]
        try:
            self._auto_created_user_cfg["organization_id"] = UUID(organization_id_str)
        except (ValueError, KeyError):
            raise exc.InitializationServiceError(
                f"Auto-created new user configuration has invalid organization_id: {organization_id_str}"
            )
