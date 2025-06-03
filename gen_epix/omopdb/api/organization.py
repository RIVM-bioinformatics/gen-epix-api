from typing import Callable
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.omopdb.api.base import EXCLUDED_PERMISSIONS
from gen_epix.omopdb.domain import command, enum, model
from gen_epix.omopdb.domain.model import CompleteUser


class UpdateUserRequestBody(PydanticBaseModel):
    is_active: bool | None
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
            retval = CompleteUser.from_model(app_retval)
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
                organization_id=request_body.organization_id,
            )
            retval: model.User = app.handle(cmd)
        except Exception as exception:
            handle_exception("a594ba2b", None, exception)
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
