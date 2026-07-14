import datetime
from typing import Any, cast
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
        auto_created_user_cfg: dict[str, str] | None = None,
        key_claim: str | None = None,
        name_claims: list[str | list[str]] | None = None,
    ):

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
        return self._organization_service.generate_id()  # type: ignore[return-value]

    def get_user_key_from_claims(self, claims: dict[str, Any]) -> str | None:
        return claims.get(self._key_claim)

    def get_user_name_from_claims(self, claims: dict[str, Any]) -> str | None:
        return get_name_from_claims(claims, self._name_claims)

    def construct_user_instance_from_claims(
        self, claims: dict[str, Any]
    ) -> model.User | None:
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
        return self._root_user.key == claims.get(self._key_claim)

    def is_root_user(self, user: model.User) -> bool:  # type: ignore[override]
        return self._rbac_service.root_role in user.roles

    def create_root_user_from_claims(self, claims: dict[str, Any]) -> model.User:
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
            root_user.id = cast(UUID, self._organization_service.generate_id())
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

            # TODO: this should be removed, does not belong in commondb since specific for casedb, and the case policies in question should not be added to the user at this stage
            # # Add user case policies by calling switching organization method
            # try:
            #     user = self._organization_service.app.handle(
            #         command.UpdateUserOwnOrganizationCommand(
            #             user=user,
            #             organization_id=user.organization_id,
            #             is_new_user=True,
            #         ),
            #     )
            # except Exception as exception:
            #     raise exc.UnauthorizedAuthError("Unable to add user case policies")

        return user

    def create_new_user_from_token(  # type: ignore[override]
        self, user: model.User, token: str, **kwargs: Any
    ) -> model.User:
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
        return self._organization_service.repository.is_existing_user_by_key(
            uow, user_key
        )

    def retrieve_user_by_key(self, user_key: str) -> model.User:
        return self._organization_service.retrieve_user_by_key(user_key)

    def retrieve_user_by_id(self, user_id: UUID) -> model.User:  # type: ignore[override]
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
        if user.name == new_name:
            return user
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
        return self._rbac_service.retrieve_user_permissions(user)
