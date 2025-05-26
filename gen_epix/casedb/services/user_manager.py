import datetime
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.service.organization import BaseOrganizationService
from gen_epix.casedb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import BaseUnitOfWork, BaseUserManager, CrudOperation, Permission
from gen_epix.fastapp.services.auth import get_email_from_claims


class UserManager(BaseUserManager):
    def __init__(
        self,
        organization_service: BaseOrganizationService,
        rbac_service: BaseRbacService,
        root_cfg: dict[str, dict[str, str]],
        automatic_new_user_cfg: dict[str, dict[str, str]] | None = None,
    ):
        self._organization_service: BaseOrganizationService = organization_service
        self._rbac_service: BaseRbacService = rbac_service

        # Generate root model objs
        self._root: dict = {}
        self._root["organization"] = model.Organization(**root_cfg["organization"])  # type: ignore[arg-type]
        self._root["user"] = model.User(
            is_active=True,
            organization_id=self._root["organization"].id,
            **root_cfg["user"],  # type: ignore[arg-type]
        )
        self._root["user"].roles.add(enum.Role.ROOT)

        # Get automatic new user data
        self._automatic_new_user: dict | None = None
        if automatic_new_user_cfg:
            self._automatic_new_user = {}
            self._automatic_new_user["roles"] = {
                enum.Role[x] for x in automatic_new_user_cfg["roles"]
            }
            self._automatic_new_user["organization"] = {
                **automatic_new_user_cfg["organization"]
            }
            self._automatic_new_user["organization"]["id"] = UUID(
                self._automatic_new_user["organization"]["id"]
            )

    def generate_id(self) -> UUID:
        return self._organization_service.generate_id()  # type: ignore[return-value]

    def get_user_key_from_claims(self, claims: dict[str, Any]) -> str | None:
        return get_email_from_claims(claims)

    def get_user_instance_from_claims(  # type: ignore[override]
        self, claims: dict[str, Any]
    ) -> model.User | None:
        if self._automatic_new_user is None:
            return None
        roles = (
            self._automatic_new_user["roles"]
            if self._automatic_new_user
            else {enum.Role.GUEST}
        )
        organization_id = (
            self._automatic_new_user["organization"]["id"]
            if self._automatic_new_user
            else self._root["organization"].id
        )
        email = get_email_from_claims(claims)
        if not email:
            raise exc.CredentialsAuthError("Email not found in claims")
        return model.User(
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
                model.User,
                None,
                self._root["user"].id,
                CrudOperation.EXISTS_ONE,
            )
            user: model.User
            if is_existing_root_user:
                user = self._organization_service.repository.crud(  # type:ignore[assignment]
                    uow,
                    None,
                    model.User,
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
                if enum.Role.ROOT not in user.roles:
                    is_updated = True
                    user.roles.add(enum.Role.ROOT)
                if is_updated:
                    role = self._organization_service.repository.crud(
                        uow,
                        self._root["user"].id,
                        model.User,
                        user,
                        None,
                        CrudOperation.UPDATE_ONE,
                    )
            else:
                user = self._organization_service.repository.crud(  # type:ignore[assignment]
                    uow,
                    self._root["user"].id,
                    model.User,
                    self._root["user"],
                    None,
                    CrudOperation.CREATE_ONE,
                )

        return user

    def create_user_from_claims(self, claims: dict[str, Any]) -> model.User | None:  # type: ignore[override]
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
            if not is_existing_user:
                claims_user = self.get_user_instance_from_claims(claims)
                if not claims_user:
                    raise exc.InitializationServiceError(
                        "Unable to create user from claims"
                    )
                claims_user.id = self.generate_id()
                user: model.User = (
                    self._organization_service.repository.crud(  # type:ignore[assignment]
                        uow,
                        claims_user.id,
                        model.User,
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
        self, new_user: model.User, token: str, **kwargs: dict
    ) -> model.User:
        assert self._organization_service.repository
        created_by_user_id: UUID = kwargs["created_by_user_id"]  # type: ignore[assignment]
        with self._organization_service.repository.uow() as uow:
            # Verify if create_by_user exists and is active
            is_existing_user = self._organization_service.repository.crud(
                uow,
                None,
                model.User,
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
            user_invitations: list[model.UserInvitation] = (
                self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    created_by_user_id,
                    model.UserInvitation,
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
                and x.email == new_user.email
                and x.organization_id == new_user.organization_id
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
                new_user.organization_id,
                CrudOperation.EXISTS_ONE,
            )
            if not is_existing_organization:
                raise exc.UnauthorizedAuthError("Organization does not exist")

            is_existing_user = self.is_existing_user_by_key(new_user.email, uow)
            if is_existing_user:
                raise exc.UnauthorizedAuthError("User already exists")

            try:
                user: model.User = (
                    self._organization_service.repository.crud(  # type:ignore[assignment]
                        uow,
                        created_by_user_id,
                        model.User,
                        model.User(
                            **(new_user.model_dump() | {"id": self.generate_id()})
                        ),
                        None,
                        CrudOperation.CREATE_ONE,
                    )
                )
            except:
                raise exc.UnauthorizedAuthError("Unable to create user")

            return user

    def is_existing_user_by_key(
        self, user_key: str | None, uow: BaseUnitOfWork
    ) -> bool:
        return self._organization_service.repository.is_existing_user_by_key(
            uow, user_key
        )

    def retrieve_user_by_key(self, user_key: str) -> model.User:  # type: ignore[override]
        return self._organization_service.retrieve_user_by_key(user_key)

    def retrieve_user_by_id(self, user_id: UUID) -> model.User:  # type: ignore[override]
        user: model.User = self._organization_service.app.handle(
            command.UserCrudCommand(
                user=self._root["user"],
                objs=None,
                obj_ids=user_id,
                operation=CrudOperation.READ_ONE,
            )
        )
        return user

    def retrieve_user_permissions(self, user: model.User) -> set[Permission]:  # type: ignore[override]
        return self._rbac_service.retrieve_user_permissions(user)  # type: ignore[arg-type]
