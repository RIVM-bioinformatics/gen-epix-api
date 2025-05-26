import datetime
from typing import Any
from uuid import UUID

from gen_epix.fastapp import BaseUnitOfWork, BaseUserManager, CrudOperation, Permission
from gen_epix.fastapp.services.auth import get_email_from_claims
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.repository.organization import BaseOrganizationRepository
from gen_epix.seqdb.domain.service.organization import BaseOrganizationService
from gen_epix.seqdb.domain.service.rbac import BaseRbacService


class UserManager(BaseUserManager):
    def __init__(
        self,
        organization_service: BaseOrganizationService,
        rbac_service: BaseRbacService,
        root_cfg: dict[str, dict[str, str]],
        automatic_new_user_cfg: dict[str, dict[str, str]] | None = None,
    ):
        self._organization_service = organization_service
        self._rbac_service = rbac_service

        # Generate root model objs
        self._root = {}
        self._root["user"] = model.User(is_active=True, **root_cfg["user"])  # type: ignore[arg-type]
        if enum.Role.ROOT not in self._root["user"].roles:
            self._root["user"].roles.add(enum.Role.ROOT)

        # Get automatic new user data
        self._automatic_new_user: dict | None = None
        if automatic_new_user_cfg:
            self._automatic_new_user = {}
            self._automatic_new_user["roles"] = {
                enum.Role[x] for x in automatic_new_user_cfg["roles"]
            }
            self._automatic_new_user["data_collection_ids"] = {
                UUID(x) for x in automatic_new_user_cfg["data_collection_ids"]
            }

    def generate_id(self) -> UUID:
        return self._organization_service.generate_id()  # type: ignore[return-value]

    def get_user_instance_from_claims(  # type: ignore
        self, claims: dict[str, Any]
    ) -> model.User | None:
        if self._automatic_new_user is None:
            return None
        roles = self._automatic_new_user["roles"] if self._automatic_new_user else set()
        data_collection_ids = (
            self._automatic_new_user["data_collection_ids"]
            if self._automatic_new_user
            else set()
        )
        email = get_email_from_claims(claims)
        if not email:
            raise exc.CredentialsAuthError("Email not found in claims")
        return model.User(
            email=email,
            is_active=True,
            roles=roles,
            data_collection_ids=data_collection_ids,
        )

    def is_root_user(self, claims: dict[str, Any]) -> bool:
        return self._root["user"].email == get_email_from_claims(claims)

    def create_root_user_from_claims(self, claims: dict[str, Any]) -> model.User:  # type: ignore
        assert isinstance(
            self._organization_service.repository, BaseOrganizationRepository
        )
        with self._organization_service.repository.uow() as uow:
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
                # Update user if necessary
                is_updated = False
                for key, value in claims.items():
                    if not hasattr(user, key) or getattr(user, key) == value:
                        continue
                    is_updated = True
                    if key == "roles":
                        value = set([enum.Role[x] for x in value])
                    elif key == "data_collection_ids":
                        value = set(UUID(x) for x in value)
                    else:
                        setattr(user, key, value)
                if enum.Role.ROOT not in user.roles:
                    is_updated = True
                    user.roles.add(enum.Role.ROOT)
                if is_updated:
                    user = self._organization_service.repository.crud(  # type: ignore[assignment]
                        uow,
                        self._root["user"].id,
                        model.User,
                        user,
                        None,
                        CrudOperation.UPDATE_ONE,
                    )
            else:
                # New user
                user = self._organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    self._root["user"].id,
                    model.User,
                    self._root["user"],
                    None,
                    CrudOperation.CREATE_ONE,
                )
        return user

    def create_user_from_claims(  # type: ignore
        self, claims: dict[str, Any]
    ) -> model.User:
        assert isinstance(
            self._organization_service.repository, BaseOrganizationRepository
        )
        with self._organization_service.repository.uow() as uow:
            email = get_email_from_claims(claims)
            is_existing_user = (
                self._organization_service.repository.is_existing_user_by_key(
                    uow, email
                )
            )
            user: model.User
            if is_existing_user:
                assert email is not None
                user = self.retrieve_user_by_key(email)
            else:
                claims_user = self.get_user_instance_from_claims(claims)
                if not claims_user:
                    raise exc.InitializationServiceError(
                        "Unable to create user from claims"
                    )
                claims_user.id = self.generate_id()
                user = self._organization_service.repository.crud(  # type:ignore[assignment]
                    uow,
                    claims_user.id,
                    model.User,
                    claims_user,
                    None,
                    CrudOperation.CREATE_ONE,
                )
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
                and x.expires_at > timestamp
            ]
            if not user_invitations:
                raise exc.UnauthorizedAuthError("Invitation does not exist")

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
