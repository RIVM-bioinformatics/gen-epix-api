"""Create the shared operational-data reset endpoint for domain app routers.

The factory controls route availability. Authorization and deletion remain in
the command lifecycle and the owning application's service and repository.
"""

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter, FastAPI, Response

from gen_epix.commondb.api.exc import handle_command
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain.command import DeleteOperationalDataCommand
from gen_epix.commondb.domain.enum import FeatureFlag
from gen_epix.fastapp import App


def create_operational_data_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
) -> None:
    """Register the reset endpoint if the application feature flag is enabled.

    The caller must only use this factory for an app with a reset handler.
    Changing route visibility requires rebuilding the routers.

    Args:
        router: Domain router receiving the endpoint below the v1 prefix.
        app: Composed application supplying authentication and command dispatch.
        handle_exception: Existing API exception adapter.
    """
    if not app.get_feature_flag(FeatureFlag.ALLOW_DELETE_OPERATIONAL_DATA.value):
        return
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    @router.delete(
        "/operational_data",
        operation_id="delete__operational_data",
        name="Delete all operational data",
        description=DeleteOperationalDataCommand.__doc__,
        status_code=204,
        response_class=Response,
    )
    async def delete__operational_data(
        user: registered_user_dependency,  # type: ignore[valid-type]
    ) -> Response:
        """Delete operational data using the authenticated command lifecycle."""
        handle_command(
            app=app,
            user=user,
            exception_code="12b97ab6",
            input_command=DeleteOperationalDataCommand(user=user),
            input_handle_exception=handle_exception,
        )
        return Response(status_code=204)
