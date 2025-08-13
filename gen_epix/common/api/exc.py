import logging
import uuid
from functools import partial
from typing import Any, Callable, Hashable, NoReturn

from gen_epix.fastapp import App, LogLevel, exc, model
from gen_epix.fastapp.api import exc as api_exc
from gen_epix.fastapp.exc import (
    AuthException,
    DomainException,
    DuplicateIdsError,
    IdsError,
    ServiceException,
)

http_exception_fmap = {
    400: api_exc.BadRequest400HTTPException,
    401: api_exc.UnauthorizedUser401HTTPException,
    403: api_exc.Forbidden403HTTPException,
    404: api_exc.ResourceNotFound404HTTPException,
    405: api_exc.MethodNotAllowed405HTTPException,
    409: api_exc.ResourceAlreadyExists409HTTPException,
    422: api_exc.UnprocessableEntity422HTTPException,
    500: api_exc.InternalServerError500HTTPException,
    503: api_exc.ServiceUnavailableError503HTTPException,
}


def get_logger_fmap(logger: logging.Logger) -> dict[LogLevel, Callable]:
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


# TODO: Consider refactoring this into a callable ExceptionHandler class
def generate_handle_exception_function(
    app: App,
    logger: logging.Logger | None,
) -> Callable[
    [str, model.User | None, Exception, Hashable | list[Hashable] | None],
    NoReturn,
]:

    def handle_exception(
        app: App,
        logger: logging.Logger | None,
        log_message_id: str,
        user: model.User | None,
        exception: Exception,
        request_ids: Hashable | list[Hashable] | None = None,
        level: LogLevel = LogLevel.ERROR,
    ) -> NoReturn:
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
        if isinstance(exception, DomainException):
            if isinstance(exception, IdsError):
                invalid_ids = []
                if request_ids and exception.ids:
                    # Compare ids received in request with those reported
                    # as invalid in the DomainError
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
                if invalid_ids:
                    # (Part of the) issue is with id(s). Provide detail on that.
                    if isinstance(exception, DuplicateIdsError):
                        invalid_ids_str = ", ".join(
                            [f'"{x}"' for x in set(invalid_ids)]
                        )
                        detail = f"Duplicate ids(s) provided: {invalid_ids_str}"
                    else:
                        invalid_ids_str = ", ".join([f'"{x}"' for x in invalid_ids])
                        detail = f"Invalid ids(s) provided: {invalid_ids_str}"
                    if logger:
                        logger.info(log_message)
                    raise http_exception_fmap[422](detail=detail) from exception
                # IdsError, but other issue than provided invalid ids.
                # No further details provided.
                if logger:
                    logger.info(log_message)
                raise http_exception_fmap[422]() from exception
            elif isinstance(exception, AuthException):
                if logger:
                    logger.info(log_message)
                raise http_exception_fmap[exception.get_http_status_code()](
                    detail="Access denied", **exception.get_http_other_props()
                ) from exception
            elif isinstance(exception, ServiceException):
                if logger:
                    logger.error(log_message)
                raise http_exception_fmap[exception.get_http_status_code()](
                    detail="System unavailable", **exception.get_http_other_props()
                ) from exception
            else:
                # Other domain issue.
                if logger:
                    logger.warning(log_message)
                raise http_exception_fmap[422](detail=str(exception)) from exception
        else:
            # Any other error than a DomainError
            if logger:
                logger.error(log_message)
            raise http_exception_fmap[500]() from exception

    return partial(handle_exception, app, logger)
