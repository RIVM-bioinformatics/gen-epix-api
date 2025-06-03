from typing import Callable
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.casedb.api.base import EXCLUDED_PERMISSIONS
from gen_epix.casedb.api.model import CompleteUser
from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator


class UpdateOrganizationSetOrganizationRequestBody(PydanticBaseModel):
    organization_set_members: list[model.OrganizationSetMember]


class UpdateDataCollectionSetDataCollectionRequestBody(PydanticBaseModel):
    data_collection_set_members: list[model.DataCollectionSetMember]


class UpdateUserRequestBody(PydanticBaseModel):
    is_active: bool | None
    roles: set[enum.Role] | None
    organization_id: UUID | None


class UpdateUserOwnOrganizationRequestBody(PydanticBaseModel):
    organization_id: UUID


def create_organization_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable | None = None,
    **kwargs: dict,
) -> None:
    assert handle_exception

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
    ) -> CompleteUser:
        try:
            cmd = command.RetrieveCompleteUserCommand(user=user)
            app_retval: model.CompleteUser = app.handle(cmd)
            retval: CompleteUser = CompleteUser.from_model(app_retval)
        except Exception as exception:
            handle_exception("f98b34ec", user, exception)
        return retval

    @router.put(
        "/users/{object_id}",
        operation_id="users__put_one",
        name="UpdateUser",
    )
    async def users__put_one(
        user: registered_user_dependency, object_id: UUID, request_body: UpdateUserRequestBody  # type: ignore
    ) -> model.User:
        try:
            cmd = command.UpdateUserCommand(
                user=user,
                tgt_user_id=object_id,
                is_active=request_body.is_active,
                roles=request_body.roles,
                organization_id=request_body.organization_id,
            )
            retval: model.User = app.handle(cmd)
        except Exception as exception:
            handle_exception("a594ba2b", None, exception)
        return retval

    @router.get(
        "/retrieve_organization_admin_name_emails",
        operation_id="retrieve_organization_admin_name_emails",
        name="RetrieveOrganizationAdminNameEmailsCommand",
    )
    async def retrieve_organization_admin_name_emails(user: registered_user_dependency) -> list[model.UserNameEmail]:  # type: ignore
        try:
            cmd = command.RetrieveOrganizationAdminNameEmailsCommand(
                user=user,
            )
            retval: list[model.UserNameEmail] = app.handle(cmd)
        except Exception as exception:
            handle_exception("fd6a9c3e", None, exception)
        return retval

    @router.put(
        "/update_user_own_organization",
        operation_id="update_user_own_organization",
        name="UpdateUserOwnOrganization",
    )
    async def update_user_own_organization(
        user: registered_user_dependency, data: UpdateUserOwnOrganizationRequestBody  # type: ignore
    ) -> model.User:
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
        service_type=enum.ServiceType.ORGANIZATION,
        user_dependency=registered_user_dependency,
        excluded_permissions=EXCLUDED_PERMISSIONS,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )
