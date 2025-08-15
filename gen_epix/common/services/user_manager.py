import datetime
from enum import Enum
from typing import Any, Type
from uuid import UUID

from gen_epix.common.domain import command, exc, model
from gen_epix.common.domain.service.organization import BaseOrganizationService
from gen_epix.common.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import (BaseUnitOfWork, BaseUserManager, CrudOperation,
                              Permission)
from gen_epix.fastapp.services.auth import get_email_from_claims


class UserManager(BaseUserManager):
    def __init__(
        self,
        user_class: Type[model.User],
        user_invitation_class: Type[model.UserInvitation],
        organization_service: BaseOrganizationService,
        rbac_service: BaseRbacService,
        root_cfg: dict[str, dict[str, str]],
        automatic_new_user_cfg: dict[str, dict[str, str]] | None = None,
    ):
        self._user_class = user_class
        self._user_invitation_class = user_invitation_class
        annotation: set[Enum] = user_class.model_fields["roles"].annotation  # type: ignore[assignment]
        self._role_enum: Type[Enum] = annotation.__args__[0]  # type: ignore[attr-defined]
        if "ROOT" not in self._role_enum._member_names_:
            raise exc.InitializationServiceError(
                "Root role is not defined in the user model"
            )
        self._root_role = self._role_enum["ROOT"]
        self._guest_role = self._role_enum["GUEST"]
        self._organization_service = organization_service
        self._rbac_service = rbac_service

        # Generate root model objs
        self._root: dict = {}
        self._root["organization"] = model.Organization(**root_cfg["organization"])  # type: ignore[arg-type]
        if self._root["organization"].id is None:
            raise exc.InitializationServiceError(
                "Root organization ID is not set in the configuration"
            )
        if "roles" not in root_cfg["user"]:
            root_cfg["user"]["roles"] = [self._root_role.name]
        self._root["user"] = self._user_class(
            is_active=True,
            organization_id=self._root["organization"].id,
            **root_cfg["user"],  # type: ignore[arg-type]
        )

        # Get automatic new user data
        self._automatic_new_user: dict[str, Any] | None = None
        if automatic_new_user_cfg:
            self._automatic_new_user = {}
            self._automatic_new_user["organization"] = dict(
                automatic_new_user_cfg["organization"]
            )
            self._automatic_new_user["roles"] = {
                self._role_enum[x] for x in automatic_new_user_cfg["roles"]
            }
            if "id" not in self._automatic_new_user["organization"]:
                raise exc.InitializationServiceError(
                    "Automatic new user organization ID is not set in the configuration"
                )
            self._automatic_new_user["organization"]["id"] = UUID(
                self._automatic_new_user["organization"]["id"]
            )

    def generate_id(self) -> UUID:
        return self._organization_service.generate_id()  # type: ignore[return-value]

    def get_user_key_from_claims(self, claims: dict[str, Any]) -> str | None:
        return get_email_from_claims(claims)

    def get_user_instance_from_claims(
        self, claims: dict[str, Any]
    ) -> model.User | None:
        if self._automatic_new_user is None:
            return None
        roles = (
            self._automatic_new_user["roles"]
            if self._automatic_new_user
            else {self._guest_role}
        )
        organization_id = (
            self._automatic_new_user["organization"]["id"]
            if self._automatic_new_user
            else self._root["organization"].id
        )
        email = get_email_from_claims(claims)
        if not email:
            raise exc.CredentialsAuthError("Email not found in claims")
        return self._user_class(
            email=email,
            is_active=True,
            roles=roles,
            organization_id=organization_id,
        )

    def is_root_user(self, claims: dict[str, Any]) -> bool:
        user: model.User = self._root["user"]
        return user.email == get_email_from_claims(claims)

    def create_root_user_from_claims(self, claims: dict[str, Any]) -> model.User:  # type: ignore
        assert self._organization_service.repository
        with self._organization_service.repository.uow() as uow:
            # Create root organization if necessary

            is_existing_organization = self._organization_service.repository.crud(
                uow,
                None,
                model.Organization,
                None,
                self._root["organization"].id,
                CrudOperation.EXISTS_ONE,
            )
            if not is_existing_organization:
                _ = self._organization_service.repository.crud(
                    uow,
                    None,
                    model.Organization,
                    self._root["organization"],
                    None,
                    CrudOperation.CREATE_ONE,
                )

            # Create root user if necessary
            is_existing_root_user = self._organization_service.repository.crud(
                uow,
                None,
                self._user_class,
                None,
                self._root["user"].id,
                CrudOperation.EXISTS_ONE,
            )
            user: model.User
            if is_existing_root_user:
                user = self._organization_service.repository.crud(  # type:ignore[assignment]
                    uow,
                    None,
                    self._user_class,
                    None,
                    self._root["user"].id,
                    CrudOperation.READ_ONE,
                )
                is_updated = False
                for key, value in claims.items():
                    if not hasattr(user, key) or getattr(user, key) == value:
                        continue
                    is_updated = True
                    if key == "organization_id":
                        user.organization_id = self._root["organization"].id
                    elif key == "roles":
                        user.roles.update(value)
                    else:
                        setattr(user, key, value)
                if self._root_role not in user.roles:
                    is_updated = True
                    user.roles.add(self._root_role)
                if is_updated:
                    user = self._organization_service.repository.crud(  # type:ignore[assignment]
                        uow,
                        self._root["user"].id,
                        self._user_class,
                        user,
                        None,
                        CrudOperation.UPDATE_ONE,
                    )
            else:
                user = self._organization_service.repository.crud(  # type:ignore[assignment]
                    uow,
                    self._root["user"].id,
                    self._user_class,
                    self._root["user"],
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
                    uow, get_email_from_claims(claims)
                )
            )
            if is_existing_user:
                raise exc.ServiceException(
                    f"User with key {get_email_from_claims(claims)} already exists"
                )
            claims_user = self.get_user_instance_from_claims(claims)
            if not claims_user:
                raise exc.ServiceException(
                    f"Unable to create user with key {get_email_from_claims(claims)} from claims"
                )
            claims_user.id = self.generate_id()
            user: model.User = (
                self._organization_service.repository.crud(  # type:ignore[assignment]
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
            timestamp = datetime.datetime.now()
            user_invitations: list[self.user_invitation_class] = ( # pyright: ignore[reportInvalidTypeForm]
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
                and x.email == user.email
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
                created_user: model.User = self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    created_by_user_id,
                    self._user_class,
                    self._user_class(
                        **(user.model_dump() | {"id": self.generate_id()})
                    ),
                    None,
                    CrudOperation.CREATE_ONE,
                )
            except:
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
            user: model.User = self._organization_service.repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
                self._user_class,
                None,
                user_id,
                CrudOperation.READ_ONE,
            )
        return user

    def retrieve_user_permissions(self, user: model.User) -> set[Permission]:  # type: ignore[override]
        return self._rbac_service.retrieve_user_permissions(user)
