from functools import partial
from typing import Any, Callable

from fastapi.openapi.utils import get_openapi

from gen_epix.fastapp.services.auth import AuthService

_GET_OPEN_API_DEFAULTS: dict[str, Any] = {
    "title": "API",
    "description": "API description",
    "version": "0.0.0",
    "separate_input_output_schemas": False,
}


def create_custom_openapi_function(
    get_open_api_kwargs: dict[str, Any] = {},
    fix_schema: bool = True,
    auth_service: AuthService | None = None,
) -> Callable[[], dict[str, Any]]:

    def custom_openapi_function(
        default_kwargs: dict[str, Any],
        get_open_api_kwargs: dict[str, Any],
        fix_schema: bool,
        auth_service: AuthService | None,
    ) -> dict[str, Any]:
        # Set defaults
        for key, value in _GET_OPEN_API_DEFAULTS.items():
            get_open_api_kwargs[key] = get_open_api_kwargs.get(key, value)

        # Get the initial OpenAPI schema
        openapi_schema = get_openapi(**get_open_api_kwargs)

        # Fix any issues with the schema if necessary
        # TODO: add a fix for read-only fields
        if fix_schema:
            fix_schema_nullable_and_single_element(openapi_schema)

        # Add x-tokenName to security schemes based on AuthService
        if auth_service:
            for idp_client in auth_service.idp_clients:
                openapi_schema["components"]["securitySchemes"][
                    f"{idp_client.scheme_name}"
                ]["x-tokenName"] = idp_client.token_name

        return openapi_schema

    return partial(
        custom_openapi_function,
        _GET_OPEN_API_DEFAULTS,
        get_open_api_kwargs,
        fix_schema,
        auth_service,
    )


def fix_schema_nullable_and_single_element(schema: dict) -> None:
    """
    Fixes the schema by handling 'anyOf' constructs and setting the 'nullable' property.
    This function performs the following operations on the given schema:
    1. Replaces 'anyOf' constructs containing {"type": "null"} with 'nullable': True.
    2. Simplifies 'anyOf', 'allOf', and 'oneOf' constructs containing a single item by replacing them with that item.
    3. Recursively processes nested dictionaries and lists to apply the above transformations.
    Args:
        schema (dict): The JSON schema to be fixed.
    Returns:
        None: The function modifies the input schema in place.


    """
    # No other fix found online as of 2023-11-15.
    keys = list(schema.keys())
    for key in keys:
        if key in {"anyOf"}:
            # Search for presence of type: null in list
            for i, value in enumerate(schema[key]):
                has_null = value == {"type": "null"}
                if has_null:
                    break
            if not has_null:
                continue
            # Remove type: null from list
            del schema[key][i]  # pylint: disable=undefined-loop-variable

            # In case only 1 remaining item in list,
            # move it one level higher and remove anyOf key
            if len(schema[key]) == 1:
                key2 = list(schema[key][0].keys())[0]
                schema[key2] = schema[key][0][key2]
                del schema[key]
            # Set nullable property
            schema["nullable"] = True
        elif isinstance(schema[key], dict):
            # Continue recursively
            fix_schema_nullable_and_single_element(schema[key])
        elif isinstance(schema[key], list):
            # Continue recursively
            for item in schema[key]:
                if isinstance(item, dict):
                    fix_schema_nullable_and_single_element(item)
        if (
            key in schema
            and key in {"anyOf", "oneOf", "allOf"}
            and len(schema[key]) == 1
        ):
            # In case only 1 remaining item in list,
            # move it one level higher and remove list
            value = schema[key][0]
            del schema[key]
            for key2 in value:
                schema[key2] = value[key2]


# TODO: add a function to fix read-only fields
