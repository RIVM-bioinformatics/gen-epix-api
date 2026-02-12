import datetime
from typing import Any
from uuid import UUID

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, exc, model
from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.commondb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import BaseUnitOfWork, BaseUserManager, CrudOperation, Permission
from gen_epix.fastapp.services.auth import get_email_from_claims
from gen_epix.fastapp.services.auth.util import get_name_from_claims


class UserManager(BaseUserManager):
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

        # Derive some properties
        app_impl: AppImplDetails = organization_service.app.impl
        self._user_class: type[model.User] = app_impl.get_mapped_class(model.User)
        self._user_invitation_class: type[model.UserInvitation] = (
            app_impl.get_mapped_class(model.UserInvitation)
        )

        # Generate root organization and user objects
        self._root_organization = model.Organization(
            **root_cfg["organization"]  # type: ignore[arg-type]
        )
        if self._root_organization.id is None:
            raise exc.InitializationServiceError(
                "Root organization ID is not set in the configuration"
            )
        self._root_user = self._user_class(
            is_active=True,
            organization_id=self._root_organization.id,
            roles={self._rbac_service.root_role},
            **root_cfg["user"],  # type: ignore[arg-type]
        )

        # Get automatic new user data
        self._automatic_new_user: dict[str, Any] | None = None
        if automatic_new_user_cfg:
            self._automatic_new_user = {}
            self._automatic_new_user["organization"] = dict(
                automatic_new_user_cfg["organization"]
            )
            self._automatic_new_user["roles"] = set(automatic_new_user_cfg["roles"])
            if "id" not in self._automatic_new_user["organization"]:
                raise exc.InitializationServiceError(
                    "Automatic new user organization ID is not set in the configuration"
                )
            # fmt:off
            self._automatic_new_user["organization"]["id"] = (  # pyright:ignore[reportArgumentType]
                UUID(  
                    self._automatic_new_user["organization"]["id"]
                )
            )
            # fmt:on

    def generate_id(self) -> UUID:
        return self._organization_service.generate_id()  # type: ignore[return-value]

    def get_user_key_from_claims(self, claims: dict[str, Any]) -> str | None:
        return claims.get(self._key_claim)

    def get_user_name_from_claims(self, claims: dict[str, Any]) -> str | None:
        return get_name_from_claims(claims, self._name_claims)

    def get_user_instance_from_claims(
        self, claims: dict[str, Any]
    ) -> model.User | None:
        if self._automatic_new_user is None:
            return None
        roles = (
            self._automatic_new_user["roles"]
            if self._automatic_new_user
            else {self._rbac_service.guest_role}
        )
        organization_id = (
            self._automatic_new_user["organization"]["id"]
            if self._automatic_new_user
            else self._root_organization.id
        )
        key = claims.get(self._key_claim)
        if not key:
            raise exc.CredentialsAuthError("Key not found in claims")
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
        return self._root_user.key == claims.get(self._key_claim)

    def is_root_user(self, user: model.User) -> bool:  # type: ignore[override]
        return self._rbac_service.root_role in user.roles

    def create_root_user_from_claims(self, claims: dict[str, Any]) -> model.User:
        assert self._organization_service.repository

        # Handle transactions
        with self._organization_service.repository.uow() as uow:
            # Create root organization if necessary
            cfg_root_organization: model.Organization = self._root_organization
            is_existing_organization = self._organization_service.repository.crud(
                uow,
                None,
                model.Organization,
                None,
                cfg_root_organization.id,
                CrudOperation.EXISTS_ONE,
            )
            if not is_existing_organization:
                _ = self._organization_service.repository.crud(
                    uow,
                    None,
                    model.Organization,
                    cfg_root_organization,
                    None,
                    CrudOperation.CREATE_ONE,
                )

            # Create root user (or retrieve if already exists)
            user_key = claims.get(self._key_claim)
            is_existing_root_user = (
                self._organization_service.repository.is_existing_user_by_key(
                    uow, user_key
                )
            )
            if is_existing_root_user:
                # Root user already exists (e.g., from demo data), retrieve it
                user: model.User = (
                    self._organization_service.repository.retrieve_user_by_key(
                        uow, user_key
                    )
                )
            else:
                # Create and store root user
                root_user = self._root_user.model_copy()
                root_user.id = (
                    self._organization_service.generate_id()
                )  # type: ignore[assignment]
                root_user.email = get_email_from_claims(claims)
                root_user.name = self.get_user_name_from_claims(claims)
                user = self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    root_user.id,
                    self._user_class,
                    root_user,
                    None,
                    CrudOperation.CREATE_ONE,
                )

        return user

    def create_user_from_claims(self, claims: dict[str, Any]) -> model.User | None:
        if self._automatic_new_user is None:
            return None
        assert self._organization_service.repository
        organization_id = self._automatic_new_user["organization"]["id"]
        with self._organization_service.repository.uow() as uow:
            # Verify if organization exists
            is_existing_organization = self._organization_service.repository.crud(
                uow,
                None,
                model.Organization,
                None,
                organization_id,
                CrudOperation.EXISTS_ONE,
            )
            if not is_existing_organization:
                raise exc.InitializationServiceError(
                    "Automatic new user organization does not exist"
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
                    f"User with key {claims.get(self._key_claim)} already exists"
                )
            claims_user = self.get_user_instance_from_claims(claims)
            if not claims_user:
                raise exc.ServiceException(
                    f"Unable to create user with key {claims.get(self._key_claim)} from claims"
                )
            claims_user.id = self.generate_id()
            user: model.User = (
                self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    claims_user.id,
                    self._user_class,
                    claims_user,
                    None,
                    CrudOperation.CREATE_ONE,
                )
            )

            # Add user case policies by calling switching organization method
            try:
                user = self._organization_service.app.handle(
                    command.UpdateUserOwnOrganizationCommand(
                        user=user,
                        organization_id=user.organization_id,
                        is_new_user=True,
                    ),
                )
            except Exception as exception:
                raise exc.UnauthorizedAuthError("Unable to add user case policies")

        return user

    def create_new_user_from_token(  # type: ignore[override]
        self, user: model.User, token: str, **kwargs: Any
    ) -> model.User:
        assert self._organization_service.repository
        created_by_user_id: UUID = kwargs["created_by_user_id"]

        with self._organization_service.repository.uow() as uow:
            # Verify if create_by_user exists and is active
            is_existing_user = self._organization_service.repository.crud(
                uow,
                None,
                self._user_class,
                None,
                created_by_user_id,
                CrudOperation.EXISTS_ONE,
            )
            if not is_existing_user:
                raise exc.UnauthorizedAuthError("Created by user does not exist")
            created_by_user = self.retrieve_user_by_id(created_by_user_id)
            if not created_by_user.is_active:
                raise exc.UnauthorizedAuthError("Created by user is not active")

            # Verify if create_by_user made an invitation for this user that is valid
            timestamp = datetime.datetime.now(datetime.timezone.utc)
            user_invitations: list[model.UserInvitation] = (
                self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    created_by_user_id,
                    self._user_invitation_class,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                )
            )

            # At least one invitation exists matching the criteria
            user_invitations = [
                x
                for x in user_invitations
                if x.invited_by_user_id == created_by_user_id
                and x.token == token
                and x.key == user.key
                and x.organization_id == user.organization_id
                and x.expires_at > timestamp
            ]
            if not user_invitations:
                raise exc.UnauthorizedAuthError("Invitation does not exist")

            # Verify if organization exists
            is_existing_organization = self._organization_service.repository.crud(
                uow,
                None,
                model.Organization,
                None,
                user.organization_id,
                CrudOperation.EXISTS_ONE,
            )
            if not is_existing_organization:
                raise exc.UnauthorizedAuthError("Organization does not exist")

            is_existing_user = self.is_existing_user_by_key(user.email, uow)
            if is_existing_user:
                raise exc.UnauthorizedAuthError("User already exists")

            try:
                created_user: model.User = (
                    self._organization_service.repository.crud(  # type: ignore[assignment]
                        uow,
                        created_by_user_id,
                        self._user_class,
                        self._user_class(
                            **(user.model_dump() | {"id": self.generate_id()})
                        ),
                        None,
                        CrudOperation.CREATE_ONE,
                    )
                )
            except Exception:
                raise exc.UnauthorizedAuthError("Unable to create user")

            return created_user

    def is_existing_user_by_key(
        self, user_key: str | None, uow: BaseUnitOfWork
    ) -> bool:
        return self._organization_service.repository.is_existing_user_by_key(
            uow, user_key
        )

    def retrieve_user_by_key(self, user_key: str) -> model.User:
        return self._organization_service.retrieve_user_by_key(user_key)

    def retrieve_user_by_id(self, user_id: UUID) -> model.User:  # type: ignore[override]
        with self._organization_service.repository.uow() as uow:
            user: model.User = (
                self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id,
                    self._user_class,
                    None,
                    user_id,
                    CrudOperation.READ_ONE,
                )
            )
        return user

    def update_user_name(  # type: ignore[override]
        self, user: model.User, new_name: str
    ) -> model.User | None:
        if user.name == new_name:
            return user
        user.name = new_name
        with self._organization_service.repository.uow() as uow:
            updated_user: model.User = (
                self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    self._user_class,
                    user,
                    None,
                    CrudOperation.UPDATE_ONE,
                )
            )
        return updated_user

    def retrieve_user_permissions(  # type: ignore[override]
        self, user: model.User
    ) -> set[Permission]:
        return self._rbac_service.retrieve_user_permissions(user)
