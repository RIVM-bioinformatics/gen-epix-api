from collections.abc import Callable
from enum import Enum
from typing import Any, NoReturn, cast
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import DOMAIN, command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.model import Permission
from gen_epix.util import copy_model_field
from gen_epix.commondb.api.exc import handle_command

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc] # Dynamic Enum required


class ApiPermission(PydanticBaseModel, frozen=True):
    command_name: CommandName = (  # pyright: ignore[reportInvalidTypeForm]
        copy_model_field(Permission, "command_name")
    )
    permission_type: PermissionType = copy_model_field(Permission, "permission_type")


class UserInvitationRequestBody(PydanticBaseModel):
    key: str = copy_model_field(model.UserInvitation, "key")
    roles: set[str] = copy_model_field(model.UserInvitation, "roles")
    organization_id: UUID = copy_model_field(model.UserInvitation, "organization_id")


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
    roles: set[str] | None = Field(
        description="The updated set of roles of the user. Not updated if not provided. If provided, should have at least one element.",
    )
    organization_id: UUID | None = Field(
        description="The updated organization ID of the user. Not updated if not provided."
    )


class UpdateUserOwnOrganizationRequestBody(PydanticBaseModel):
    organization_id: UUID = Field(
        description="The ID of the organization to update the user to"
    )


class UpdateOrganizationIdentifierIssuerLinksRequestBody(PydanticBaseModel):
    organization_identifier_issuer_links: list[
        model.OrganizationIdentifierIssuerLink
    ] = Field(description="The identifier issuers that the organization is linked to.")


def create_organization_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    service_type: enum.ServiceType = enum.ServiceType.ORGANIZATION,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    api_permission_class: type = Permission,
    **kwargs: Any,
) -> None:
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    user_class: type[model.User] = app_impl.get_mapped_class(model.User)
    user_invitation_class: type[model.UserInvitation] = app_impl.get_mapped_class(
        model.UserInvitation
    )
    invite_user_command_class: type[command.InviteUserCommand] = (
        app_impl.get_mapped_class(command.InviteUserCommand)
    )
    retrieve_invite_user_constraints_command_class: type[
        command.RetrieveInviteUserConstraintsCommand
    ] = app_impl.get_mapped_class(command.RetrieveInviteUserConstraintsCommand)
    update_user_command_class: type[command.UpdateUserCommand] = (
        app_impl.get_mapped_class(command.UpdateUserCommand)
    )
    # TODO: If dynamic typing isn't used or required anymore,
    # refator endpoints below using handle_command method (return cast(..., handle_command()))
    registered_user_dependency = app_impl.registered_user_dependency
    new_user_dependency = app_impl.new_user_dependency

    @router.post(
        "/invite_user",
        operation_id="invite_user",
        name="Invite a user",
        description=invite_user_command_class.__doc__,
    )
    async def invite_user(
        user: registered_user_dependency, user_invitation: UserInvitationRequestBody  # type: ignore[valid-type] # Dynamic type annotation
    ) -> user_invitation_class:  # type: ignore
        try:
            retval: user_invitation_class = app.handle(  # type: ignore[valid-type] # Dynamic type annotation
                invite_user_command_class(
                    user=user,
                    key=user_invitation.key,
                    roles=user_invitation.roles,
                    organization_id=user_invitation.organization_id,
                )
            )
        except Exception as exception:
            handle_exception("e088de91", None, exception)
        return retval

    @router.get(
        "/invite_user/constraints",
        operation_id="invite_user__constraints",
        name="The constraints for inviting a user",
        description=retrieve_invite_user_constraints_command_class.__doc__,
    )
    async def invite_user__constraints(
        user: registered_user_dependency,
    ) -> model.UserInvitationConstraints:
        return cast(
            model.UserInvitationConstraints,
            handle_command(
                app=app,
                user=user,
                exception_code="cad2509e",
                input_handle_exception=handle_exception,
                input_command=retrieve_invite_user_constraints_command_class(user=user),
            ),
        )

    @router.post(
        "/user_registrations/{token}",
        operation_id="user_registrations__post_one",
        name="RegisterInvitedUser",
        description=command.RegisterInvitedUserCommand.__doc__,
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
        description=command.OrganizationSetOrganizationUpdateAssociationCommand.__doc__,
    )
    async def organization_sets__put__organizations(
        user: registered_user_dependency,  # type: ignore
        organization_set_id: UUID,
        request_body: UpdateOrganizationSetOrganizationRequestBody,
    ) -> list[model.OrganizationSetMember]:
        return cast(
            list[model.OrganizationSetMember],
            handle_command(
                app=app,
                user=user,
                exception_code="c026628e",
                input_handle_exception=handle_exception,
                input_command=command.OrganizationSetOrganizationUpdateAssociationCommand(
                    user=user,
                    obj_id1=organization_set_id,
                    association_objs=request_body.organization_set_members,
                    props={"return_id": False},
                ),
            ),
        )

    @router.put(
        "/data_collection_sets/{data_collection_set_id}/data_collections",
        operation_id="data_collection_sets__put__data_collections",
        name="DataCollectionSet_DataCollection",
        description=command.DataCollectionSetDataCollectionUpdateAssociationCommand.__doc__,
    )
    async def data_collection_sets__put__data_collections(
        user: registered_user_dependency,  # type: ignore
        data_collection_set_id: UUID,
        request_body: UpdateDataCollectionSetDataCollectionRequestBody,
    ) -> list[model.DataCollectionSetMember]:
        return cast(
            list[model.DataCollectionSetMember],
            handle_command(
                app=app,
                user=user,
                exception_code="cf892de0",
                input_handle_exception=handle_exception,
                input_command=command.DataCollectionSetDataCollectionUpdateAssociationCommand(
                    user=user,
                    obj_id1=data_collection_set_id,
                    association_objs=request_body.data_collection_set_members,
                    props={"return_id": False},
                ),
            ),
        )

    @router.get(
        "/user_me",
        operation_id="user_me__get_one",
        name="UserMe",
        description=user_class.__doc__,
    )
    async def user_me__get_one(
        user: registered_user_dependency,  # type: ignore
    ) -> user_class:
        return user

    @router.get(
        "/user_me/permissions",
        operation_id="user_me__retrieve_permissions",
        name="UserMe_Permissions",
        description=command.RetrieveOwnPermissionsCommand.__doc__,
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
        "/update_user/{object_id}",
        operation_id="update_user",
        name="UpdateUser",
        description=update_user_command_class.__doc__,
    )
    async def update_user(
        user: registered_user_dependency, object_id: UUID, request_body: UpdateUserRequestBody  # type: ignore
    ) -> user_class:
        try:
            cmd = update_user_command_class(
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
        name="UpdateUserOwnOrganizationCommand",
        description=command.UpdateUserOwnOrganizationCommand.__doc__,
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

    @router.put(
        "/organizations/{organization_id}/identifier_issuers",
        operation_id="organizations__put__identifier_issuers",
        name="Update association between Organization and IdentifierIssuer",
        description=command.OrganizationIdentifierIssuerLinkUpdateAssociationCommand.__doc__,
    )
    async def organizations__put__identifier_issuers(
        user: registered_user_dependency,  # type: ignore
        organization_id: UUID,
        request_body: UpdateOrganizationIdentifierIssuerLinksRequestBody,
    ) -> list[model.OrganizationIdentifierIssuerLink]:
        return cast(
            list[model.OrganizationIdentifierIssuerLink],
            handle_command(
                app=app,
                user=user,
                exception_code="a3c7f9d2",
                input_handle_exception=handle_exception,
                input_command=command.OrganizationIdentifierIssuerLinkUpdateAssociationCommand(
                    user=user,
                    obj_id1=organization_id,
                    association_objs=request_body.organization_identifier_issuer_links,
                    props={"return_id": False},
                ),
            ),
        )

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=service_type,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )
