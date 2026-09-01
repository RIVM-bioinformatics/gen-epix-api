"""Provide the commondb user-manager contract for resolved identities.

The manager builds the root fallback user and optional automatically created
user defaults from application configuration and organization/RBAC services.
"""

from typing import Any
from uuid import UUID

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.commondb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import exc
from gen_epix.fastapp.user_manager import BaseUserManager as ServiceUserManager


class BaseUserManager(ServiceUserManager):
    """Resolve commondb users and validate root and automatic-user configuration."""

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
        """Initialize identity claim settings and user creation configuration.

        Args:
            organization_service: Service that retrieves commondb users.
            rbac_service: Service that supplies registered role values.
            user_class: Model used to represent resolved users.
            user_invitation_class: Model used to represent invitations.
            root_cfg: Required configuration for the root organization and user.
            auto_created_user_cfg: Optional defaults for automatically created users.
            key_claim: Identity-provider claim used as the user key.
            name_claims: Claims considered when resolving a display name.

        Raises:
            InitializationServiceError: If required root configuration is absent or invalid.
        """
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
                "835074f1", "Root configuration for user manager is not provided"
            )
        self.init_root_cfg(root_cfg)

        # Initialize automatic new user config
        self.init_auto_created_user_cfg(auto_created_user_cfg)

    def init_root_cfg(self, root_cfg: dict[str, dict[str, str]]) -> None:
        """Validate and construct the root organization and root user.

        Args:
            root_cfg: Configuration containing ``organization`` and ``user`` sections.

        Raises:
            InitializationServiceError: If required sections or the organization ID are
                missing.
        """
        # Check top level keys
        required_keys = {"organization", "user"}
        if not required_keys.issubset(root_cfg.keys()):
            missing_keys_str = ", ".join(sorted(required_keys - set(root_cfg.keys())))
            raise exc.InitializationServiceError(
                "7fc1f394",
                f"Root configuration is missing required keys: {missing_keys_str}",
            )
        # Create root organization instance
        self._root_organization = model.Organization(
            **root_cfg["organization"]  # type: ignore[arg-type]
        )
        if self._root_organization.id is None:
            raise exc.InitializationServiceError(
                "e72c66f9", "Root organization ID is not set in the configuration"
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
        """Validate optional defaults used to create previously unknown users.

        Args:
            auto_created_user_cfg: Role and organization defaults, or None to disable
                automatic user creation.

        Raises:
            InitializationServiceError: If required values are missing, roles are not
                registered, or the organization ID is invalid.
        """
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
                "386d8f64",
                f"Auto-created new user configuration is missing required keys: {missing_keys_str}",
            )
        ## Verify roles
        roles = set(auto_created_user_cfg["roles"])
        all_roles: set[str] = self._rbac_service.get_roles()  # type: ignore[assignment]
        if not roles.issubset(all_roles):
            extra_roles_str = ", ".join(sorted(roles - all_roles))
            raise exc.InitializationServiceError(
                "9a34d173",
                f"Auto-created new user configuration has extra roles not registered: {extra_roles_str}",
            )
        self._auto_created_user_cfg["roles"] = roles
        # Verify organization_id
        organization_id_str = auto_created_user_cfg["organization_id"]
        try:
            self._auto_created_user_cfg["organization_id"] = UUID(organization_id_str)
        except (ValueError, KeyError):
            raise exc.InitializationServiceError(
                "fb19c5c0",
                f"Auto-created new user configuration has invalid organization_id: {organization_id_str}",
            )
