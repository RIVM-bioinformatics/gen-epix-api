from typing import Callable
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from gen_epix.casedb.api.base import EXCLUDED_PERMISSIONS
from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator


class UserInvitationRequestBody(PydanticBaseModel):
    email: str
    roles: set[enum.Role] = Field(description="The roles of the user", min_length=1)
    organization_id: UUID


def create_auth_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable | None = None,
    **kwargs: dict,
) -> None:
    assert handle_exception

    # Specific endpoints - Auth
    @router.get(
        "/identity_providers",
        operation_id="identity_providers__get_all",
        name="IdentityProvider",
    )
    async def identity_providers__get_all() -> list[model.IdentityProvider]:
        try:
            cmd = command.GetIdentityProvidersCommand(user=None)
            retval: list[model.IdentityProvider] = app.handle(cmd)
        except Exception as exception:
            handle_exception("3ddf8ebb", None, exception)
        return retval

    @router.post(
        "/user_invitations",
        operation_id="user_invitations__post_one",
        name="UserInvitations",
    )
    async def user_invitations__post_one(
        user: registered_user_dependency, user_invitation: UserInvitationRequestBody  # type: ignore
    ) -> model.UserInvitation:
        try:
            retval: model.UserInvitation = app.handle(
                command.InviteUserCommand(
                    user=user,
                    email=user_invitation.email,
                    roles=user_invitation.roles,
                    organization_id=user_invitation.organization_id,
                )
            )
        except Exception as exception:
            handle_exception("e088de91", None, exception)
        return retval

    @router.post(
        "/user_registrations/{token}",
        operation_id="user_registrations__post_one",
        name="RegisterInvitedUser",
    )
    async def user_registrations__post_one(
        user: new_user_dependency, token: str  # type: ignore
    ) -> model.User:
        try:
            cmd = command.RegisterInvitedUserCommand(
                user=user,
                token=token,
            )
            retval: model.User = app.handle(cmd)
        except Exception as exception:
            handle_exception("fc1fc53c", None, exception)
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.AUTH,
        user_dependency=registered_user_dependency,
        excluded_permissions=EXCLUDED_PERMISSIONS,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )
