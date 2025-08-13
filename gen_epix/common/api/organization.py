from enum import Enum
from typing import Any, Callable, NoReturn, Type
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_validator

from gen_epix.common.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.fastapp.model import Permission


class UserInvitationRequestBody(PydanticBaseModel):
    email: str
    roles: set[Enum] = Field(description="The roles of the user", min_length=1)
    organization_id: UUID = Field(
        description="The ID of the organization that the invited will belong to"
    )


class UpdateOrganizationSetOrganizationRequestBody(PydanticBaseModel):
    organization_set_members: list[model.OrganizationSetMember] = Field(
        description="The updated set of organization set members, replacing the previous set"
    )


class UpdateDataCollectionSetDataCollectionRequestBody(PydanticBaseModel):
    data_collection_set_members: list[model.DataCollectionSetMember] = Field(
        description="The updated set of data collection set members, replacing the previous set"
    )


class UpdateUserRequestBody(PydanticBaseModel):
    is_active: bool | None = Field(
        description="The updated active status of the user. Not updated if not provided."
    )
    roles: set[Enum] | None = Field(
        description="The updated set of roles of the user. Not updated if not provided. If provided, should have at least one element.",
    )
    organization_id: UUID | None = Field(
        description="The updated organization ID of the user. Not updated if not provided."
    )

    @field_validator("roles", mode="after")
    def validate_roles(cls, value: set[Enum] | None) -> set[Enum] | None:
        if value is not None and len(value) < 1:
            raise ValueError("Roles must have at least one element when provided.")
        return value


class UpdateUserOwnOrganizationRequestBody(PydanticBaseModel):
    organization_id: UUID = Field(
        description="The ID of the organization to update the user to"
    )


def create_organization_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    service_type: enum.ServiceType = enum.ServiceType.ORGANIZATION,
    user_class: Type[model.User] = model.User,
    user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
    user_invitation_request_body_class: Type[
        UserInvitationRequestBody
    ] = UserInvitationRequestBody,
    update_user_request_body_class: Type[UpdateUserRequestBody] = UpdateUserRequestBody,
    api_permission_class: Type = Permission,
    **kwargs: Any,
) -> None:
    assert handle_exception

    @router.post(
        "/user_invitations",
        operation_id="user_invitations__post_one",
        name="UserInvitations",
    )
    async def user_invitations__post_one(
        user: registered_user_dependency, user_invitation: user_invitation_request_body_class  # type: ignore[valid-type] # Dynamic type annotation
    ) -> user_invitation_class:  # type: ignore
        try:
            retval: user_invitation_class = app.handle(  # type: ignore[valid-type] # Dynamic type annotation
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
        user: new_user_dependency, token: str  # type: ignore[valid-type] # Dynamic type annotation
    ) -> user_class:  # type: ignore[valid-type] # Dynamic type annotation
        try:
            cmd = command.RegisterInvitedUserCommand(
                user=user,
                token=token,
            )
            retval: user_class = app.handle(cmd)  # type: ignore[valid-type] # Dynamic type annotation
        except Exception as exception:
            handle_exception("fc1fc53c", None, exception)
        return retval

    @router.put(
        "/organization_sets/{organization_set_id}/organizations",
        operation_id="organization_sets__put__organizations",
        name="OrganizationSet_Organization",
    )
    async def organization_sets__put__organizations(
        user: registered_user_dependency,  # type: ignore
        organization_set_id: UUID,
        request_body: UpdateOrganizationSetOrganizationRequestBody,
    ) -> list[model.OrganizationSetMember]:
        try:
            cmd = command.OrganizationSetOrganizationUpdateAssociationCommand(
                user=user,
                obj_id1=organization_set_id,
                association_objs=request_body.organization_set_members,
                props={"return_id": False},
            )
            retval: list[model.OrganizationSetMember] = app.handle(cmd)
        except Exception as exception:
            handle_exception("c026628e", user, exception)
        return retval

    @router.put(
        "/data_collection_sets/{data_collection_set_id}/data_collections",
        operation_id="data_collection_sets__put__data_collections",
        name="DataCollectionSet_DataCollection",
    )
    async def data_collection_sets__put__data_collections(
        user: registered_user_dependency,  # type: ignore
        data_collection_set_id: UUID,
        request_body: UpdateDataCollectionSetDataCollectionRequestBody,
    ) -> list[model.DataCollectionSetMember]:
        try:
            cmd = command.DataCollectionSetDataCollectionUpdateAssociationCommand(
                user=user,
                obj_id1=data_collection_set_id,
                association_objs=request_body.data_collection_set_members,
                props={"return_id": False},
            )
            retval: list[model.DataCollectionSetMember] = app.handle(cmd)
        except Exception as exception:
            handle_exception("cf892de0", user, exception)
        return retval

    @router.get(
        "/user_me",
        operation_id="user_me__get_one",
        name="UserMe",
    )
    async def user_me__get_one(
        user: registered_user_dependency,  # type: ignore
    ) -> user_class:
        return user

    @router.get(
        "/user_me/permissions",
        operation_id="user_me__retrieve_permissions",
        name="UserMe",
    )
    async def user_me__retrieve_permissions(
        user: registered_user_dependency,  # type: ignore
    ) -> set[api_permission_class]:  # pyricht: ignore[reportInvalidTypeForm]
        try:
            cmd = command.RetrieveOwnPermissionsCommand(user=user)
            permissions: set[Permission] = app.handle(cmd)
            retval = {api_permission_class(**x.model_dump()) for x in permissions}
        except Exception as exception:
            handle_exception("a7f3b8e2", user, exception)
        return retval

    @router.put(
        "/users/{object_id}",
        operation_id="users__put_one",
        name="UpdateUser",
    )
    async def users__put_one(
        user: registered_user_dependency, object_id: UUID, request_body: update_user_request_body_class  # type: ignore
    ) -> user_class:
        try:
            cmd = command.UpdateUserCommand(
                user=user,
                tgt_user_id=object_id,
                is_active=request_body.is_active,
                roles=request_body.roles,
                organization_id=request_body.organization_id,
            )
            retval: user_class = app.handle(cmd)
        except Exception as exception:
            handle_exception("a594ba2b", None, exception)
        return retval

    @router.put(
        "/update_user_own_organization",
        operation_id="update_user_own_organization",
        name="UpdateUserOwnOrganization",
    )
    async def update_user_own_organization(
        user: registered_user_dependency, data: UpdateUserOwnOrganizationRequestBody  # type: ignore
    ) -> user_class:
        try:
            cmd = command.UpdateUserOwnOrganizationCommand(
                user=user,
                organization_id=data.organization_id,
            )
            retval: model.User = app.handle(cmd)
        except Exception as exception:
            handle_exception("c2382b65", None, exception)
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=service_type,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )
