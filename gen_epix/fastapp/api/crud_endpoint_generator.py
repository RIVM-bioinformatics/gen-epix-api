import itertools
import json
from typing import Annotated, Any, Callable, Hashable, Type
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import Field

from gen_epix.fastapp import exc, model
from gen_epix.fastapp.api.crud_endpoint_set import CrudEndpointSet
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import (
    CrudEndpointType,
    CrudOperation,
    HttpMethod,
    PermissionType,
    PermissionTypeSet,
    StringCasing,
)
from gen_epix.fastapp.model import Permission
from gen_epix.filter import (
    CompositeFilter,
    Filter,
    TypedCompositeFilter,
    TypedDateRangeFilter,
    TypedDatetimeRangeFilter,
    TypedEqualsBooleanFilter,
    TypedEqualsNumberFilter,
    TypedEqualsStringFilter,
    TypedEqualsUuidFilter,
    TypedExistsFilter,
    TypedNoFilter,
    TypedNumberRangeFilter,
    TypedNumberSetFilter,
    TypedPartialDateRangeFilter,
    TypedRegexFilter,
    TypedStringSetFilter,
    TypedUuidSetFilter,
)


def _default_validate_query_filter(
    query_filter: Filter,
) -> bool:
    if isinstance(query_filter, CompositeFilter):
        for subfilter in query_filter.filters:
            if isinstance(subfilter, CompositeFilter):
                return False
    return True


class CrudEndpointGenerator:
    DEFAULT_BATCH_ROUTE_SUFFIX = "/batch"
    DEFAULT_QUERY_ROUTE_SUFFIX = "/query"
    DEFAULT_IDS_ROUTE_SUFFIX = "/ids"

    CRUD_OPERATION_TO_ENDPOINT_TYPE: dict[CrudOperation, CrudEndpointType] = {
        CrudOperation.READ_ALL: CrudEndpointType.GET_ALL,
        CrudOperation.READ_SOME: CrudEndpointType.GET_SOME,
        CrudOperation.READ_ONE: CrudEndpointType.GET_ONE,
        CrudOperation.CREATE_ONE: CrudEndpointType.POST_ONE,
        CrudOperation.CREATE_SOME: CrudEndpointType.POST_SOME,
        CrudOperation.UPDATE_ONE: CrudEndpointType.PUT_ONE,
        CrudOperation.UPDATE_SOME: CrudEndpointType.PUT_SOME,
        CrudOperation.DELETE_ONE: CrudEndpointType.DELETE_ONE,
        CrudOperation.DELETE_SOME: CrudEndpointType.DELETE_SOME,
        CrudOperation.DELETE_ALL: CrudEndpointType.DELETE_ALL,
    }
    CRUD_ENDPOINT_TYPE_ORDER: list[CrudEndpointType] = [
        CrudEndpointType.GET_ALL,
        CrudEndpointType.DELETE_ALL,
        CrudEndpointType.POST_QUERY,
        CrudEndpointType.POST_QUERY_IDS,
        CrudEndpointType.POST_SOME,
        CrudEndpointType.GET_SOME,
        CrudEndpointType.PUT_SOME,
        CrudEndpointType.DELETE_SOME,
        CrudEndpointType.POST_ONE,
        CrudEndpointType.GET_ONE,
        CrudEndpointType.PUT_ONE,
        CrudEndpointType.DELETE_ONE,
    ]

    @staticmethod
    def convert_ids_string_to_list(
        id_class: Type, ids_str: str
    ) -> tuple[list | None, list[str]]:
        invalid_ids = []
        try:
            ids = [id_class(x) for x in ids_str.split(",")]
        except:
            try:
                raw_ids = json.loads(ids_str)
                ids = []
                for id_ in raw_ids:
                    try:
                        ids.append(id_class(id_))
                    except:
                        invalid_ids.append(id_)
            except:
                invalid_ids.append(ids_str)
                ids = None
        return ids, invalid_ids

    @staticmethod
    def generate_get_all(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
    ) -> None:
        async def endpoint_function(user: route.user_dependency) -> Any:  # type: ignore
            obj_ids = None
            cmd = route.crud_command_class(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
            try:
                retval = route.app.handle(cmd)
                if route.model_class is not route.read_api_model_class:
                    retval = [route.read_api_model_class.from_model(x) for x in retval]
            except Exception as exception:
                handle_exception_fun(
                    "79d26f4f" + route.endpoint_basename,
                    user,
                    exception,
                    request_ids=obj_ids,
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename,
            endpoint_function,
            HttpMethod.GET,
            list[route.read_api_model_class],
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__get_all",
        )

    @staticmethod
    def generate_get_some(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
        batch_route_suffix: str | None = None,
    ) -> None:
        if not batch_route_suffix:
            batch_route_suffix = CrudEndpointGenerator.DEFAULT_BATCH_ROUTE_SUFFIX

        async def endpoint_function(user: route.user_dependency, ids: str) -> Any:  # type: ignore
            obj_ids, invalid_obj_ids = CrudEndpointGenerator.convert_ids_string_to_list(
                route.id_class, ids
            )
            if invalid_obj_ids:
                # f-string parsing fails if this is not first passed to a variable
                error_msg = ", ".join([f'"{x}"' for x in invalid_obj_ids])
                handle_exception_fun(
                    "a8abf0e3",
                    user,
                    exc.InvalidIdsError(
                        f"Invalid ids in ids query parameter: {error_msg}",
                        invalid_obj_ids,
                    ),
                    request_ids=invalid_obj_ids,
                )
            cmd = route.crud_command_class(
                user=user,
                obj_ids=obj_ids,
                operation=CrudOperation.READ_SOME,
            )
            try:
                retval = route.app.handle(cmd)
                if route.model_class is not route.read_api_model_class:
                    retval = [route.read_api_model_class.from_model(x) for x in retval]

            # TODO: Add a specific exception for NotImplementedError
            except Exception as exception:
                handle_exception_fun(
                    "fbc53f5d" + route.endpoint_basename,
                    user,
                    exception,
                    request_ids=obj_ids,
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + batch_route_suffix,
            endpoint_function,
            HttpMethod.GET,
            list[route.read_api_model_class],
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__get_some",
        )

    @staticmethod
    def generate_post_query(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
        query_route_suffix: str | None = None,
        return_id: bool = False,
        ids_route_suffix: str | None = None,
        validate_query_filter: (
            Callable[[Filter], bool] | None
        ) = _default_validate_query_filter,
    ) -> None:
        if not query_route_suffix:
            query_route_suffix = CrudEndpointGenerator.DEFAULT_QUERY_ROUTE_SUFFIX
        if not ids_route_suffix:
            ids_route_suffix = CrudEndpointGenerator.DEFAULT_IDS_ROUTE_SUFFIX
        route_suffix = query_route_suffix
        if return_id:
            route_suffix = route_suffix + ids_route_suffix
        operation_id = route.operation_id_basename or route.endpoint_basename
        operation_id += "__post_query"
        if return_id:
            operation_id += "__ids"

        async def endpoint_function(
            user: route.user_dependency,  # type: ignore
            filter: Annotated[
                TypedExistsFilter
                | TypedEqualsBooleanFilter
                | TypedEqualsNumberFilter
                | TypedEqualsStringFilter
                | TypedEqualsUuidFilter
                | TypedNumberRangeFilter
                | TypedDateRangeFilter
                | TypedDatetimeRangeFilter
                | TypedPartialDateRangeFilter
                | TypedRegexFilter
                | TypedNumberSetFilter
                | TypedStringSetFilter
                | TypedUuidSetFilter
                | TypedNoFilter
                | TypedCompositeFilter,
                Field(discriminator="type"),
            ],
        ) -> Any:
            if validate_query_filter and not validate_query_filter(filter):
                handle_exception_fun(
                    "cee23041" + route.endpoint_basename,
                    user,
                    exc.InvalidArgumentsError("Invalid filter"),
                )
            cmd = route.crud_command_class(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=filter,
                props={
                    "return_id": return_id,
                },
            )
            try:
                retval = route.app.handle(cmd)
                if (
                    not return_id
                    and route.model_class is not route.read_api_model_class
                ):
                    retval = [route.read_api_model_class.from_model(x) for x in retval]

            # TODO: Add a specific exception for NotImplementedError
            except Exception as exception:
                handle_exception_fun(
                    "ca2591fa" + route.endpoint_basename, user, exception
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + route_suffix,
            endpoint_function,
            HttpMethod.POST,
            list[route.id_class] if return_id else list[route.read_api_model_class],
            route,
            operation_id=operation_id,
        )

    @staticmethod
    def generate_get_one(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
    ) -> None:
        async def endpoint_function(
            user: route.user_dependency,  # type: ignore
            object_id: route.id_class,  # type: ignore
        ) -> Any:
            try:
                cmd = route.crud_command_class(
                    user=user,
                    operation=CrudOperation.READ_ONE,
                    obj_ids=object_id,
                )
                obj = route.app.handle(cmd)
                if route.model_class is not route.read_api_model_class:
                    obj = route.read_api_model_class.from_model(obj)

            # TODO: Add a specific exception for NotImplementedError
            except Exception as exception:
                handle_exception_fun(
                    "3680417c" + route.endpoint_basename + f"/{object_id}",
                    user,
                    exception,
                    request_ids=[object_id],
                )
            return obj

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + "/{object_id}",
            endpoint_function,
            HttpMethod.GET,
            route.read_api_model_class,
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__get_one",
        )

    @staticmethod
    def generate_post_one(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
    ) -> None:
        async def endpoint_function(
            user: route.user_dependency, create_obj: route.create_api_model_class  # type: ignore
        ) -> Any:
            try:
                cmd = route.crud_command_class(
                    user=user,
                    operation=CrudOperation.CREATE_ONE,
                    objs=(
                        create_obj
                        if route.model_class is route.create_api_model_class
                        else route.create_api_model_class.to_model(create_obj)
                    ),
                    props={"return_id": route.post_returns_id},
                )
                retval = route.app.handle(cmd)
                if (
                    not route.post_returns_id
                    and route.model_class is not route.read_api_model_class
                ):
                    retval = route.read_api_model_class.from_model(retval)

            except Exception as exception:
                try:
                    request_ids = [create_obj.id]
                except:
                    request_ids = None
                handle_exception_fun(
                    "02c70ca7" + route.endpoint_basename,
                    user,
                    exception,
                    request_ids=request_ids,
                )

            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename,
            endpoint_function,
            HttpMethod.POST,
            route.id_class if route.post_returns_id else route.read_api_model_class,
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__post_one",
        )

    @staticmethod
    def generate_post_some(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
        batch_route_suffix: str | None = None,
    ) -> None:
        if not batch_route_suffix:
            batch_route_suffix = CrudEndpointGenerator.DEFAULT_BATCH_ROUTE_SUFFIX

        async def endpoint_function(
            user: route.user_dependency, create_objs: list[route.create_api_model_class]  # type: ignore
        ) -> Any:
            try:
                cmd = route.crud_command_class(
                    user=user,
                    operation=CrudOperation.CREATE_SOME,
                    objs=(
                        create_objs
                        if route.model_class is route.create_api_model_class
                        else [
                            route.create_api_model_class.to_model(x)
                            for x in create_objs
                        ]
                    ),
                    props={"return_id": route.post_returns_id},
                )
                retval = route.app.handle(cmd)
                if (
                    not route.post_returns_id
                    and route.model_class is not route.read_api_model_class
                ):
                    retval = [route.read_api_model_class.from_model(x) for x in retval]

            except Exception as exception:
                try:
                    request_ids = [x.id for x in create_objs]
                except:
                    request_ids = None
                handle_exception_fun(
                    "e96480ac" + route.endpoint_basename,
                    user,
                    exception,
                    request_ids=request_ids,
                )

            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + batch_route_suffix,
            endpoint_function,
            HttpMethod.POST,
            (
                list[route.id_class]
                if route.post_returns_id
                else list[route.read_api_model_class]
            ),
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__post_some",
        )

    @staticmethod
    def generate_put_one(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
    ) -> None:
        async def endpoint_function(
            user: route.user_dependency,
            object_id: route.id_class,  # type: ignore
            update_obj: route.create_api_model_class,  # type: ignore
        ) -> Any:
            if update_obj.id != object_id:
                raise exc.BadRequest400HTTPException()
            try:
                cmd = route.crud_command_class(
                    user=user,
                    operation=CrudOperation.UPDATE_ONE,
                    objs=(
                        update_obj
                        if route.model_class is route.create_api_model_class
                        else route.model_class.to_model(update_obj)
                    ),
                    props={"return_id": route.put_returns_id},
                )
                retval = route.app.handle(cmd)
                if (
                    not route.put_returns_id
                    and route.model_class is not route.read_api_model_class
                ):
                    retval = route.read_api_model_class.from_model(retval)
            except Exception as exception:
                handle_exception_fun(
                    "1459d302" + route.endpoint_basename + f"/{object_id}",
                    user,
                    exception,
                    request_ids=[object_id],
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + "/{object_id}",
            endpoint_function,
            HttpMethod.PUT,
            route.id_class if route.post_returns_id else route.read_api_model_class,
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__put_one",
        )

    @staticmethod
    def generate_put_some(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
        batch_route_suffix: str | None = None,
    ) -> None:
        if not batch_route_suffix:
            batch_route_suffix = CrudEndpointGenerator.DEFAULT_BATCH_ROUTE_SUFFIX

        async def endpoint_function(
            user: route.user_dependency,  # type: ignore
            update_objs: list[route.create_api_model_class],  # type: ignore
        ) -> Any:
            try:
                cmd = route.crud_command_class(
                    user=user,
                    operation=CrudOperation.UPDATE_SOME,
                    objs=(
                        update_objs
                        if route.model_class is route.create_api_model_class
                        else [route.model_class.to_model(x) for x in update_objs]
                    ),
                    props={"return_id": route.put_returns_id},
                )
                retval = route.app.handle(cmd)
                if (
                    not route.put_returns_id
                    and route.model_class is not route.read_api_model_class
                ):
                    retval = [route.read_api_model_class.from_model(x) for x in retval]
            except Exception as exception:
                handle_exception_fun(
                    "b9359ae3" + route.endpoint_basename,
                    user,
                    exception,
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + batch_route_suffix,
            endpoint_function,
            HttpMethod.PUT,
            (
                list[route.id_class]
                if route.post_returns_id
                else list[route.read_api_model_class]
            ),
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__put_some",
        )

    @staticmethod
    def generate_delete_one(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
    ) -> None:
        async def endpoint_function(user: route.user_dependency, object_id: Any) -> Any:  # type: ignore
            # TODO: distinguish between soft and hard delete through hard_delete:
            #  bool = False parameter
            try:
                cmd = route.crud_command_class(
                    user=user,
                    operation=CrudOperation.DELETE_ONE,
                    obj_ids=object_id,
                )
                retval = route.app.handle(cmd)
            except Exception as exception:
                handle_exception_fun(
                    "ab4df15f" + route.endpoint_basename + f"/{object_id}",
                    user,
                    exception,
                    request_ids=[object_id],
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + "/{object_id}",
            endpoint_function,
            HttpMethod.DELETE,
            route.id_class,
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__delete_one",
        )

    @staticmethod
    def generate_delete_all(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
    ) -> None:
        async def endpoint_function(user: route.user_dependency) -> Any:  # type: ignore
            obj_ids = None
            cmd = route.crud_command_class(
                user=user,
                operation=CrudOperation.DELETE_ALL,
                props={"return_id": route.delete_all_returns_id},
            )
            try:
                retval = route.app.handle(cmd)
            # TODO: Add a specific exception for NotImplementedError
            except Exception as exception:
                handle_exception_fun(
                    "79d26f4f" + route.endpoint_basename,
                    user,
                    exception,
                    request_ids=obj_ids,
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename,
            endpoint_function,
            HttpMethod.DELETE,
            list[route.id_class] if route.delete_all_returns_id else None,
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__delete_all",
        )

    @staticmethod
    def generate_delete_some(
        fast_api: FastAPI | APIRouter,
        route: CrudEndpointSet,
        handle_exception_fun: Callable,
        batch_route_suffix: str | None = None,
    ) -> None:
        if not batch_route_suffix:
            batch_route_suffix = CrudEndpointGenerator.DEFAULT_BATCH_ROUTE_SUFFIX

        async def endpoint_function(
            user: route.user_dependency,  # type: ignore
            ids: str,
        ) -> Any:
            obj_ids, invalid_obj_ids = CrudEndpointGenerator.convert_ids_string_to_list(
                route.id_class, ids
            )
            if invalid_obj_ids:
                # f-string parsing fails if this is not first passed to a variable
                error_msg = ", ".join([f'"{x}"' for x in invalid_obj_ids])
                handle_exception_fun(
                    "e73f930b",
                    user,
                    exc.InvalidIdsError(
                        f"Invalid ids in ids query parameter: {error_msg}",
                        invalid_obj_ids,
                    ),
                    request_ids=invalid_obj_ids,
                )
            cmd = route.crud_command_class(
                user=user,
                obj_ids=obj_ids,
                operation=CrudOperation.DELETE_SOME,
                props={"return_id": route.delete_all_returns_id},
            )
            try:
                retval = route.app.handle(cmd)
            # TODO: Add a specific exception for NotImplementedError
            except Exception as exception:
                handle_exception_fun(
                    "fce475e1" + route.endpoint_basename,
                    user,
                    exception,
                    request_ids=obj_ids,
                )
            return retval

        CrudEndpointGenerator._add_route(
            fast_api,
            route.endpoint_basename + batch_route_suffix,
            endpoint_function,
            HttpMethod.DELETE,
            list[route.id_class],
            route,
            operation_id=(route.operation_id_basename or route.endpoint_basename)
            + "__delete_some",
        )

    @staticmethod
    def _add_route(
        fast_api: FastAPI | APIRouter,
        endpoint: str,
        endpoint_function: Callable,
        method: HttpMethod,
        response_model: Any | None,
        route: CrudEndpointSet,
        operation_id: str | None = None,
    ) -> None:
        if not operation_id:
            tokens = endpoint.split("/")
            if tokens[-1] == "{object_id}" or method.value.upper() == "POST":
                operation_id = tokens[1] + "__" + method.value.lower() + "_one"
            else:
                operation_id = tokens[1] + "__" + method.value.lower() + "_all"

        fast_api.add_api_route(
            "/" + endpoint,
            endpoint_function,
            methods=[method.value],
            response_model=response_model,
            name=route.operation_id_basename,
            description=route.description,
            operation_id=operation_id,
            response_model_exclude_none=bool(route.response_model_exclude_none),
        )

    @staticmethod
    def generate_endpoints(
        fast_api: FastAPI | APIRouter,
        routes: list[CrudEndpointSet],
        handle_exception_fun: Callable,
        batch_route_suffix: str | None = None,
        query_route_suffix: str | None = None,
        ids_route_suffix: str | None = None,
        validate_query_filter: (
            Callable[[Filter], bool] | None
        ) = _default_validate_query_filter,
    ) -> None:
        # Map endpoint types to functions
        function_map = {
            CrudEndpointType.GET_ALL: CrudEndpointGenerator.generate_get_all,
            CrudEndpointType.GET_SOME: CrudEndpointGenerator.generate_get_some,
            CrudEndpointType.POST_QUERY: CrudEndpointGenerator.generate_post_query,
            CrudEndpointType.POST_QUERY_IDS: CrudEndpointGenerator.generate_post_query,
            CrudEndpointType.GET_ONE: CrudEndpointGenerator.generate_get_one,
            CrudEndpointType.POST_ONE: CrudEndpointGenerator.generate_post_one,
            CrudEndpointType.POST_SOME: CrudEndpointGenerator.generate_post_some,
            CrudEndpointType.PUT_ONE: CrudEndpointGenerator.generate_put_one,
            CrudEndpointType.PUT_SOME: CrudEndpointGenerator.generate_put_some,
            CrudEndpointType.DELETE_ALL: CrudEndpointGenerator.generate_delete_all,
            CrudEndpointType.DELETE_SOME: CrudEndpointGenerator.generate_delete_some,
            CrudEndpointType.DELETE_ONE: CrudEndpointGenerator.generate_delete_one,
        }
        # Go over each route and create the endpoints
        for route in routes:
            # Create each endpoint type in order to avoid path conflicts, e.g. if
            # /batch overlaps with /{object_id} then /batch should be created first
            for endpoint_type in CrudEndpointGenerator.CRUD_ENDPOINT_TYPE_ORDER:
                if endpoint_type not in route.endpoint_types:
                    continue
                extra_args: dict[str, Any] = {}
                if endpoint_type == CrudEndpointType.POST_QUERY:
                    extra_args["query_route_suffix"] = query_route_suffix
                    extra_args["return_id"] = False
                    extra_args["ids_route_suffix"] = ids_route_suffix
                    extra_args["validate_query_filter"] = validate_query_filter
                elif endpoint_type == CrudEndpointType.POST_QUERY_IDS:
                    extra_args["query_route_suffix"] = query_route_suffix
                    extra_args["return_id"] = True
                    extra_args["ids_route_suffix"] = ids_route_suffix
                    extra_args["validate_query_filter"] = validate_query_filter
                elif endpoint_type == CrudEndpointType.POST_SOME:
                    extra_args["batch_route_suffix"] = batch_route_suffix
                elif endpoint_type == CrudEndpointType.GET_SOME:
                    extra_args["batch_route_suffix"] = batch_route_suffix
                elif endpoint_type == CrudEndpointType.PUT_SOME:
                    extra_args["batch_route_suffix"] = batch_route_suffix
                elif endpoint_type == CrudEndpointType.DELETE_SOME:
                    extra_args["batch_route_suffix"] = batch_route_suffix
                function_map[endpoint_type](  # type: ignore
                    fast_api, route, handle_exception_fun, **extra_args
                )

    @staticmethod
    def create_crud_endpoint_set_for_domain(
        app: App,
        service_type: Hashable | set[Hashable] | None = None,
        user_dependency: Callable | None = None,
        excluded_permissions: (
            set[Permission] | dict[Type[model.Model], PermissionTypeSet | None] | None
        ) = None,
        excluded_crud_operations: (
            dict[Type[model.Model], set[CrudOperation]] | None
        ) = None,
        excluded_crud_endpoint_types: (
            dict[Type[model.Model], set[CrudEndpointType]] | None
        ) = None,
        default_description: str | None = None,
        endpoint_string_casing: StringCasing = StringCasing.SNAKE_CASE,
        query_filter_validator: (
            Callable[[Filter], bool] | None
        ) = _default_validate_query_filter,
    ) -> list[CrudEndpointSet]:
        # Parse exclusions
        if excluded_permissions is None:
            excluded_permissions = app.domain.get_model_excluded_permissions()  # type: ignore[assignment] # Unclear why raised
        parsed_excluded_permissions: set[Permission] = set()
        if isinstance(excluded_permissions, dict):
            parsed_excluded_permissions = set()
            for model_class, permission_type_set in excluded_permissions.items():
                parsed_excluded_permissions.update(
                    app.domain.get_permissions_for_model(
                        model_class, permission_type_set=permission_type_set
                    )
                )
        elif isinstance(excluded_permissions, set):
            parsed_excluded_permissions = excluded_permissions
        if excluded_crud_operations is None:
            excluded_crud_operations = {}
        if excluded_crud_endpoint_types is None:
            excluded_crud_endpoint_types = {}
        # Create CRUD endpoint sets
        if service_type is None:
            entities = app.domain.get_dag_sorted_entities()
        elif isinstance(service_type, Hashable):
            entities = app.domain.get_dag_sorted_entities(service_type=service_type)
        elif isinstance(service_type, set):
            entities = list(
                itertools.chain(
                    app.domain.get_dag_sorted_entities(service_type=x)
                    for x in service_type
                )
            )
        else:
            raise exc.DomainException(
                f"Invalid service type {service_type} for CRUD endpoint generation"
            )
        crud_endpoint_sets = []
        for entity in entities:
            if not entity.persistable:
                continue
            assert issubclass(entity.model_class, model.Model)
            crud_endpoint_sets.append(
                CrudEndpointGenerator.get_crud_endpoint_set_for_entity(
                    entity,
                    app,
                    user_dependency=user_dependency,
                    excluded_permissions=parsed_excluded_permissions,
                    excluded_crud_operations=excluded_crud_operations.get(
                        entity.model_class
                    ),
                    excluded_crud_endpoint_types=excluded_crud_endpoint_types.get(
                        entity.model_class
                    ),
                    default_description=default_description,
                    endpoint_string_casing=endpoint_string_casing,
                    query_filter_validator=query_filter_validator,
                )
            )
        return crud_endpoint_sets

    @staticmethod
    def get_crud_endpoint_set_for_entity(
        entity: Entity,
        app: App,
        user_dependency: Callable | None = None,
        add_query_route: bool = True,
        excluded_permissions: set[Permission] | None = None,
        excluded_crud_operations: set[CrudOperation] | None = None,
        excluded_crud_endpoint_types: set[CrudEndpointType] | None = None,
        default_description: str | None = None,
        endpoint_string_casing: StringCasing = StringCasing.SNAKE_CASE,
        endpoint_string_is_plural: bool = True,
        query_filter_validator: (
            Callable[[Filter], bool] | None
        ) = _default_validate_query_filter,
    ) -> CrudEndpointSet:
        # Initialize some
        model_class = entity.model_class
        assert issubclass(model_class, model.Model)
        if excluded_crud_endpoint_types is None:
            excluded_crud_endpoint_types = set()
        if excluded_crud_operations is None:
            excluded_crud_operations = set()
        if excluded_permissions is None:
            excluded_permissions = set()
        # Get endpoint types to create, starting from all permissions for the model and removing any excluded ones
        crud_command_class = entity.crud_command_class
        if crud_command_class is None:
            raise exc.DomainException(
                f"Entity {entity.name} does not have a crud command class"
            )
        assert issubclass(crud_command_class, model.CrudCommand)
        permissions = (
            app.domain.get_permissions_for_model(model_class) - excluded_permissions
        )
        crud_operations = (
            CrudEndpointGenerator.get_crud_operations_for_permissions(permissions)
            - excluded_crud_operations
        )
        crud_endpoint_types = (
            CrudEndpointGenerator.get_crud_endpoint_types_for_operations(
                crud_operations, add_query_route=add_query_route
            )
        ) - excluded_crud_endpoint_types
        # Create CRUD endpoint set
        endpoint_basename = CrudEndpointGenerator.get_endpoint_basename(
            entity, endpoint_string_casing, endpoint_string_is_plural
        )
        crud_endpoint_set = CrudEndpointSet(
            model_class=model_class,
            create_api_model_class=entity.create_api_model_class,
            read_api_model_class=entity.read_api_model_class,
            endpoint_basename=endpoint_basename,
            crud_command_class=crud_command_class,
            endpoint_types=crud_endpoint_types,
            operation_id_basename=entity.name,
            description=model_class.__doc__ or default_description,
            # description=model_class.model_json_schema().get(
            #     "description", default_description
            # ),
            user_dependency=user_dependency,
            app=app,
            id_class=UUID,
            response_model_exclude_none=True,
            query_filter_validator=query_filter_validator,
        )
        return crud_endpoint_set

    @staticmethod
    def get_crud_operations_for_permissions(
        permissions: set[Permission],
    ) -> set[CrudOperation]:
        crud_operations = set()
        for permission in permissions:
            permission_type = permission.permission_type
            if permission_type == PermissionType.CREATE:
                crud_operations.update(
                    {CrudOperation.CREATE_ONE, CrudOperation.CREATE_SOME}
                )
            elif permission_type == PermissionType.READ:
                crud_operations.update(
                    {
                        CrudOperation.READ_ALL,
                        CrudOperation.READ_SOME,
                        CrudOperation.READ_ONE,
                    }
                )
            elif permission_type == PermissionType.UPDATE:
                crud_operations.update(
                    {CrudOperation.UPDATE_ONE, CrudOperation.UPDATE_SOME}
                )
            elif permission_type == PermissionType.DELETE:
                crud_operations.update(
                    {
                        CrudOperation.DELETE_ALL,
                        CrudOperation.DELETE_SOME,
                        CrudOperation.DELETE_ONE,
                    }
                )
            else:
                raise NotImplementedError(
                    f"Permission type {permission_type} not implemented"
                )
        return crud_operations

    @staticmethod
    def get_endpoint_basename(
        entity: Entity,
        string_casing: StringCasing = StringCasing.SNAKE_CASE,
        is_plural: bool = True,
    ) -> str:
        name = entity.get_name_by_casing(string_casing, is_plural=is_plural)
        if name is None:
            raise exc.DomainException(
                f"Entity {entity.name} does not have a {string_casing.value} name"
            )
        return name

    @staticmethod
    def get_crud_endpoint_types_for_operations(
        crud_operations: set[CrudOperation], add_query_route: bool = True
    ) -> set[CrudEndpointType]:
        crud_endpoint_types = set()
        for crud_operation in crud_operations:
            crud_endpoint_types.add(
                CrudEndpointGenerator.CRUD_OPERATION_TO_ENDPOINT_TYPE[crud_operation]
            )
            if crud_operation == CrudOperation.READ_ALL and add_query_route:
                crud_endpoint_types.update(
                    {
                        CrudEndpointType.POST_QUERY,
                        CrudEndpointType.POST_QUERY_IDS,
                    }
                )
        return crud_endpoint_types
