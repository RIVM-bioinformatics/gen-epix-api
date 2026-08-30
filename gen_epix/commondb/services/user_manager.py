"""Implement commondb identity resolution, root bootstrap, and user provisioning."""

import datetime
from typing import Any
from uuid import UUID

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import exc, model
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.service import (
    BaseOrganizationService,
    BaseRbacService,
    BaseUserManager,
)
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation, Permission
from gen_epix.fastapp.services.auth import get_email_from_claims
from gen_epix.fastapp.services.auth.util import get_name_from_claims
from gen_epix.util import str_to_uuid


class UserManager(BaseUserManager):
    """Resolve authenticated users and create root, invited, and automatic users."""

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
        auto_created_user_cfg: dict[str, str] | None = None,
        key_claim: str | None = None,
        name_claims: list[str | list[str]] | None = None,
    ):
        """Initialize mapped commondb user models and identity claim configuration.

        Args:
            organization_service: Service that persists organizations and users.
            rbac_service: Service that resolves configured role values.
            root_cfg: Required root organization and user configuration.
            auto_created_user_cfg: Optional defaults for automatic user provisioning.
            key_claim: Identity claim used as the user key.
            name_claims: Claims used to resolve user display names.

        Raises:
            InitializationServiceError: If root or automatic-user configuration is
                incomplete or invalid.
        """
        # Derive some properties
        app_impl: AppImplDetails = organization_service.app.impl
        user_class: type[model.User] = app_impl.get_mapped_class(model.User)
        user_invitation_class: type[model.UserInvitation] = app_impl.get_mapped_class(
            model.UserInvitation
        )

        # Initialize through parent constructor
        super().__init__(
            organization_service,
            rbac_service,
            user_class=user_class,
            user_invitation_class=user_invitation_class,
            root_cfg=root_cfg,
            auto_created_user_cfg=auto_created_user_cfg,
            key_claim=key_claim,
            name_claims=name_claims,
        )

    def generate_id(self) -> UUID:
        """Generate an ID through the organization service.

        Returns:
            New user identifier.
        """
        return self._organization_service.generate_id()  # type: ignore[return-value]

    def get_user_key_from_claims(self, claims: dict[str, Any]) -> str | None:
        """Retrieve the configured user-key claim from identity claims.

        Args:
            claims: Authenticated identity-provider claims.

        Returns:
            Claim value when present; otherwise None.
        """
        return claims.get(self._key_claim)

    def get_user_name_from_claims(self, claims: dict[str, Any]) -> str | None:
        """Resolve a display name from configured identity-provider claims.

        Args:
            claims: Authenticated identity-provider claims.

        Returns:
            Resolved display name when available; otherwise None.
        """
        return get_name_from_claims(claims, self._name_claims)

    def construct_user_instance_from_claims(
        self, claims: dict[str, Any]
    ) -> model.User | None:
        """Construct a user from claims and configured automatic-user defaults.

        Args:
            claims: Authenticated identity-provider claims.

        Returns:
            New user model, or None when no model can be constructed.

        Raises:
            CredentialsAuthError: If the configured key claim is absent or empty.
        """
        if self._auto_created_user_cfg is None:
            # No auto-created user config provided, set dummy roles and organization ID for the created user since they are mandatory, and which should be overridden by the calling function
            roles = {self._rbac_service.guest_role}
            organization_id = NULL_ID
        else:
            # Auto-created user config provided, get roles and organization ID from the config
            roles = self._auto_created_user_cfg["roles"]
            organization_id = self._auto_created_user_cfg["organization_id"]
        key = claims.get(self._key_claim)
        if not key:
            raise exc.CredentialsAuthError("89778b52", "Key not found in claims")
        email = get_email_from_claims(claims)
        name = self.get_user_name_from_claims(claims)
        return self._user_class(
            key=key,
            email=email,
            name=name,
            is_active=True,
            roles=roles,
            organization_id=organization_id,
        )

    def is_root_user_claims(self, claims: dict[str, Any]) -> bool:
        """Determine whether identity claims belong to the configured root user.

        Args:
            claims: Authenticated identity-provider claims.

        Returns:
            True when the configured key claim matches the root user key.
        """
        return self._root_user.key == claims.get(self._key_claim)

    def is_root_user(self, user: model.User) -> bool:  # type: ignore[override]
        """Determine whether a user has the configured root role.

        Args:
            user: User whose assigned roles are evaluated.

        Returns:
            True when the user has the root role; otherwise False.
        """
        return self._rbac_service.root_role in user.roles

    def create_root_user_from_claims(self, claims: dict[str, Any]) -> model.User:
        """Create or retrieve the configured root organization and user.

        The operation is idempotent to support services sharing a commondb database,
        including NONE IDP mode where claims may be empty.

        Args:
            claims: Identity claims used for root user name and email fields.

        Returns:
            Existing or newly persisted root user.
        """
        assert self._organization_service.repository

        # Handle transactions
        with self._organization_service.repository.uow() as uow:
            # Create root organization if necessary
            cfg_root_organization: model.Organization = self._root_organization
            is_existing_organization: bool = self._organization_service.repository.crud(
                uow,
                None,
                model.Organization,
                CrudOperation.EXISTS_ONE,
                obj_ids=cfg_root_organization.id,
            )
            if not is_existing_organization:
                _ = self._organization_service.repository.crud(
                    uow,
                    None,
                    model.Organization,
                    CrudOperation.CREATE_ONE,
                    objs=cfg_root_organization,
                )

            # Create root user if not already present, otherwise return it.
            # The lookup uses self._root_user.key (the configured key) rather
            # than claims.get(self._key_claim), because NONE IDP mode calls
            # this method with empty claims ({}), making the claim-based lookup
            # always return None and the existence check always return False —
            # a silent bug that causes a UniqueConstraintViolationError on the
            # subsequent INSERT. Using the configured key fixes the check.
            # Returning the existing user (instead of raising) makes this call
            # idempotent, which is required when multiple services share a
            # database: e.g. in SA_SQL mode the standalone seqdb service and
            # casedb's embedded LOCAL seqdb both initialise against the same
            # seqdb database and both call this method on startup.
            is_existing_root_user = (
                self._organization_service.repository.is_existing_user_by_key(
                    uow, self._root_user.key
                )
            )
            if is_existing_root_user:
                return self._organization_service.repository.retrieve_user_by_key(
                    uow, self._root_user.key
                )
            # Create and store root user
            root_user = self._root_user.model_copy()
            root_user.id = root_user.id or str_to_uuid(root_user.key)
            root_user.email = get_email_from_claims(claims)
            root_user.name = self.get_user_name_from_claims(claims)
            user: model.User = self._organization_service.repository.crud(
                uow,
                root_user.id,
                self._user_class,
                CrudOperation.CREATE_ONE,
                objs=root_user,
            )

        return user

    def auto_create_new_user(self, claims: dict[str, Any]) -> model.User | None:
        """Create a user from configured defaults when automatic provisioning is enabled.

        Args:
            claims: Authenticated identity-provider claims for the new user.

        Returns:
            Newly persisted user, or None when automatic provisioning is disabled.

        Raises:
            InitializationServiceError: If the configured target organization is absent.
            ServiceException: If the user exists or cannot be constructed from claims.
            CredentialsAuthError: If the configured key claim is absent or empty.
        """
        if self._auto_created_user_cfg is None:
            return None
        assert self._organization_service.repository
        organization_id = self._auto_created_user_cfg["organization_id"]
        with self._organization_service.repository.uow() as uow:
            # Verify if organization exists
            is_existing_organization: bool = self._organization_service.repository.crud(
                uow,
                None,
                model.Organization,
                CrudOperation.EXISTS_ONE,
                obj_ids=organization_id,
            )
            if not is_existing_organization:
                if organization_id == self._root_organization.id:
                    # auto create the organization for the root user if it does not exist
                    self._organization_service.repository.crud(
                        uow,
                        None,
                        model.Organization,
                        CrudOperation.CREATE_ONE,
                        objs=self._root_organization,
                    )
                else:
                    raise exc.InitializationServiceError(
                        "26baf193", "Auto-created new user organization does not exist"
                    )

            # Verify if user exists and add if not
            # TODO: refactor this to add a separate method for a potential existing user
            is_existing_user = (
                self._organization_service.repository.is_existing_user_by_key(
                    uow, claims.get(self._key_claim)
                )
            )
            if is_existing_user:
                raise exc.ServiceException(
                    "98a3327c",
                    f"User with key {claims.get(self._key_claim)} already exists",
                )
            claims_user = self.construct_user_instance_from_claims(claims)
            if not claims_user:
                raise exc.ServiceException(
                    "2eb471f8",
                    f"Unable to auto-create user with key {claims.get(self._key_claim)} from claims",
                )
            claims_user.id = self.generate_id()
            user: model.User = self._organization_service.repository.crud(
                uow,
                claims_user.id,
                self._user_class,
                CrudOperation.CREATE_ONE,
                objs=claims_user,
            )

        return user

    def create_new_user_from_token(  # type: ignore[override]
        self, user: model.User, token: str, **kwargs: Any
    ) -> model.User:
        """Create an invited user after validating inviter, token, and organization.

        Args:
            user: User model supplied during invitation registration.
            token: Invitation token that authorizes registration.
            **kwargs: Requires ``created_by_user_id`` for the invitation issuer.

        Returns:
            Newly persisted user.

        Raises:
            UnauthorizedAuthError: If the inviter, invitation, organization, or new
                user is invalid, or persistence cannot create the user.
        """
        assert self._organization_service.repository
        created_by_user_id: UUID = kwargs["created_by_user_id"]

        with self._organization_service.repository.uow() as uow:
            # Verify if create_by_user exists and is active
            is_existing_user: bool = self._organization_service.repository.crud(
                uow,
                None,
                self._user_class,
                CrudOperation.EXISTS_ONE,
                obj_ids=created_by_user_id,
            )
            if not is_existing_user:
                raise exc.UnauthorizedAuthError(
                    "d9c42047", "Created by user does not exist"
                )
            created_by_user = self.retrieve_user_by_id(created_by_user_id)
            if not created_by_user.is_active:
                raise exc.UnauthorizedAuthError(
                    "16a88680", "Created by user is not active"
                )

            # Verify if create_by_user made an invitation for this user that is valid
            user_invitations: list[model.UserInvitation] = (
                self._organization_service.repository.crud(
                    uow,
                    created_by_user_id,
                    self._user_invitation_class,
                    CrudOperation.READ_ALL,
                )
            )

            def convert_to_utc(x: datetime.datetime) -> datetime.datetime:
                """Normalize an invitation expiration timestamp to UTC.

                Args:
                    x: Naive or timezone-aware timestamp to normalize.

                Returns:
                    Timestamp expressed with the UTC timezone.
                """
                if x.tzinfo is None:
                    return x.replace(tzinfo=datetime.timezone.utc)
                return x.astimezone(datetime.timezone.utc)

            timestamp = datetime.datetime.now(datetime.timezone.utc)

            # At least one invitation exists matching the criteria
            user_invitations = [
                x
                for x in user_invitations
                if x.invited_by_user_id == created_by_user_id
                and x.token == token
                and (x.key is None or x.key == user.get_key())
                and x.organization_id == user.organization_id
                and convert_to_utc(x.expires_at) > timestamp
            ]
            if not user_invitations:
                raise exc.UnauthorizedAuthError("edc14ebd", "Invitation does not exist")

            # Verify if organization exists
            is_existing_organization: bool = self._organization_service.repository.crud(
                uow,
                None,
                model.Organization,
                CrudOperation.EXISTS_ONE,
                obj_ids=user.organization_id,
            )
            if not is_existing_organization:
                raise exc.UnauthorizedAuthError(
                    "c14b47ee", "Organization does not exist"
                )

            is_existing_user = self.is_existing_user_by_key(user.email, uow)
            if is_existing_user:
                raise exc.UnauthorizedAuthError("00133e20", "User already exists")

            try:
                created_user: model.User = self._organization_service.repository.crud(
                    uow,
                    created_by_user_id,
                    self._user_class,
                    CrudOperation.CREATE_ONE,
                    objs=self._user_class(
                        **(user.model_dump() | {"id": self.generate_id()})
                    ),
                )
            except Exception:
                raise exc.UnauthorizedAuthError("28217e8d", "Unable to create user")

            return created_user

    def is_existing_user_by_key(
        self, user_key: str | None, uow: BaseUnitOfWork
    ) -> bool:
        """Determine whether a normalized user key already exists.

        Args:
            user_key: Candidate user key, or None when no key is available.
            uow: Active unit of work for the lookup.

        Returns:
            True when a user exists for the key; otherwise False.
        """
        return self._organization_service.repository.is_existing_user_by_key(
            uow, user_key
        )

    def retrieve_user_by_key(self, user_key: str) -> model.User:
        """Retrieve a commondb user by normalized key.

        Args:
            user_key: User key to resolve.

        Returns:
            Matching user.
        """
        return self._organization_service.retrieve_user_by_key(user_key)

    def retrieve_user_by_id(self, user_id: UUID) -> model.User:  # type: ignore[override]
        """Retrieve a commondb user by ID.

        Args:
            user_id: ID of the user to retrieve.

        Returns:
            Matching persisted user.
        """
        with self._organization_service.repository.uow() as uow:
            user: model.User = self._organization_service.repository.crud(
                uow,
                user_id,
                self._user_class,
                CrudOperation.READ_ONE,
                obj_ids=user_id,
            )
        return user

    def update_user_name(  # type: ignore[override]
        self, user: model.User, new_name: str
    ) -> model.User | None:
        """Update an active user's display name when it has changed.

        Args:
            user: User to update.
            new_name: Replacement display name.

        Returns:
            Original or updated user, or None when the user is inactive.
        """
        if user.name == new_name:
            return user
        if user.is_active is False:
            return None
        user.name = new_name
        with self._organization_service.repository.uow() as uow:
            updated_user: model.User = self._organization_service.repository.crud(
                uow,
                user.id,
                self._user_class,
                CrudOperation.UPDATE_ONE,
                objs=user,
            )
        return updated_user

    def retrieve_user_permissions(  # type: ignore[override]
        self, user: model.User
    ) -> set[Permission]:
        """Retrieve effective permissions through the commondb RBAC service.

        Args:
            user: User whose permissions are requested.

        Returns:
            Effective permissions assigned through the RBAC service.
        """
        return self._rbac_service.retrieve_user_permissions(user)
