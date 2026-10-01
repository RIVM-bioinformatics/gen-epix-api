"""Translate commondb domain exceptions into logged FastAPI HTTP responses."""

import logging
import uuid
from collections.abc import Callable, Hashable
from functools import partial
from typing import Any, NoReturn

from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool

from gen_epix.casedb.domain import command
from gen_epix.commondb.domain import model
from gen_epix.fastapp import App, LogLevel, exc
from gen_epix.fastapp.api import exc as api_exc

http_exception_fmap: dict[int, Callable[..., HTTPException]] = {
    400: api_exc.BadRequest400HTTPException,
    401: api_exc.UnauthorizedUser401HTTPException,
    403: api_exc.Forbidden403HTTPException,
    404: api_exc.ResourceNotFound404HTTPException,
    405: api_exc.MethodNotAllowed405HTTPException,
    409: api_exc.ResourceConflict409HTTPException,
    422: api_exc.UnprocessableEntity422HTTPException,
    500: api_exc.InternalServerError500HTTPException,
    503: api_exc.ServiceUnavailableError503HTTPException,
}


def get_logger_fmap(logger: logging.Logger) -> dict[LogLevel, Callable[..., None]]:
    """Create a mapping from application log levels to logger callables.

    Args:
        logger: Logger that receives mapped log messages.

    Returns:
        Mapping of each LogLevel to its corresponding logger method.
    """
    logger_fmap = {
        LogLevel.TRACE: logger.debug,
        LogLevel.DEBUG: logger.debug,
        LogLevel.INFO: logger.info,
        LogLevel.WARN: logger.warning,
        LogLevel.ERROR: logger.error,
        LogLevel.FATAL: logger.critical,
    }
    return logger_fmap


# For debugging purposes
LAST_HANDLED_EXCEPTION: dict[str, Any] = {
    "id": uuid.uuid4(),
}


def handle_exception(
    app: App,
    logger: logging.Logger | None,
    log_message_id: str,
    user: model.User | None,
    exception: Exception,
    request_ids: Hashable | list[Hashable] | None = None,
    level: LogLevel = LogLevel.ERROR,
) -> NoReturn:
    """Log an exception and raise the corresponding HTTP exception.

    Args:
        app: Application used to create the structured log message.
        logger: Optional logger that receives the error message.
        log_message_id: Correlation ID for the logged exception.
        user: User associated with the failed request, if known.
        exception: Exception to translate to an HTTP response.
        request_ids: Requested IDs used to report invalid-ID details.
        level: Severity recorded in the last-handled-exception diagnostic state.

    Raises:
        HTTPException: Mapped client or service error for a domain exception, or an
            internal-server error for an unexpected exception.
    """
    LAST_HANDLED_EXCEPTION.update(
        {
            "id": uuid.uuid4(),
            "log_message_id": log_message_id,
            "user": user,
            "exception": exception,
            "request_ids": request_ids,
            "level": level,
        }
    )
    # Log without stack trace since this is expected to be logged separately
    log_message = app.create_log_message(
        log_message_id, None, user_id=user.id if user else None, exception=exception
    )
    # Raise HTTP exception
    if isinstance(exception, exc.DomainException):
        if isinstance(exception, exc.IdsError):
            _handle_invalid_ids_exception(logger, exception, request_ids, log_message)
        if isinstance(exception, exc.AuthException):
            _handle_auth_exception(logger, exception, log_message)
        if isinstance(exception, exc.ServiceException):
            _handle_service_exception(logger, exception, log_message)
        else:
            # Other DomainError
            if logger:
                logger.warning(log_message)
            raise http_exception_fmap[422](detail=str(exception)) from exception
    else:
        # Any other error than a DomainError
        if logger:
            logger.error(log_message)
        raise http_exception_fmap[500]() from exception


def _handle_service_exception(
    logger: logging.Logger | None,
    exception: exc.ServiceException,
    log_message: str,
) -> NoReturn:
    """Log a service exception and raise its mapped service-unavailable response.

    Args:
        logger: Optional logger that receives the error message.
        exception: Service exception that supplies HTTP response properties.
        log_message: Structured message describing the exception.

    Raises:
        HTTPException: Response with the service exception's HTTP status and metadata.
    """
    if logger:
        logger.error(log_message)
    raise http_exception_fmap[exception.get_http_status_code()](
        detail="System unavailable", **exception.get_http_other_props()
    ) from exception


def _handle_auth_exception(
    logger: logging.Logger | None,
    exception: exc.AuthException,
    log_message: str,
) -> NoReturn:
    """Log an authentication exception and raise its mapped access-denied response.

    Args:
        logger: Optional logger that receives the access-denied message.
        exception: Authentication exception that supplies HTTP response properties.
        log_message: Structured message describing the exception.

    Raises:
        HTTPException: Response with the authentication exception's HTTP status and
            metadata.
    """
    if logger:
        logger.info(log_message)
    raise http_exception_fmap[exception.get_http_status_code()](
        detail="Access denied", **exception.get_http_other_props()
    ) from exception


def _handle_invalid_ids_exception(
    logger: logging.Logger | None,
    exception: exc.IdsError,
    request_ids: Hashable | list[Hashable] | None,
    log_message: str,
) -> NoReturn:
    """Translate an ID exception into a validation or conflict HTTP response.

    Args:
        logger: Optional logger that receives the invalid-ID message.
        exception: Domain exception containing invalid or duplicate IDs.
        request_ids: IDs supplied by the request, if available.
        log_message: Structured message describing the exception.

    Raises:
        HTTPException: Conflict for duplicate or link-constraint IDs, otherwise an
            unprocessable-entity response.
    """
    http_status_code = 422
    if isinstance(exception, (exc.LinkConstraintViolationError, exc.DuplicateIdsError)):
        http_status_code = 409
    invalid_ids = []
    if request_ids and exception.ids:
        # Compare ids received in request with those reported
        # as invalid in the DomainError
        invalid_ids = __extract_invalid_ids(exception, request_ids)
    if invalid_ids:
        log_and_raise_invalid_ids_exception(
            logger, exception, log_message, http_status_code, invalid_ids
        )
    if logger:
        logger.info(log_message)
    raise http_exception_fmap[http_status_code]() from exception


def log_and_raise_invalid_ids_exception(
    logger: logging.Logger | None,
    exception: exc.IdsError,
    log_message: str,
    http_status_code: int,
    invalid_ids: list[Hashable],
) -> NoReturn:
    """Log invalid IDs and raise an HTTP response with their public details.

    Args:
        logger: Optional logger that receives the invalid-ID message.
        exception: ID exception that determines duplicate versus invalid wording.
        log_message: Structured message describing the exception.
        http_status_code: Status code for the HTTP response.
        invalid_ids: IDs to expose in the response detail.

    Raises:
        HTTPException: Response with the provided status and invalid-ID detail.
    """
    if isinstance(exception, exc.DuplicateIdsError):
        invalid_ids_str = ", ".join([f'"{x}"' for x in set(invalid_ids)])
        detail = f"Duplicate ids(s) provided: {invalid_ids_str}"
    else:
        invalid_ids_str = ", ".join([f'"{x}"' for x in invalid_ids])
        detail = f"Invalid ids(s) provided: {invalid_ids_str}"
    if logger:
        logger.info(log_message)
    raise http_exception_fmap[http_status_code](detail=detail) from exception


async def handle_command(
    app: App,
    user: model.User,
    exception_code: str,
    input_command: command.Command,
    input_handle_exception: (
        Callable[
            [str, model.User | None, Exception, Hashable | list[Hashable] | None],
            NoReturn,
        ]
        | None
    ),
) -> Any:
    """Dispatch a command and translate any exception through an API error handler.

    Args:
        app: Application that dispatches the command.
        user: User associated with the command.
        exception_code: Correlation ID used if command dispatch fails.
        input_command: Command passed to the application dispatcher.
        input_handle_exception: Optional exception adapter; defaults to this module's
            handler.

    Returns:
        Result returned by the command handler.

    Raises:
        Exception: Re-raises the original exception after invoking the configured
            exception handler.
    """
    try:
        return await run_in_threadpool(app.handle, input_command)
    except Exception as exception:
        if input_handle_exception is None:
            input_handle_exception = generate_handle_exception_function(
                app, logger=None
            )
        input_handle_exception(exception_code, user, exception, None)
        raise


def __extract_invalid_ids(
    exception: exc.IdsError,
    request_ids: Hashable | list[Hashable],
) -> list[Hashable]:
    """Return request IDs that are also reported by an ID exception.

    Args:
        exception: ID exception containing invalid IDs.
        request_ids: One or more request IDs, optionally nested in a list.

    Returns:
        Requested IDs also listed as invalid by the exception.
    """
    raw_request_ids = request_ids
    if not isinstance(raw_request_ids, list):
        raw_request_ids = [raw_request_ids]
    request_ids = []
    for id_ in raw_request_ids:
        if not id_:
            continue
        if isinstance(id_, list):
            request_ids += [x for x in id_ if x]
        else:
            request_ids.append(id_)
    invalid_ids = [x for x in request_ids if x in exception.ids]
    return invalid_ids


# TODO: Consider refactoring this into a callable ExceptionHandler class
def generate_handle_exception_function(
    app: App,
    logger: logging.Logger | None,
) -> Callable[
    [str, model.User | None, Exception, Hashable | list[Hashable] | None],
    NoReturn,
]:
    """Bind application and logger dependencies into an exception handler.

    Args:
        app: Application used to create structured error messages.
        logger: Optional logger that receives translated exceptions.

    Returns:
        Callable that translates a request exception to an HTTP response.
    """
    return partial(handle_exception, app, logger)
